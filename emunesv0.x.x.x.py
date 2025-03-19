# test_v0.py
# A simplified NES emulator in Python 3, with a "Vibe Mode" color swirl.
# Translated directly (and naively) from the provided C++ example.

import sys
import pygame
import struct
import time

SCREEN_WIDTH  = 256
SCREEN_HEIGHT = 240

MASTER_CYCLES_PER_FRAME = 29781
CPU_FREQ                = 1789773
PPU_FREQ                = 5369318

def makeWord(low, high):
    return (low & 0xFF) | ((high & 0xFF) << 8)

class Cartridge:
    def __init__(self):
        self.prgROM = []
        self.chrROM = []
        self.hasCHRRAM = False

    def load(self, path):
        try:
            with open(path, 'rb') as rom:
                header = rom.read(16)
                if len(header) < 16 or header[0:4] != b'NES\x1A':
                    print("Not a valid iNES ROM.")
                    return False
                prgCount = header[4]
                chrCount = header[5]
                prgSize  = prgCount * 16384
                chrSize  = chrCount * 8192
                trainerPresent = (header[6] & 0x04) != 0
                if trainerPresent:
                    rom.seek(512, 1)
                self.prgROM = list(rom.read(prgSize))
                if chrSize > 0:
                    self.chrROM = list(rom.read(chrSize))
                else:
                    self.chrROM = [0]*8192
                    self.hasCHRRAM = True
                if len(self.prgROM) < prgSize:
                    print("Error reading PRG ROM data.")
                    return False
        except:
            print("Could not open ROM file.")
            return False
        return True

