import tkinter as tk
from tkinter import filedialog
from functools import partial
import subprocess
import os

class Snex9xBackend:
    def __init__(self):
        self.snex9x_path = "path/to/snes9x"
        self.current_rom = None
        self.rom_data = bytearray()

    def load_rom(self, rom_path):
        """
        Loads the ROM into memory and spawns Snes9x as a subprocess.
        Stores the ROM data locally for a basic memory viewer.
        """
        self.current_rom = rom_path
        self.rom_data.clear()

        if not os.path.isfile(self.current_rom):
            print(f"ROM not found: {self.current_rom}")
            return

        try:
            with open(self.current_rom, "rb") as f:
                self.rom_data.extend(f.read())
        except Exception as e:
            print(f"Error reading ROM file: {e}")
            return

        try:
            subprocess.Popen(
                [self.snex9x_path, self.current_rom],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except FileNotFoundError:
            print("Snes9x executable not found at the specified path.")
        except Exception as e:
            print(f"An error occurred while trying to run Snes9x: {e}")

class DynamicRecompilingNES:
    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.title("No$GBA - SNES Emulation")
        self.master.geometry("1200x800")

        self.snes_backend = Snex9xBackend()

        self.create_gui()

    def create_gui(self):
        """
        Creates a minimal interface resembling a No$GBA-style window:
          - A button to load a game
          - A text widget to display memory contents
          - A canvas to emulate the screen output
        """
        self.load_button = tk.Button(
            self.master, text="Load SNES Game", command=self.load_game
        )
        self.load_button.pack(pady=10)

        self.game_label_var = tk.StringVar(value="No game loaded")
        self.game_label = tk.Label(self.master, textvariable=self.game_label_var)
        self.game_label.pack()

        self.memory_display = tk.Text(self.master, height=10, width=50)
        self.memory_display.pack(pady=5)

        self.ppu_display = tk.Canvas(self.master, width=256, height=240, bg="black")
        self.ppu_display.pack(pady=5)

        self.update_mem_button = tk.Button(
            self.master, text="Refresh Memory View", command=self.update_memory_display
        )
        self.update_mem_button.pack(pady=5)

    def load_game(self):
        """
        Opens a file dialog for the user to select a SNES ROM.
        Loads it via Snex9xBackend, then updates the GUI label.
        """
        rom_path = filedialog.askopenfilename(
            title="Select SNES ROM",
            filetypes=[("SNES ROM Files", "*.smc *.sfc *.fig *.bin *.zip *.7z")]
        )
        if rom_path:
            self.snes_backend.load_rom(rom_path)
            self.game_label_var.set(f"Loaded: {os.path.basename(rom_path)}")
            self.update_memory_display()

    def update_memory_display(self):
        """
        Shows a portion of the locally stored ROM data in hex.
        If no ROM is loaded, it shows a placeholder message.
        """
        self.memory_display.delete('1.0', tk.END)

        if not self.snes_backend.rom_data:
            self.memory_display.insert(tk.END, "No ROM loaded.\n")
            return

        # Display the first 512 bytes (32 lines of 16 bytes each) for example
        display_size = min(len(self.snes_backend.rom_data), 512)
        for i in range(0, display_size, 16):
            chunk = self.snes_backend.rom_data[i:i+16]
            hex_line = " ".join(f"{byte:02X}" for byte in chunk)
            self.memory_display.insert(tk.END, f"{i:04X}: {hex_line}\n")

if __name__ == "__main__":
    root = tk.Tk()
    emulator = DynamicRecompilingNES(root)
    root.mainloop()
