import sys
import tkinter as tk
from tkinter import filedialog, Menu, Label
import random
import pickle
import os
import time
import threading

# CHIP-8 Emulator - Inspired by mGBA look/style using Tkinter
# Modified to use a file dialog for ROM selection and have a more standard keyboard layout

class Chip8:
    def __init__(self, rom_path=None):
        # Core registers and memory
        self.memory = [0] * 4096
        self.V = [0] * 16
        self.I = 0
        self.pc = 0x200
        self.stack = []
        self.delay_timer = 0
        self.sound_timer = 0
        self.paused = False
        self.step_mode = False
        self.frame_skip = 2  # Adjust for performance
        self.skip_count = 0
        self.rom_path = rom_path
        self.rom_name = "No ROM Loaded"

        # Display
        self.width = 64
        self.height = 32
        self.display = [[0]*self.width for _ in range(self.height)]

        # Window size
        self.window_width = 640
        self.window_height = 320
        self.pixel_width = self.window_width / self.width
        self.pixel_height = self.window_height / self.height

        # Keypad - SNES-style layout attempt
        # CHIP-8:   1 2 3 C     Keyboard:
        #           4 5 6 D       Q W E R
        #           7 8 9 E       A S D F
        #           A 0 B F       Z X C V
        self.keys = [0]*16
        self.keymap = {
            # Row 1: 1 2 3 C
            '1': 0x1, '2': 0x2, '3': 0x3, '4': 0xC,
            # Row 2: 4 5 6 D
            'q': 0x4, 'w': 0x5, 'e': 0x6, 'r': 0xD,
            # Row 3: 7 8 9 E
            'a': 0x7, 's': 0x8, 'd': 0x9, 'f': 0xE,
            # Row 4: A 0 B F
            'z': 0xA, 'x': 0x0, 'c': 0xB, 'v': 0xF
        }
        # Create reverse map for status display
        self.reverse_keymap = {v: k.upper() for k, v in self.keymap.items()}

        # Fontset
        fontset = [
            0xF0,0x90,0x90,0x90,0xF0,
            0x20,0x60,0x20,0x20,0x70,
            0xF0,0x10,0xF0,0x80,0xF0,
            0xF0,0x10,0xF0,0x10,0xF0,
            0x90,0x90,0xF0,0x10,0x10,
            0xF0,0x80,0xF0,0x10,0xF0,
            0xF0,0x80,0xF0,0x90,0xF0,
            0xF0,0x10,0x20,0x40,0x40,
            0xF0,0x90,0xF0,0x90,0xF0,
            0xF0,0x90,0xF0,0x10,0xF0,
            0xF0,0x90,0xF0,0x90,0x90,
            0xE0,0x90,0xE0,0x90,0xE0,
            0xF0,0x80,0x80,0x80,0xF0,
            0xE0,0x90,0x90,0x90,0xE0,
            0xF0,0x80,0xF0,0x80,0xF0,
            0xF0,0x80,0xF0,0x80,0x80
        ]
        for i, b in enumerate(fontset):
            self.memory[i] = b
        if self.rom_path:
            self.load_rom(self.rom_path)

    def load_rom(self, path):
        try:
            with open(path, 'rb') as f:
                rom = f.read()
            for i, b in enumerate(rom):
                self.memory[0x200 + i] = b
            self.rom_path = path # Store path for save states
            self.rom_name = os.path.basename(path)
            if hasattr(self, 'status_label'):
                 self.status_label.config(text=f"ROM: {self.rom_name}")
        except FileNotFoundError:
            print(f"ROM file not found: {path}")
            # If initial load fails, we'll prompt via dialog later
            if not hasattr(self, 'root'): # Only prompt if GUI is up
                 self.prompt_for_rom()

    def prompt_for_rom(self):
        """Open a file dialog to select a ROM."""
        if not hasattr(self, 'root') or not self.root:
             # Create a temporary root for the dialog if main GUI isn't ready
             temp_root = tk.Tk()
             temp_root.withdraw() # Hide the window
             rom_path = filedialog.askopenfilename(
                 title="Select CHIP-8 ROM",
                 filetypes=[("CHIP-8 ROMs", "*.ch8"), ("All Files", "*.*")]
             )
             temp_root.destroy()
        else:
            # Use the main window as parent
            rom_path = filedialog.askopenfilename(
                 title="Select CHIP-8 ROM",
                 filetypes=[("CHIP-8 ROMs", "*.ch8"), ("All Files", "*.*")],
                 parent=self.root
             )
        if rom_path:
            self.rom_path = rom_path
            self.load_rom(self.rom_path)
            # If this is the initial load and GUI isn't running, start it
            if not hasattr(self, 'root') or not self.root:
                self.run()
        else:
            print("No ROM selected.")
            # Update status if GUI exists
            if hasattr(self, 'status_label'):
                 self.status_label.config(text="No ROM Loaded")
            # Don't exit if GUI is running, just don't load a ROM

    def save_state(self):
        if not self.rom_path:
            print("No ROM loaded, cannot save state.")
            return
        state = dict(memory=self.memory, V=self.V, I=self.I, pc=self.pc,
                     stack=self.stack, delay_timer=self.delay_timer,
                     sound_timer=self.sound_timer, display=self.display, keys=self.keys)
        try:
            with open(self.rom_path + '.state', 'wb') as f:
                pickle.dump(state, f)
            print('State saved.')
            if hasattr(self, 'status_label'):
                 self.status_label.config(text=f"State saved for {self.rom_name}")
        except Exception as e:
            error_msg = f'Error saving state: {e}'
            print(error_msg)
            if hasattr(self, 'status_label'):
                 self.status_label.config(text=error_msg)

    def load_state(self):
        if not self.rom_path:
             print("No ROM loaded, cannot load state.")
             return
        fname = self.rom_path + '.state'
        if os.path.exists(fname):
            try:
                with open(fname, 'rb') as f:
                    st = pickle.load(f)
                    self.__dict__.update(st)
                print('State loaded.')
                if hasattr(self, 'status_label'):
                     self.status_label.config(text=f"State loaded for {self.rom_name}")
            except Exception as e:
                 error_msg = f'Error loading state: {e}'
                 print(error_msg)
                 if hasattr(self, 'status_label'):
                     self.status_label.config(text=error_msg)
        else:
            msg = 'No saved state found.'
            print(msg)
            if hasattr(self, 'status_label'):
                 self.status_label.config(text=msg)

    def cycle(self):
        if self.paused or not self.rom_path: # Don't cycle if no ROM
            return
        if self.step_mode:
            self.paused = True
            self.step_mode = False
        opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]
        self.pc += 2
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        n = opcode & 0x000F
        nn = opcode & 0x00FF
        nnn = opcode & 0x0FFF

        # Opcode handling
        if opcode == 0x00E0:  # Clear screen
            self.display = [[0]*self.width for _ in range(self.height)]
        elif opcode == 0x00EE:  # Return from subroutine
            self.pc = self.stack.pop()
        elif (opcode & 0xF000) == 0x1000:  # JP addr
            self.pc = nnn
        elif (opcode & 0xF000) == 0x2000:  # CALL addr
            self.stack.append(self.pc)
            self.pc = nnn
        elif (opcode & 0xF000) == 0x3000:  # SE Vx, byte
            if self.V[x] == nn:
                self.pc += 2
        elif (opcode & 0xF000) == 0x4000:  # SNE Vx, byte
            if self.V[x] != nn:
                self.pc += 2
        elif (opcode & 0xF000) == 0x5000:  # SE Vx, Vy
            if self.V[x] == self.V[y]:
                self.pc += 2
        elif (opcode & 0xF000) == 0x6000:  # LD Vx, byte
            self.V[x] = nn
        elif (opcode & 0xF000) == 0x7000:  # ADD Vx, byte
            self.V[x] = (self.V[x] + nn) & 0xFF
        elif (opcode & 0xF00F) == 0x8000:  # LD Vx, Vy
            self.V[x] = self.V[y]
        elif (opcode & 0xF00F) == 0x8001:  # OR Vx, Vy
            self.V[x] |= self.V[y]
        elif (opcode & 0xF00F) == 0x8002:  # AND Vx, Vy
            self.V[x] &= self.V[y]
        elif (opcode & 0xF00F) == 0x8003:  # XOR Vx, Vy
            self.V[x] ^= self.V[y]
        elif (opcode & 0xF00F) == 0x8004:  # ADD Vx, Vy
            result = self.V[x] + self.V[y]
            self.V[0xF] = 1 if result > 0xFF else 0
            self.V[x] = result & 0xFF
        elif (opcode & 0xF00F) == 0x8005:  # SUB Vx, Vy
            self.V[0xF] = 1 if self.V[x] > self.V[y] else 0
            self.V[x] = (self.V[x] - self.V[y]) & 0xFF
        elif (opcode & 0xF00F) == 0x8006:  # SHR Vx {, Vy}
            self.V[0xF] = self.V[x] & 0x1
            self.V[x] >>= 1
        elif (opcode & 0xF00F) == 0x8007:  # SUBN Vx, Vy
            self.V[0xF] = 1 if self.V[y] > self.V[x] else 0
            self.V[x] = (self.V[y] - self.V[x]) & 0xFF
        elif (opcode & 0xF00F) == 0x800E:  # SHL Vx {, Vy}
            self.V[0xF] = (self.V[x] & 0x80) >> 7
            self.V[x] = (self.V[x] << 1) & 0xFF
        elif (opcode & 0xF000) == 0x9000:  # SNE Vx, Vy
            if self.V[x] != self.V[y]:
                self.pc += 2
        elif (opcode & 0xF000) == 0xA000:  # LD I, addr
            self.I = nnn
        elif (opcode & 0xF000) == 0xB000:  # JP V0, addr
            self.pc = nnn + self.V[0]
        elif (opcode & 0xF000) == 0xC000:  # RND Vx, byte
            self.V[x] = random.randint(0, 255) & nn
        elif (opcode & 0xF000) == 0xD000:  # DRW Vx, Vy, nibble
            self.V[0xF] = 0
            for i in range(n):
                sprite_byte = self.memory[self.I + i]
                for j in range(8):
                    if sprite_byte & (0x80 >> j):
                        pixel_x = (self.V[x] + j) % self.width
                        pixel_y = (self.V[y] + i) % self.height
                        if self.display[pixel_y][pixel_x] == 1:
                            self.V[0xF] = 1
                        self.display[pixel_y][pixel_x] ^= 1
        elif (opcode & 0xF0FF) == 0xE09E:  # SKP Vx
            if self.keys[self.V[x]] == 1:
                self.pc += 2
        elif (opcode & 0xF0FF) == 0xE0A1:  # SKNP Vx
            if self.keys[self.V[x]] == 0:
                self.pc += 2
        elif (opcode & 0xF0FF) == 0xF007:  # LD Vx, DT
            self.V[x] = self.delay_timer
        elif (opcode & 0xF0FF) == 0xF00A:  # LD Vx, K
            key_pressed = False
            for i, key in enumerate(self.keys):
                if key == 1:
                    self.V[x] = i
                    key_pressed = True
                    break
            if not key_pressed:
                self.pc -= 2  # Wait for key press
        elif (opcode & 0xF0FF) == 0xF015:  # LD DT, Vx
            self.delay_timer = self.V[x]
        elif (opcode & 0xF0FF) == 0xF018:  # LD ST, Vx
            self.sound_timer = self.V[x]
        elif (opcode & 0xF0FF) == 0xF01E:  # ADD I, Vx
            result = self.I + self.V[x]
            self.V[0xF] = 1 if result > 0xFFF else 0
            self.I = result & 0xFFF
        elif (opcode & 0xF0FF) == 0xF029:  # LD F, Vx
            self.I = self.V[x] * 5
        elif (opcode & 0xF0FF) == 0xF033:  # LD B, Vx
            self.memory[self.I] = self.V[x] // 100
            self.memory[self.I + 1] = (self.V[x] // 10) % 10
            self.memory[self.I + 2] = self.V[x] % 10
        elif (opcode & 0xF0FF) == 0xF055:  # LD [I], Vx
            for i in range(x + 1):
                self.memory[self.I + i] = self.V[i]
        elif (opcode & 0xF0FF) == 0xF065:  # LD Vx, [I]
            for i in range(x + 1):
                self.V[i] = self.memory[self.I + i]

        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1
            # Play sound in a separate thread to avoid blocking
            if not hasattr(self, '_sound_thread') or not self._sound_thread.is_alive():
                self._sound_thread = threading.Thread(target=lambda: os.system('afplay /System/Library/Sounds/Pop.aiff &'))
                self._sound_thread.start()

    def draw(self):
        if not hasattr(self, 'canvas'):
             return # Canvas not created yet
        self.canvas.delete('pixel')
        for y in range(self.height):
            for x in range(self.width):
                if self.display[y][x]:
                    x0 = x * self.pixel_width
                    y0 = y * self.pixel_height
                    x1 = x0 + self.pixel_width
                    y1 = y0 + self.pixel_height
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill='white', outline='', tag='pixel')

    def create_menu(self):
        menubar = Menu(self.root)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open ROM...", command=self.prompt_for_rom)
        filemenu.add_separator()
        filemenu.add_command(label="Save State", command=self.save_state)
        filemenu.add_command(label="Load State", command=self.load_state)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.destroy)
        menubar.add_cascade(label="File", menu=filemenu)

        emumenu = Menu(menubar, tearoff=0)
        emumenu.add_command(label="Pause/Resume", command=self._toggle_pause)
        emumenu.add_command(label="Step", command=self._step)
        menubar.add_cascade(label="Emulation", menu=emumenu)

        self.root.config(menu=menubar)

    def run(self):
        # If no ROM path and GUI not initialized, prompt for ROM
        if not self.rom_path and (not hasattr(self, 'root') or not self.root):
             # Note: Prompting before GUI creation might be tricky.
             # Let's just create the GUI first.
             pass # We'll handle initial ROM load in the GUI setup

        self.root = tk.Tk()
        self.root.title('CHIP-8 Emulator')
        # Removed fullscreen for mGBA-like windowed look
        # self.root.attributes('-fullscreen', True)

        # Create Menu Bar (mGBA style)
        self.create_menu()

        # Main Canvas for Emulation
        self.canvas = tk.Canvas(self.root, width=self.window_width, height=self.window_height, bg='black', highlightthickness=0)
        self.canvas.pack()

        # Status Bar (mGBA style)
        self.status_label = Label(self.root, text=f"ROM: {self.rom_name}", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        # Key bindings
        for k in self.keymap:
            # Bind both upper and lower case for convenience
            self.root.bind(f'<KeyPress-{k}>', lambda e, k=k: self._set_key(k, 1))
            self.root.bind(f'<KeyRelease-{k}>', lambda e, k=k: self._set_key(k, 0))
            upper_k = k.upper()
            if upper_k != k:
                self.root.bind(f'<KeyPress-{upper_k}>', lambda e, k=k: self._set_key(k, 1)) # Map uppercase key press to lowercase key
                self.root.bind(f'<KeyRelease-{upper_k}>', lambda e, k=k: self._set_key(k, 0)) # Map uppercase key release to lowercase key

        # Also bind Escape to exit
        self.root.bind('<Escape>', lambda e: self.root.destroy())

        # Emulation loop
        self.last_time = time.perf_counter()
        self.root.after(16, self._loop)

        # If ROM path was given, load it now
        if self.rom_path:
            self.load_rom(self.rom_path)
        else:
            # If no ROM provided initially, prompt or just start empty
            # self.prompt_for_rom() # Optionally prompt immediately
            self.status_label.config(text="No ROM Loaded. Use File -> Open ROM.")

        self.root.mainloop()

    def _loop(self):
        if not self.paused:
            self.cycle()
            self.skip_count += 1
            if self.skip_count >= self.frame_skip:
                self.draw()
                self.skip_count = 0
        self.root.after(16, self._loop)  # ~60 FPS

    def _set_key(self, k, val):
        # Handle both upper and lower case keys
        lower_k = k.lower()
        if lower_k in self.keymap:
             self.keys[self.keymap[lower_k]] = val
             # Optionally update status to show key pressed (for debugging)
             # if val == 1:
             #     self.status_label.config(text=f"Key Pressed: {self.reverse_keymap.get(self.keymap[lower_k], 'Unknown')} ({lower_k.upper()})")

    def _toggle_pause(self):
        self.paused = not self.paused
        state = "Paused" if self.paused else "Running"
        print(f"Emulation {state}")
        if hasattr(self, 'status_label'):
             current_text = self.status_label.cget("text")
             # Simple way to append state, you might want a better status management
             if "Paused" in current_text or "Running" in current_text:
                 # Replace state part
                 new_text = " ".join(current_text.split(" ")[:-1]) + f" ({state})"
             else:
                 new_text = f"{current_text} ({state})"
             self.status_label.config(text=new_text)

    def _step(self):
        self.step_mode = True
        self.paused = False # Need to unpause to execute one step
        print("Stepping...")
        if hasattr(self, 'status_label'):
             self.status_label.config(text=f"Stepping... ROM: {self.rom_name}")


if __name__ == '__main__':
    # Check if a ROM path was provided via command line (optional now)
    rom_path = sys.argv[1] if len(sys.argv) > 1 else None

    # Create emulator instance, potentially with a ROM path
    emulator = Chip8(rom_path=rom_path)

    # Start the emulator
    emulator.run()qw