class PPU:
    def __init__(self):
        self.framebuffer = [0]*(SCREEN_WIDTH*SCREEN_HEIGHT)
        self.nametable   = [0]*2048
        self.OAM         = [0]*256
        self.PPUCTRL     = 0
        self.PPUMASK     = 0
        self.PPUSTATUS   = 0
        self.OAMADDR     = 0
        self.OAMDATA     = 0
        self.PPUSCROLL   = 0
        self.PPUADDR     = 0
        self.PPUDATA     = 0
        self.latch       = False
        self.vramAddr    = 0
        self.tempAddr    = 0
        self.fineX       = 0
        self.chrROM      = None

    def writeRegister(self, addr, val):
        reg = addr & 7
        if reg == 0:  # 0x2000
            self.PPUCTRL = val
        elif reg == 1:  # 0x2001
            self.PPUMASK = val
        elif reg == 2:  # 0x2002
            pass
        elif reg == 3:  # 0x2003
            self.OAMADDR = val
        elif reg == 4:  # 0x2004
            self.OAM[self.OAMADDR & 0xFF] = val
            self.OAMADDR = (self.OAMADDR + 1) & 0xFF
        elif reg == 5:  # 0x2005
            if not self.latch:
                self.tempAddr = (self.tempAddr & 0xFFE0) | (val >> 3)
                self.fineX    = val & 0x07
                self.latch    = True
            else:
                self.tempAddr = (self.tempAddr & 0x8FFF) | ((val & 0x07) << 12)
                self.tempAddr = (self.tempAddr & 0xFC1F) | ((val & 0xF8) << 2)
                self.latch    = False
        elif reg == 6:  # 0x2006
            if not self.latch:
                self.tempAddr = (self.tempAddr & 0x00FF) | ((val & 0x3F) << 8)
                self.latch    = True
            else:
                self.tempAddr = (self.tempAddr & 0xFF00) | val
                self.vramAddr = self.tempAddr
                self.latch    = False
        elif reg == 7:  # 0x2007
            self.writeVRAM(self.vramAddr, val)
            if self.PPUCTRL & 0x04:
                self.vramAddr = (self.vramAddr + 32) & 0xFFFF
            else:
                self.vramAddr = (self.vramAddr + 1) & 0xFFFF

    def readRegister(self, addr):
        data = 0
        reg = addr & 7
        if reg == 2:  # 0x2002
            data = self.PPUSTATUS
            self.PPUSTATUS &= 0x7F
            self.latch = False
        elif reg == 4:  # 0x2004
            data = self.OAM[self.OAMADDR & 0xFF]
        elif reg == 7:  # 0x2007
            data = self.readVRAM(self.vramAddr)
            if self.PPUCTRL & 0x04:
                self.vramAddr = (self.vramAddr + 32) & 0xFFFF
            else:
                self.vramAddr = (self.vramAddr + 1) & 0xFFFF
        return data

    def writeVRAM(self, addr, val):
        addr &= 0x3FFF
        if addr < 0x2000:
            if addr < len(self.chrROM):
                self.chrROM[addr] = val
        elif addr < 0x3F00:
            self.nametable[addr & 0x07FF] = val
        else:
            pass

    def readVRAM(self, addr):
        addr &= 0x3FFF
        if addr < 0x2000:
            if addr < len(self.chrROM):
                return self.chrROM[addr]
            return 0
        elif addr < 0x3F00:
            return self.nametable[addr & 0x07FF]
        else:
            return 0

    def renderBackground(self):
        baseNT = 0x2000
        for row in range(30):
            for col in range(32):
                ntAddr = baseNT + row*32 + col
                tileIndex = self.nametable[ntAddr & 0x07FF]
                patternAddr = ((self.PPUCTRL & 0x10) and 0x1000 or 0x0000) + (tileIndex*16)
                for fy in range(8):
                    lowByte  = self.readVRAM(patternAddr + fy)
                    highByte = self.readVRAM(patternAddr + fy + 8)
                    for fx in range(8):
                        bit = 7 - fx
                        paletteIndex = ((lowByte >> bit) & 1) | (((highByte >> bit) & 1) << 1)
                        color = 0xFF606060
                        if paletteIndex == 1:
                            color = 0xFFFF0000
                        elif paletteIndex == 2:
                            color = 0xFF00FF00
                        elif paletteIndex == 3:
                            color = 0xFF0000FF
                        sx = col*8 + fx
                        sy = row*8 + fy
                        if sx < SCREEN_WIDTH and sy < SCREEN_HEIGHT:
                            self.framebuffer[sy*SCREEN_WIDTH + sx] = color

    def renderSprites(self):
        for i in range(64):
            y    = self.OAM[i*4 + 0]
            tile = self.OAM[i*4 + 1]
            attr = self.OAM[i*4 + 2]
            x    = self.OAM[i*4 + 3]
            flipH = (attr & 0x40) != 0
            flipV = (attr & 0x80) != 0
            patternAddr = ((self.PPUCTRL & 0x08) and 0x1000 or 0x0000) + (tile*16)
            for row in range(8):
                actualRow = (7 - row) if flipV else row
                lowByte  = self.readVRAM(patternAddr + actualRow)
                highByte = self.readVRAM(patternAddr + actualRow + 8)
                for col in range(8):
                    bit = col if flipH else (7 - col)
                    paletteIndex = ((lowByte >> bit) & 1) | (((highByte >> bit) & 1) << 1)
                    if paletteIndex == 0:
                        continue
                    color = 0xFFFFFFFF
                    if paletteIndex == 1:
                        color = 0xFFFFFF00
                    elif paletteIndex == 2:
                        color = 0xFFFF00FF
                    elif paletteIndex == 3:
                        color = 0xFF00FFFF
                    px = x + col
                    py = y + row
                    if 0 <= px < SCREEN_WIDTH and 0 <= py < SCREEN_HEIGHT:
                        self.framebuffer[py*SCREEN_WIDTH + px] = color

    def render(self):
        if self.PPUMASK & 0x08:
            self.renderBackground()
        else:
            for i in range(SCREEN_WIDTH*SCREEN_HEIGHT):
                self.framebuffer[i] = 0xFF000000
        if self.PPUMASK & 0x10:
            self.renderSprites()

class APU:
    def writeRegister(self, addr, val):
        pass
    def readRegister(self, addr):
        return 0
    def step(self):
        pass

class Controller:
    def __init__(self):
        self.state   = 0
        self.shiftReg= 0
        self.strobe  = False
    def write(self, val):
        newStrobe = (val & 1) != 0
        if not self.strobe and newStrobe:
            self.shiftReg = self.state
        self.strobe = newStrobe
        if self.strobe:
            self.shiftReg = self.state
    def read(self):
        ret = self.shiftReg & 1
        self.shiftReg >>= 1
        return ret

