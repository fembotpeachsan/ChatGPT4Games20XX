import pygame
import sys
import os

# Initialize Pygame
pygame.init()

# GBA screen dimensions
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 160
SCALE = 2  # Scale up for visibility
WINDOW = pygame.display.set_mode((SCREEN_WIDTH * SCALE, SCREEN_HEIGHT * SCALE))
pygame.display.set_caption("Simple GBA Emulator")

# Colors (for basic rendering)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Memory layout (simplified)
class Memory:
    def __init__(self, rom_path):
        self.rom = self.load_rom(rom_path)  # Game ROM
        self.wram = bytearray(256 * 1024)  # 256 KB Work RAM
        self.registers = bytearray(0x400)  # I/O registers (simplified)
        self.vram = bytearray(96 * 1024)   # 96 KB Video RAM

    def load_rom(self, rom_path):
        if not os.path.exists(rom_path):
            raise FileNotFoundError(f"ROM file {rom_path} not found")
        with open(rom_path, "rb") as f:
            return bytearray(f.read())

    def read32(self, addr):
        # Read 32-bit word from memory (little-endian)
        if addr >= 0x08000000 and addr < 0x0E000000:  # ROM space
            offset = addr - 0x08000000
            if offset + 3 < len(self.rom):
                return (self.rom[offset] | (self.rom[offset + 1] << 8) |
                        (self.rom[offset + 2] << 16) | (self.rom[offset + 3] << 24))
        elif addr < 0x04000000:  # WRAM
            offset = addr % len(self.wram)
            return (self.wram[offset] | (self.wram[offset + 1] << 8) |
                    (self.wram[offset + 2] << 16) | (self.wram[offset + 3] << 24))
        return 0

    def write32(self, addr, value):
        # Write 32-bit word to memory
        if addr < 0x04000000:  # WRAM
            offset = addr % len(self.wram)
            self.wram[offset:offset + 4] = [
                value & 0xFF, (value >> 8) & 0xFF,
                (value >> 16) & 0xFF, (value >> 24) & 0xFF
            ]
        elif addr >= 0x05000000 and addr < 0x07000000:  # VRAM (simplified)
            offset = addr - 0x06000000
            if offset + 3 < len(self.vram):
                self.vram[offset:offset + 4] = [
                    value & 0xFF, (value >> 8) & 0xFF,
                    (value >> 16) & 0xFF, (value >> 24) & 0xFF
                ]

# CPU (ARM7TDMI, simplified)
class CPU:
    def __init__(self, memory):
        self.memory = memory
        self.regs = [0] * 16  # R0-R15 (R15 = PC)
        self.regs[15] = 0x08000000  # Start at ROM entry point
        self.cpsr = 0  # Condition flags (simplified)

    def fetch(self):
        instr = self.memory.read32(self.regs[15])
        self.regs[15] += 4  # Increment PC
        return instr

    def execute(self, instr):
        # Decode and execute basic ARM instructions
        cond = (instr >> 28) & 0xF
        if not self.check_condition(cond):
            return

        opcode = (instr >> 21) & 0xF
        rn = (instr >> 16) & 0xF  # Base register
        rd = (instr >> 12) & 0xF  # Destination register
        operand2 = instr & 0xFFF  # Immediate or shifted value

        if opcode == 0xA:  # ADD
            self.regs[rd] = self.regs[rn] + operand2
        elif opcode == 0xE:  # SUB
            self.regs[rd] = self.regs[rn] - operand2
        elif (instr & 0x0FFFFF00) == 0x0E000F00:  # SWI (software interrupt, simplified)
            print(f"SWI called with {instr & 0xFF}")
        elif (instr & 0x0F000000) == 0x0A000000:  # B (branch)
            offset = instr & 0xFFFFFF
            if offset & 0x800000:  # Sign extend
                offset -= 0x1000000
            self.regs[15] += (offset << 2) + 4  # Branch with link offset

    def check_condition(self, cond):
        # Simplified condition check (always true for now)
        return True

# Emulator class
class GBAEmulator:
    def __init__(self, rom_path):
        self.memory = Memory(rom_path)
        self.cpu = CPU(self.memory)
        self.clock = pygame.time.Clock()

    def render(self):
        # Very basic rendering (draws VRAM as pixels)
        WINDOW.fill(BLACK)
        for y in range(SCREEN_HEIGHT):
            for x in range(SCREEN_WIDTH):
                addr = (y * SCREEN_WIDTH + x) * 2  # 16-bit color per pixel
                if addr + 1 < len(self.memory.vram):
                    color = self.memory.vram[addr] | (self.memory.vram[addr + 1] << 8)
                    r = (color & 0x1F) << 3
                    g = ((color >> 5) & 0x1F) << 3
                    b = ((color >> 10) & 0x1F) << 3
                    pygame.draw.rect(WINDOW, (r, g, b), (x * SCALE, y * SCALE, SCALE, SCALE))
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Execute one instruction per frame (not cycle-accurate)
            instr = self.cpu.fetch()
            self.cpu.execute(instr)

            # Render screen
            self.render()
            self.clock.tick(60)  # 60 FPS

        pygame.quit()

# Main entry point
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python gba_emulator.py <rom_path>")
        sys.exit(1)

    rom_path = sys.argv[1]
    emulator = GBAEmulator(rom_path)
    emulator.run()
