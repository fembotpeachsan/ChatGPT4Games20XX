#!/usr/bin/env python3
"""
A complete Chip-8 Emulator in Python with a tkinter GUI, no command-line arguments needed.

Features:
 - Open a Chip-8 ROM from a file dialog
 - Start / Stop emulation
 - Basic Chip-8 instructions
 - Keyboard mapping for hex keys
 - Monochrome display (64×32) scaled up
 - Timers at ~60Hz
"""

import tkinter as tk
import tkinter.filedialog
import time
import random

class Chip8App:
    def __init__(self, master, scale=10):
        """
        Initialize the Chip-8 emulator within a tkinter application window.

        Parameters
        ----------
        master : tk.Tk
            The main tkinter root.
        scale : int
            Pixel scaling factor for the 64x32 Chip-8 display.
        """
        self.master = master
        self.master.title("Chip-8 Emulator (Tkinter)")

        # Chip-8 Specs
        self.MEMORY_SIZE = 4096
        self.SCREEN_WIDTH = 64
        self.SCREEN_HEIGHT = 32
        self.PROGRAM_START = 0x200
        self.scale = scale

        # Create memory, registers, stack
        self.memory = [0] * self.MEMORY_SIZE
        self.V = [0] * 16  # V0..VF
        self.I = 0
        self.pc = self.PROGRAM_START
        self.stack = []
        self.sp = 0

        # Timers
        self.delay_timer = 0
        self.sound_timer = 0
        self.timer_frequency = 60  # 60Hz

        # Graphics buffer (64x32)
        self.gfx = [[0] * self.SCREEN_WIDTH for _ in range(self.SCREEN_HEIGHT)]

        # Key states for 16 Chip-8 keys (0-F)
        self.keys = [0] * 16

        # Load fontset at 0x50
        self.load_fontset()

        # Emulator run/pause state
        self.running = False
        self.paused = False

        # CPU frequency (cycles per second)
        self.cycle_rate = 500
        self.cycle_delay = 1.0 / self.cycle_rate

        # Set up tkinter UI
        self.create_widgets()

        # Set up key bindings
        self.keymap = {
            '1': 0x1, '2': 0x2, '3': 0x3, '4': 0xC,
            'q': 0x4, 'w': 0x5, 'e': 0x6, 'r': 0xD,
            'a': 0x7, 's': 0x8, 'd': 0x9, 'f': 0xE,
            'z': 0xA, 'x': 0x0, 'c': 0xB, 'v': 0xF
        }
        master.bind("<KeyPress>", self.on_key_down)
        master.bind("<KeyRelease>", self.on_key_up)

    # ----------------------------
    # UI
    # ----------------------------
    def create_widgets(self):
        # Create a menu
        menubar = tk.Menu(self.master)
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Open ROM", command=self.open_rom)
        file_menu.add_command(label="Exit", command=self.master.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.master.config(menu=menubar)

        # Frame for control buttons
        control_frame = tk.Frame(self.master)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        self.start_button = tk.Button(control_frame, text="Start", command=self.start_emulation)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.pause_button = tk.Button(control_frame, text="Pause/Resume", command=self.toggle_pause)
        self.pause_button.pack(side=tk.LEFT, padx=5)

        # Canvas for the 64x32 screen
        self.canvas = tk.Canvas(
            self.master,
            width=self.SCREEN_WIDTH * self.scale,
            height=self.SCREEN_HEIGHT * self.scale,
            bg="black"
        )
        self.canvas.pack(side=tk.BOTTOM)

    def open_rom(self):
        """Open a file dialog to select a Chip-8 ROM, load it into memory."""
        filepath = tk.filedialog.askopenfilename(
            title="Open Chip-8 ROM",
            filetypes=[("Chip-8 ROMs", "*.ch8 *.c8 *.bin"), ("All Files", "*.*")]
        )
        if filepath:
            self.load_rom(filepath)

    def load_rom(self, rom_path):
        """Load a Chip-8 ROM from disk into emulator memory at 0x200."""
        with open(rom_path, "rb") as f:
            data = f.read()

        # Clear memory & reload font
        self.memory = [0] * self.MEMORY_SIZE
        self.load_fontset()

        # Write ROM to memory
        for i, b in enumerate(data):
            self.memory[self.PROGRAM_START + i] = b

        # Reset CPU state
        self.V = [0] * 16
        self.I = 0
        self.pc = self.PROGRAM_START
        self.stack = []
        self.sp = 0
        self.delay_timer = 0
        self.sound_timer = 0
        self.gfx = [[0] * self.SCREEN_WIDTH for _ in range(self.SCREEN_HEIGHT)]
        print(f"Loaded ROM: {rom_path}")

    def start_emulation(self):
        """Start running the emulator loop."""
        if self.running:
            print("Already running.")
            return
        self.running = True
        self.paused = False
        self.emulation_loop()

    def toggle_pause(self):
        """Pause or resume the emulation."""
        self.paused = not self.paused

    # ----------------------------
    # Fontset
    # ----------------------------
    def load_fontset(self):
        """Load the standard Chip-8 4x5 font into memory at 0x50."""
        fontset = [
            0xF0,0x90,0x90,0x90,0xF0, # 0
            0x20,0x60,0x20,0x20,0x70, # 1
            0xF0,0x10,0xF0,0x80,0xF0, # 2
            0xF0,0x10,0xF0,0x10,0xF0, # 3
            0x90,0x90,0xF0,0x10,0x10, # 4
            0xF0,0x80,0xF0,0x10,0xF0, # 5
            0xF0,0x80,0xF0,0x90,0xF0, # 6
            0xF0,0x10,0x20,0x40,0x40, # 7
            0xF0,0x90,0xF0,0x90,0xF0, # 8
            0xF0,0x90,0xF0,0x10,0xF0, # 9
            0xF0,0x90,0xF0,0x90,0x90, # A
            0xE0,0x90,0xE0,0x90,0xE0, # B
            0xF0,0x80,0x80,0x80,0xF0, # C
            0xE0,0x90,0xE0,0x90,0xE0, # D
            0xF0,0x80,0xF0,0x80,0xF0, # E
            0xF0,0x80,0xF0,0x80,0x80  # F
        ]
        start = 0x50
        for i, b in enumerate(fontset):
            self.memory[start + i] = b

    # ----------------------------
    # Main Emulation Loop
    # ----------------------------
    def emulation_loop(self):
        """Schedules the next CPU cycle (or IDLE if paused) using tkinter's after()."""
        if not self.running:
            return

        if not self.paused:
            self.emulate_cycle()
            self.draw_screen()

        # Schedule next iteration
        self.master.after(int(self.cycle_delay * 1000), self.emulation_loop)

    # ----------------------------
    # Fetch/Decode/Execute
    # ----------------------------
    def emulate_cycle(self):
        """One CPU cycle: fetch opcode, decode, execute, update timers."""
        opcode = (self.memory[self.pc] << 8) | self.memory[self.pc+1]
        self.pc += 2

        # Extract parts
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        n = opcode & 0x000F
        nn = opcode & 0x00FF
        nnn = opcode & 0x0FFF

        if opcode == 0x00E0:
            # CLS
            self.gfx = [[0]*self.SCREEN_WIDTH for _ in range(self.SCREEN_HEIGHT)]
        elif opcode == 0x00EE:
            # RET
            self.pc = self.stack.pop()
        elif (opcode & 0xF000) == 0x1000:
            # JP nnn
            self.pc = nnn
        elif (opcode & 0xF000) == 0x2000:
            # CALL nnn
            self.stack.append(self.pc)
            self.pc = nnn
        elif (opcode & 0xF000) == 0x3000:
            # SE Vx, nn
            if self.V[x] == nn:
                self.pc += 2
        elif (opcode & 0xF000) == 0x4000:
            # SNE Vx, nn
            if self.V[x] != nn:
                self.pc += 2
        elif (opcode & 0xF000) == 0x5000 and n == 0:
            # SE Vx, Vy
            if self.V[x] == self.V[y]:
                self.pc += 2
        elif (opcode & 0xF000) == 0x6000:
            # LD Vx, nn
            self.V[x] = nn
        elif (opcode & 0xF000) == 0x7000:
            # ADD Vx, nn
            self.V[x] = (self.V[x] + nn) & 0xFF
        elif (opcode & 0xF000) == 0x8000:
            # Logical / Math ops
            if n == 0x0:
                # LD Vx, Vy
                self.V[x] = self.V[y]
            elif n == 0x1:
                # OR Vx, Vy
                self.V[x] |= self.V[y]
            elif n == 0x2:
                # AND Vx, Vy
                self.V[x] &= self.V[y]
            elif n == 0x3:
                # XOR Vx, Vy
                self.V[x] ^= self.V[y]
            elif n == 0x4:
                # ADD Vx, Vy
                s = self.V[x] + self.V[y]
                self.V[0xF] = 1 if s > 0xFF else 0
                self.V[x] = s & 0xFF
            elif n == 0x5:
                # SUB Vx, Vy
                self.V[0xF] = 1 if self.V[x] >= self.V[y] else 0
                self.V[x] = (self.V[x] - self.V[y]) & 0xFF
            elif n == 0x6:
                # SHR Vx
                self.V[0xF] = self.V[x] & 1
                self.V[x] >>= 1
            elif n == 0x7:
                # SUBN Vx, Vy
                self.V[0xF] = 1 if self.V[y] >= self.V[x] else 0
                self.V[x] = (self.V[y] - self.V[x]) & 0xFF
            elif n == 0xE:
                # SHL Vx
                self.V[0xF] = (self.V[x] & 0x80) >> 7
                self.V[x] = (self.V[x] << 1) & 0xFF
        elif (opcode & 0xF000) == 0x9000 and n == 0:
            # SNE Vx, Vy
            if self.V[x] != self.V[y]:
                self.pc += 2
        elif (opcode & 0xF000) == 0xA000:
            # LD I, nnn
            self.I = nnn
        elif (opcode & 0xF000) == 0xB000:
            # JP V0, nnn
            self.pc = nnn + self.V[0]
        elif (opcode & 0xF000) == 0xC000:
            # RND Vx, nn
            self.V[x] = random.randint(0, 255) & nn
        elif (opcode & 0xF000) == 0xD000:
            # DRW Vx, Vy, n
            vx = self.V[x] & 0xFF
            vy = self.V[y] & 0xFF
            self.V[0xF] = 0
            for row in range(n):
                sprite_byte = self.memory[self.I + row]
                for col in range(8):
                    if (sprite_byte & (0x80 >> col)) != 0:
                        px = (vx + col) % self.SCREEN_WIDTH
                        py = (vy + row) % self.SCREEN_HEIGHT
                        if self.gfx[py][px] == 1:
                            self.V[0xF] = 1
                        self.gfx[py][px] ^= 1
        elif (opcode & 0xF0FF) == 0xE09E:
            # SKP Vx
            if self.keys[self.V[x]] == 1:
                self.pc += 2
        elif (opcode & 0xF0FF) == 0xE0A1:
            # SKNP Vx
            if self.keys[self.V[x]] == 0:
                self.pc += 2
        elif (opcode & 0xF0FF) == 0xF007:
            # LD Vx, DT
            self.V[x] = self.delay_timer
        elif (opcode & 0xF0FF) == 0xF00A:
            # LD Vx, K
            pressed_key = None
            for idx, val in enumerate(self.keys):
                if val == 1:
                    pressed_key = idx
                    break
            if pressed_key is not None:
                self.V[x] = pressed_key
            else:
                # No key pressed => repeat this instr
                self.pc -= 2
        elif (opcode & 0xF0FF) == 0xF015:
            # LD DT, Vx
            self.delay_timer = self.V[x]
        elif (opcode & 0xF0FF) == 0xF018:
            # LD ST, Vx
            self.sound_timer = self.V[x]
        elif (opcode & 0xF0FF) == 0xF01E:
            # ADD I, Vx
            self.I += self.V[x]
            self.I &= 0xFFF
        elif (opcode & 0xF0FF) == 0xF029:
            # LD F, Vx
            digit = self.V[x] & 0xF
            self.I = 0x50 + digit * 5
        elif (opcode & 0xF0FF) == 0xF033:
            # LD B, Vx
            val = self.V[x]
            self.memory[self.I]   = val // 100
            self.memory[self.I+1] = (val // 10) % 10
            self.memory[self.I+2] = val % 10
        elif (opcode & 0xF0FF) == 0xF055:
            # LD [I], V0..Vx
            for idx in range(x + 1):
                self.memory[self.I + idx] = self.V[idx]
        elif (opcode & 0xF0FF) == 0xF065:
            # LD V0..Vx, [I]
            for idx in range(x + 1):
                self.V[idx] = self.memory[self.I + idx]
        else:
            print(f"Unknown opcode: {opcode:04X}")

        # Update timers
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1
            if self.sound_timer == 0:
                print("BEEP!")

    # ----------------------------
    # Drawing
    # ----------------------------
    def draw_screen(self):
        """Draw the 64x32 gfx buffer onto the tkinter canvas."""
        self.canvas.delete("all")
        for y in range(self.SCREEN_HEIGHT):
            for x in range(self.SCREEN_WIDTH):
                if self.gfx[y][x] == 1:
                    self.canvas.create_rectangle(
                        x*self.scale, y*self.scale,
                        (x+1)*self.scale, (y+1)*self.scale,
                        fill="white", outline="white"
                    )

    # ----------------------------
    # Keyboard
    # ----------------------------
    def on_key_down(self, event):
        """Set the corresponding Chip-8 key state to 1 if mapped."""
        k = event.keysym.lower()
        if k in self.keymap:
            key_id = self.keymap[k]
            self.keys[key_id] = 1

    def on_key_up(self, event):
        """Set the corresponding Chip-8 key state to 0 if mapped."""
        k = event.keysym.lower()
        if k in self.keymap:
            key_id = self.keymap[k]
            self.keys[key_id] = 0

def main():
    root = tk.Tk()
    app = Chip8App(root, scale=10)
    root.mainloop()

if __name__ == "__main__":
    main()