class CPU:
    def __init__(self):
        self.A  = 0
        self.X  = 0
        self.Y  = 0
        self.SP = 0xFD
        self.P  = 0x24
        self.PC = 0xC000
        self.RAM = [0]*2048
        self.cart = None
        self.ppu  = None
        self.apu  = None
        self.controller = None

    def read(self, addr):
        addr &= 0xFFFF
        if addr < 0x2000:
            return self.RAM[addr & 0x07FF]
        elif addr < 0x4000:
            return self.ppu.readRegister(addr)
        elif addr == 0x4016:
            return self.controller.read()
        elif addr == 0x4017:
            return 0
        elif addr < 0x4018:
            if addr < 0x4014:
                return self.apu.readRegister(addr)
            return 0
        elif addr >= 0x8000:
            sz = len(self.cart.prgROM)
            if sz == 16384:
                return self.cart.prgROM[addr & 0x3FFF]
            else:
                return self.cart.prgROM[addr & 0x7FFF]
        return 0

    def write(self, addr, val):
        addr &= 0xFFFF
        val  &= 0xFF
        if addr < 0x2000:
            self.RAM[addr & 0x07FF] = val
        elif addr < 0x4000:
            self.ppu.writeRegister(addr, val)
        elif addr == 0x4014:
            base = val << 8
            for i in range(256):
                self.ppu.OAM[i] = self.read(base + i)
        elif addr == 0x4016:
            self.controller.write(val)
        elif addr < 0x4018:
            self.apu.writeRegister(addr, val)
        else:
            pass

    def setNZ(self, value):
        value &= 0xFF
        if value & 0x80:
            self.P |= 0x80
        else:
            self.P &= ~0x80
        if value == 0:
            self.P |= 0x02
        else:
            self.P &= ~0x02

    def reset(self):
        self.A  = 0
        self.X  = 0
        self.Y  = 0
        self.P  = 0x24
        self.SP = 0xFD
        lo = self.read(0xFFFC)
        hi = self.read(0xFFFD)
        self.PC = makeWord(lo, hi)

    def nmi(self):
        self.push((self.PC >> 8) & 0xFF)
        self.push(self.PC & 0xFF)
        self.push(self.P & ~0x10)
        self.P |= 0x04
        lo = self.read(0xFFFA)
        hi = self.read(0xFFFB)
        self.PC = makeWord(lo, hi)

    def irq(self):
        if self.P & 0x04:
            return
        self.push((self.PC >> 8) & 0xFF)
        self.push(self.PC & 0xFF)
        self.push(self.P & ~0x10)
        self.P |= 0x04
        lo = self.read(0xFFFE)
        hi = self.read(0xFFFF)
        self.PC = makeWord(lo, hi)

    def push(self, val):
        self.write(0x0100 + (self.SP & 0xFF), val)
        self.SP = (self.SP - 1) & 0xFF

    def pop(self):
        self.SP = (self.SP + 1) & 0xFF
        return self.read(0x0100 + (self.SP & 0xFF))

    def imm(self):
        val = self.read(self.PC)
        self.PC = (self.PC + 1) & 0xFFFF
        return val

    def imm16(self):
        lo = self.imm()
        hi = self.imm()
        return makeWord(lo, hi)

    def zpg(self):
        return self.imm()
    def zpgX(self):
        return (self.imm() + self.X) & 0xFF
    def zpgY(self):
        return (self.imm() + self.Y) & 0xFF
    def abs_(self):
        return self.imm16()
    def absX(self, dummy=False):
        return (self.abs_() + self.X) & 0xFFFF
    def absY(self, dummy=False):
        return (self.abs_() + self.Y) & 0xFFFF
    def ind(self):
        ptr = self.imm16()
        lo = self.read(ptr)
        hi = self.read((ptr & 0xFF00) | ((ptr+1) & 0x00FF))
        return makeWord(lo, hi)
    def indX(self):
        base = self.imm()
        effZp = (base + self.X) & 0xFF
        lo = self.read(effZp)
        hi = self.read((effZp + 1) & 0xFF)
        return makeWord(lo, hi)
    def indY(self, dummy=False):
        base = self.imm()
        lo = self.read(base & 0xFF)
        hi = self.read((base+1) & 0xFF)
        return (makeWord(lo, hi) + self.Y) & 0xFFFF

    def opADC(self, val):
        sum_ = self.A + val + (self.P & 1)
        if sum_ > 0xFF:
            self.P |= 0x01
        else:
            self.P &= ~0x01
        result = sum_ & 0xFF
        overflow = ((~(self.A ^ val) & (self.A ^ result) & 0x80) != 0)
        if overflow:
            self.P |= 0x40
        else:
            self.P &= ~0x40
        self.A = result & 0xFF
        self.setNZ(self.A)

    def opSBC(self, val):
        self.opADC(val ^ 0xFF)

    def opCMP(self, lhs, rhs):
        tmp = (lhs - rhs) & 0x1FF
        if lhs >= rhs:
            self.P |= 0x01
        else:
            self.P &= ~0x01
        tmp &= 0xFF
        if tmp == 0:
            self.P |= 0x02
        else:
            self.P &= ~0x02
        if tmp & 0x80:
            self.P |= 0x80
        else:
            self.P &= ~0x80

    def step(self):
        opcode = self.read(self.PC)
        self.PC = (self.PC + 1) & 0xFFFF
        # Just do a big switch-like structure:
        if opcode == 0xA9:  # LDA imm
            self.A = self.imm(); self.setNZ(self.A)
        elif opcode == 0xA5:  # LDA zpg
            self.A = self.read(self.zpg()); self.setNZ(self.A)
        elif opcode == 0xB5:  # LDA zpgX
            self.A = self.read(self.zpgX()); self.setNZ(self.A)
        elif opcode == 0xAD:  # LDA abs
            self.A = self.read(self.abs_()); self.setNZ(self.A)
        elif opcode == 0xBD:  # LDA absX
            self.A = self.read(self.absX()); self.setNZ(self.A)
        elif opcode == 0xB9:  # LDA absY
            self.A = self.read(self.absY()); self.setNZ(self.A)
        elif opcode == 0xA1:  # LDA indX
            self.A = self.read(self.indX()); self.setNZ(self.A)
        elif opcode == 0xB1:  # LDA indY
            self.A = self.read(self.indY()); self.setNZ(self.A)

        elif opcode == 0xA2:  # LDX imm
            self.X = self.imm(); self.setNZ(self.X)
        elif opcode == 0xA6:  # LDX zpg
            self.X = self.read(self.zpg()); self.setNZ(self.X)
        elif opcode == 0xB6:  # LDX zpgY
            self.X = self.read(self.zpgY()); self.setNZ(self.X)
        elif opcode == 0xAE:  # LDX abs
            self.X = self.read(self.abs_()); self.setNZ(self.X)
        elif opcode == 0xBE:  # LDX absY
            self.X = self.read(self.absY()); self.setNZ(self.X)

        elif opcode == 0xA0:  # LDY imm
            self.Y = self.imm(); self.setNZ(self.Y)
        elif opcode == 0xA4:  # LDY zpg
            self.Y = self.read(self.zpg()); self.setNZ(self.Y)
        elif opcode == 0xB4:  # LDY zpgX
            self.Y = self.read(self.zpgX()); self.setNZ(self.Y)
        elif opcode == 0xAC:  # LDY abs
            self.Y = self.read(self.abs_()); self.setNZ(self.Y)
        elif opcode == 0xBC:  # LDY absX
            self.Y = self.read(self.absX()); self.setNZ(self.Y)

        elif opcode == 0x85:  # STA zpg
            self.write(self.zpg(), self.A)
        elif opcode == 0x95:  # STA zpgX
            self.write(self.zpgX(), self.A)
        elif opcode == 0x8D:  # STA abs
            self.write(self.abs_(), self.A)
        elif opcode == 0x9D:  # STA absX
            self.write(self.absX(), self.A)
        elif opcode == 0x99:  # STA absY
            self.write(self.absY(), self.A)
        elif opcode == 0x81:  # STA indX
            self.write(self.indX(), self.A)
        elif opcode == 0x91:  # STA indY
            self.write(self.indY(), self.A)

        elif opcode == 0x86:  # STX zpg
            self.write(self.zpg(), self.X)
        elif opcode == 0x96:  # STX zpgY
            self.write(self.zpgY(), self.X)
        elif opcode == 0x8E:  # STX abs
            self.write(self.abs_(), self.X)

        elif opcode == 0x84:  # STY zpg
            self.write(self.zpg(), self.Y)
        elif opcode == 0x94:  # STY zpgX
            self.write(self.zpgX(), self.Y)
        elif opcode == 0x8C:  # STY abs
            self.write(self.abs_(), self.Y)

        elif opcode == 0xAA:  # TAX
            self.X = self.A; self.setNZ(self.X)
        elif opcode == 0xA8:  # TAY
            self.Y = self.A; self.setNZ(self.Y)
        elif opcode == 0xBA:  # TSX
            self.X = self.SP; self.setNZ(self.X)
        elif opcode == 0x8A:  # TXA
            self.A = self.X; self.setNZ(self.A)
        elif opcode == 0x98:  # TYA
            self.A = self.Y; self.setNZ(self.A)
        elif opcode == 0x9A:  # TXS
            self.SP = self.X

        elif opcode == 0xE8:  # INX
            self.X = (self.X + 1) & 0xFF; self.setNZ(self.X)
        elif opcode == 0xC8:  # INY
            self.Y = (self.Y + 1) & 0xFF; self.setNZ(self.Y)
        elif opcode == 0xCA:  # DEX
            self.X = (self.X - 1) & 0xFF; self.setNZ(self.X)
        elif opcode == 0x88:  # DEY
            self.Y = (self.Y - 1) & 0xFF; self.setNZ(self.Y)

        elif opcode == 0x69:  # ADC imm
            self.opADC(self.imm())
        elif opcode == 0x65:  # ADC zpg
            self.opADC(self.read(self.zpg()))
        elif opcode == 0x75:  # ADC zpgX
            self.opADC(self.read(self.zpgX()))
        elif opcode == 0x6D:  # ADC abs
            self.opADC(self.read(self.abs_()))
        elif opcode == 0x7D:  # ADC absX
            self.opADC(self.read(self.absX()))
        elif opcode == 0x79:  # ADC absY
            self.opADC(self.read(self.absY()))
        elif opcode == 0x61:  # ADC indX
            self.opADC(self.read(self.indX()))
        elif opcode == 0x71:  # ADC indY
            self.opADC(self.read(self.indY()))

        elif opcode == 0xE9:  # SBC imm
            self.opSBC(self.imm())
        elif opcode == 0xE5:  # SBC zpg
            self.opSBC(self.read(self.zpg()))
        elif opcode == 0xF5:  # SBC zpgX
            self.opSBC(self.read(self.zpgX()))
        elif opcode == 0xED:  # SBC abs
            self.opSBC(self.read(self.abs_()))
        elif opcode == 0xFD:  # SBC absX
            self.opSBC(self.read(self.absX()))
        elif opcode == 0xF9:  # SBC absY
            self.opSBC(self.read(self.absY()))
        elif opcode == 0xE1:  # SBC indX
            self.opSBC(self.read(self.indX()))
        elif opcode == 0xF1:  # SBC indY
            self.opSBC(self.read(self.indY()))

        elif opcode == 0xC9:  # CMP imm
            self.opCMP(self.A, self.imm())
        elif opcode == 0xC5:  # CMP zpg
            self.opCMP(self.A, self.read(self.zpg()))
        elif opcode == 0xD5:  # CMP zpgX
            self.opCMP(self.A, self.read(self.zpgX()))
        elif opcode == 0xCD:  # CMP abs
            self.opCMP(self.A, self.read(self.abs_()))
        elif opcode == 0xDD:  # CMP absX
            self.opCMP(self.A, self.read(self.absX()))
        elif opcode == 0xD9:  # CMP absY
            self.opCMP(self.A, self.read(self.absY()))
        elif opcode == 0xC1:  # CMP indX
            self.opCMP(self.A, self.read(self.indX()))
        elif opcode == 0xD1:  # CMP indY
            self.opCMP(self.A, self.read(self.indY()))

        elif opcode == 0xE0:  # CPX imm
            self.opCMP(self.X, self.imm())
        elif opcode == 0xE4:  # CPX zpg
            self.opCMP(self.X, self.read(self.zpg()))
        elif opcode == 0xEC:  # CPX abs
            self.opCMP(self.X, self.read(self.abs_()))

        elif opcode == 0xC0:  # CPY imm
            self.opCMP(self.Y, self.imm())
        elif opcode == 0xC4:  # CPY zpg
            self.opCMP(self.Y, self.read(self.zpg()))
        elif opcode == 0xCC:  # CPY abs
            self.opCMP(self.Y, self.read(self.abs_()))

        elif opcode == 0x29:  # AND imm
            self.A &= self.imm(); self.setNZ(self.A)
        elif opcode == 0x09:  # ORA imm
            self.A |= self.imm(); self.setNZ(self.A)
        elif opcode == 0x49:  # EOR imm
            self.A ^= self.imm(); self.setNZ(self.A)

        elif opcode == 0x0A:  # ASL A
            c = (self.A & 0x80) != 0
            self.A = (self.A << 1) & 0xFF
            if c: self.P |= 0x01
            else: self.P &= ~0x01
            self.setNZ(self.A)
        elif opcode == 0x4A:  # LSR A
            c = (self.A & 0x01) != 0
            self.A >>= 1
            if c: self.P |= 0x01
            else: self.P &= ~0x01
            self.setNZ(self.A)
        elif opcode == 0x2A:  # ROL A
            c = (self.P & 0x01)
            newC = (self.A & 0x80) != 0
            self.A = ((self.A << 1) & 0xFF) | c
            if newC: self.P |= 0x01
            else: self.P &= ~0x01
            self.setNZ(self.A)
        elif opcode == 0x6A:  # ROR A
            c = (self.P & 0x01) << 7
            newC = (self.A & 0x01) != 0
            self.A = ((self.A >> 1) & 0x7F) | c
            if newC: self.P |= 0x01
            else: self.P &= ~0x01
            self.setNZ(self.A)

        elif opcode == 0x4C:  # JMP abs
            self.PC = self.imm16()
        elif opcode == 0x6C:  # JMP ind
            self.PC = self.ind()

        elif opcode == 0x20:  # JSR
            addr = self.imm16()
            ret = (self.PC - 1) & 0xFFFF
            self.push((ret >> 8) & 0xFF)
            self.push(ret & 0xFF)
            self.PC = addr
        elif opcode == 0x60:  # RTS
            lo = self.pop()
            hi = self.pop()
            self.PC = (makeWord(lo, hi) + 1) & 0xFFFF

        elif opcode == 0xD0:  # BNE
            off = struct.unpack('b', bytes([self.imm()]))[0]
            if not (self.P & 0x02):
                self.PC = (self.PC + off) & 0xFFFF
        elif opcode == 0xF0:  # BEQ
            off = struct.unpack('b', bytes([self.imm()]))[0]
            if (self.P & 0x02):
                self.PC = (self.PC + off) & 0xFFFF
        elif opcode == 0x90:  # BCC
            off = struct.unpack('b', bytes([self.imm()]))[0]
            if not (self.P & 0x01):
                self.PC = (self.PC + off) & 0xFFFF
        elif opcode == 0xB0:  # BCS
            off = struct.unpack('b', bytes([self.imm()]))[0]
            if (self.P & 0x01):
                self.PC = (self.PC + off) & 0xFFFF
        elif opcode == 0x10:  # BPL
            off = struct.unpack('b', bytes([self.imm()]))[0]
            if not (self.P & 0x80):
                self.PC = (self.PC + off) & 0xFFFF
        elif opcode == 0x30:  # BMI
            off = struct.unpack('b', bytes([self.imm()]))[0]
            if (self.P & 0x80):
                self.PC = (self.PC + off) & 0xFFFF
        elif opcode == 0x50:  # BVC
            off = struct.unpack('b', bytes([self.imm()]))[0]
            if not (self.P & 0x40):
                self.PC = (self.PC + off) & 0xFFFF
        elif opcode == 0x70:  # BVS
            off = struct.unpack('b', bytes([self.imm()]))[0]
            if (self.P & 0x40):
                self.PC = (self.PC + off) & 0xFFFF

        elif opcode == 0x24:  # BIT zpg
            val = self.read(self.zpg())
            tmp = self.A & val
            if tmp == 0:
                self.P |= 0x02
            else:
                self.P &= ~0x02
            self.P = (self.P & 0x3F) | (val & 0xC0)
        elif opcode == 0x2C:  # BIT abs
            val = self.read(self.abs_())
            tmp = self.A & val
            if tmp == 0:
                self.P |= 0x02
            else:
                self.P &= ~0x02
            self.P = (self.P & 0x3F) | (val & 0xC0)

        elif opcode == 0x00:  # BRK
            self.PC = (self.PC + 1) & 0xFFFF
            self.push((self.PC >> 8) & 0xFF)
            self.push(self.PC & 0xFF)
            self.push(self.P | 0x10)
            self.P |= 0x04
            lo = self.read(0xFFFE)
            hi = self.read(0xFFFF)
            self.PC = makeWord(lo, hi)
        elif opcode == 0x40:  # RTI
            flags = self.pop()
            self.P = flags
            lo = self.pop()
            hi = self.pop()
            self.PC = makeWord(lo, hi)
        else:
            pass

class NES:
    def __init__(self):
        self.cart = Cartridge()
        self.cpu  = CPU()
        self.ppu  = PPU()
        self.apu  = APU()
        self.controller = Controller()

    def loadROM(self, path):
        if not self.cart.load(path):
            return False
        self.cpu.cart = self.cart
        self.cpu.ppu  = self.ppu
        self.cpu.apu  = self.apu
        self.cpu.controller = self.controller
        self.ppu.chrROM = self.cart.chrROM
        self.reset()
        return True

    def reset(self):
        self.cpu.reset()

    def runFrame(self):
        for _ in range(MASTER_CYCLES_PER_FRAME):
            self.cpu.step()
            self.apu.step()
        if self.ppu.PPUCTRL & 0x80:
            self.cpu.nmi()
        self.ppu.render()

def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} romfile.nes")
        return

    pygame.init()
    window_scale = 2
    screen = pygame.display.set_mode((SCREEN_WIDTH*window_scale, SCREEN_HEIGHT*window_scale))
    pygame.display.set_caption("Vibe NES Emulator (Python)")

    nes = NES()
    if not nes.loadROM(sys.argv[1]):
        print("Failed to load ROM.")
        return

    vibeMode = False
    clock = pygame.time.Clock()
    running = True
    while running:
        frameStart = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_z:
                    nes.controller.state |= 0x80
                elif event.key == pygame.K_x:
                    nes.controller.state |= 0x40
                elif event.key == pygame.K_SPACE:
                    nes.controller.state |= 0x20
                elif event.key == pygame.K_RETURN:
                    nes.controller.state |= 0x10
                elif event.key == pygame.K_UP:
                    nes.controller.state |= 0x08
                elif event.key == pygame.K_DOWN:
                    nes.controller.state |= 0x04
                elif event.key == pygame.K_LEFT:
                    nes.controller.state |= 0x02
                elif event.key == pygame.K_RIGHT:
                    nes.controller.state |= 0x01
                elif event.key == pygame.K_v:
                    vibeMode = not vibeMode
                    print("[VIBE MODE ON]" if vibeMode else "[VIBE MODE OFF]")

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_z:
                    nes.controller.state &= ~0x80
                elif event.key == pygame.K_x:
                    nes.controller.state &= ~0x40
                elif event.key == pygame.K_SPACE:
                    nes.controller.state &= ~0x20
                elif event.key == pygame.K_RETURN:
                    nes.controller.state &= ~0x10
                elif event.key == pygame.K_UP:
                    nes.controller.state &= ~0x08
                elif event.key == pygame.K_DOWN:
                    nes.controller.state &= ~0x04
                elif event.key == pygame.K_LEFT:
                    nes.controller.state &= ~0x02
                elif event.key == pygame.K_RIGHT:
                    nes.controller.state &= ~0x01

        nes.runFrame()

        if vibeMode:
            for i in range(SCREEN_WIDTH*SCREEN_HEIGHT):
                pix = nes.ppu.framebuffer[i] & 0xFFFFFFFF
                a = (pix >> 24) & 0xFF
                r = (pix >> 16) & 0xFF
                g = (pix >> 8)  & 0xFF
                b = (pix >> 0)  & 0xFF
                nr, ng, nb = g, b, r
                nes.ppu.framebuffer[i] = (a << 24) | (nr << 16) | (ng << 8) | nb

        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surf_lock = pygame.surfarray.pixels2d(surf)
        for i in range(SCREEN_WIDTH*SCREEN_HEIGHT):
            surf_lock[i] = nes.ppu.framebuffer[i] & 0xFFFFFFFF
        del surf_lock

        scaled_surf = pygame.transform.scale(surf, (SCREEN_WIDTH*window_scale, SCREEN_HEIGHT*window_scale))
        screen.blit(scaled_surf, (0,0))
        pygame.display.flip()

        frameTime = pygame.time.get_ticks() - frameStart
        delay = max(0, int((1000/60) - frameTime))
        pygame.time.delay(delay)

    pygame.quit()

if __name__ == "__main__":
    main()
