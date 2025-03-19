/********************************************************************
 *  Simplified Full-Blown NES Emulator Example (Single-File) + Vibe Mode
 *  -------------------------------------------------------------------
 *  This is your existing simplified NES emulator with a “Vibe Mode”
 *  post-processing color swirl effect. Press 'V' in the emulator window
 *  to toggle the swirling colors. Not cycle-accurate but definitely vibey!
 *
 *  Build: g++ -O2 main.cpp -lSDL2 -o nes_emulator
 *  Run:   ./nes_emulator path/to/rom.nes
 ********************************************************************/

#include <SDL2/SDL.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <cstdint>
#include <cstring>

// ---------------------------------------------------------------------
//                          CONSTANTS
// ---------------------------------------------------------------------

static const int SCREEN_WIDTH  = 256;
static const int SCREEN_HEIGHT = 240;

static const uint32_t MASTER_CYCLES_PER_FRAME = 29781; // Approx, for demonstration
static const uint32_t CPU_FREQ                = 1789773;
static const uint32_t PPU_FREQ                = 5369318;

// ---------------------------------------------------------------------
//                      HELPER: read/write macros
// ---------------------------------------------------------------------
inline uint16_t makeWord(uint8_t low, uint8_t high) {
    return (uint16_t)(low) | ((uint16_t)(high) << 8);
}

// ---------------------------------------------------------------------
//                          CART & MAPPER
// ---------------------------------------------------------------------
class Cartridge {
public:
    std::vector<uint8_t> prgROM;
    std::vector<uint8_t> chrROM;
    bool hasCHRRAM = false;

    bool load(const char* path) {
        std::ifstream rom(path, std::ios::binary);
        if (!rom.good()) {
            std::cerr << "Could not open ROM file.\n";
            return false;
        }
        char header[16];
        rom.read(header, 16);
        if (strncmp(header, "NES\x1A", 4) != 0) {
            std::cerr << "Not a valid iNES ROM.\n";
            return false;
        }

        uint8_t prgCount = static_cast<uint8_t>(header[4]);
        uint8_t chrCount = static_cast<uint8_t>(header[5]);
        size_t prgSize = prgCount * 16384;
        size_t chrSize = chrCount * 8192;

        bool trainerPresent = header[6] & 0x04;
        if (trainerPresent) {
            // skip 512 trainer bytes
            rom.seekg(512, std::ios_base::cur);
        }

        prgROM.resize(prgSize);
        rom.read(reinterpret_cast<char*>(prgROM.data()), prgSize);

        if (chrSize > 0) {
            chrROM.resize(chrSize);
            rom.read(reinterpret_cast<char*>(chrROM.data()), chrSize);
        } else {
            // CHR RAM fallback
            chrROM.resize(8192);
            hasCHRRAM = true;
        }

        if (!rom.good()) {
            std::cerr << "Error reading ROM data.\n";
            return false;
        }
        return true;
    }
};

// ---------------------------------------------------------------------
//                              PPU
// ---------------------------------------------------------------------
class PPU {
public:
    uint32_t framebuffer[SCREEN_WIDTH * SCREEN_HEIGHT];
    uint8_t nametable[2048]; // 2KB VRAM
    uint8_t OAM[256];        // Sprite OAM

    // Registers
    uint8_t PPUCTRL   = 0;
    uint8_t PPUMASK   = 0;
    uint8_t PPUSTATUS = 0;
    uint8_t OAMADDR   = 0;
    uint8_t OAMDATA   = 0;
    uint8_t PPUSCROLL = 0;
    uint8_t PPUADDR   = 0;
    uint8_t PPUDATA   = 0;

    bool    latch     = false;
    uint16_t vramAddr = 0;
    uint16_t tempAddr = 0;
    uint8_t  fineX    = 0;

    // Pointer to CHR (ROM or RAM)
    std::vector<uint8_t>* chrROM;

    PPU() {
        memset(framebuffer, 0, sizeof(framebuffer));
        memset(nametable, 0, sizeof(nametable));
        memset(OAM, 0, sizeof(OAM));
    }

    void writeRegister(uint16_t addr, uint8_t val) {
        switch (addr & 7) {
            case 0: // $2000
                PPUCTRL = val;
                break;
            case 1: // $2001
                PPUMASK = val;
                break;
            case 2: // $2002 (write no effect in real hardware)
                break;
            case 3: // $2003
                OAMADDR = val;
                break;
            case 4: // $2004
                OAM[OAMADDR++] = val;
                break;
            case 5: // $2005
                if (!latch) {
                    tempAddr = (tempAddr & 0xFFE0) | (val >> 3);
                    fineX = val & 0x07;
                    latch = true;
                } else {
                    tempAddr = (tempAddr & 0x8FFF) | ((val & 0x07) << 12);
                    tempAddr = (tempAddr & 0xFC1F) | ((val & 0xF8) << 2);
                    latch = false;
                }
                break;
            case 6: // $2006
                if (!latch) {
                    tempAddr = (tempAddr & 0x00FF) | ((val & 0x3F) << 8);
                    latch = true;
                } else {
                    tempAddr = (tempAddr & 0xFF00) | val;
                    vramAddr = tempAddr;
                    latch = false;
                }
                break;
            case 7: // $2007
                writeVRAM(vramAddr, val);
                if (PPUCTRL & 0x04) vramAddr += 32; else vramAddr += 1;
                break;
        }
    }

    uint8_t readRegister(uint16_t addr) {
        uint8_t data = 0;
        switch (addr & 7) {
            case 2: { // $2002
                data = PPUSTATUS;
                // Clear VBlank
                PPUSTATUS &= 0x7F;
                latch = false;
            } break;
            case 4: { // $2004
                data = OAM[OAMADDR];
            } break;
            case 7: { // $2007
                data = readVRAM(vramAddr);
                if (PPUCTRL & 0x04) vramAddr += 32; else vramAddr += 1;
            } break;
        }
        return data;
    }

    void writeVRAM(uint16_t addr, uint8_t val) {
        addr &= 0x3FFF;
        if (addr < 0x2000) {
            // CHR (possibly RAM)
            if (chrROM->size() > addr) {
                (*chrROM)[addr] = val; 
            }
        } else if (addr < 0x3F00) {
            // Nametable
            nametable[addr & 0x07FF] = val;
        } else {
            // Palette range: ignoring details
        }
    }

    uint8_t readVRAM(uint16_t addr) {
        addr &= 0x3FFF;
        if (addr < 0x2000) {
            if (chrROM->size() > addr) {
                return (*chrROM)[addr];
            }
            return 0;
        } else if (addr < 0x3F00) {
            return nametable[addr & 0x07FF];
        } else {
            // Return palette data (stub)
            return 0;
        }
    }

    // -- Very naive background rendering (ignoring attributes, scrolling, etc.)
    void renderBackground() {
        uint16_t baseNT = 0x2000;
        for (int row = 0; row < 30; row++) {
            for (int col = 0; col < 32; col++) {
                uint16_t ntAddr = baseNT + row * 32 + col;
                uint8_t tileIndex = nametable[ntAddr & 0x07FF];
                // background pattern table from PPUCTRL bit 4
                uint16_t patternAddr = ((PPUCTRL & 0x10) ? 0x1000 : 0x0000) + (tileIndex * 16);

                for (int fy = 0; fy < 8; fy++) {
                    uint8_t lowByte  = readVRAM(patternAddr + fy);
                    uint8_t highByte = readVRAM(patternAddr + fy + 8);
                    for (int fx = 0; fx < 8; fx++) {
                        int bit = 7 - fx;
                        uint8_t paletteIndex = ((lowByte >> bit) & 1) | (((highByte >> bit) & 1) << 1);
                        uint32_t color = 0xFF606060; // default gray
                        if (paletteIndex == 1) color = 0xFFFF0000; // Red
                        if (paletteIndex == 2) color = 0xFF00FF00; // Green
                        if (paletteIndex == 3) color = 0xFF0000FF; // Blue

                        int sx = col * 8 + fx;
                        int sy = row * 8 + fy;
                        if (sx < SCREEN_WIDTH && sy < SCREEN_HEIGHT) {
                            framebuffer[sy * SCREEN_WIDTH + sx] = color;
                        }
                    }
                }
            }
        }
    }

    // -- Very naive sprite rendering
    void renderSprites() {
        for (int i = 0; i < 64; i++) {
            uint8_t y    = OAM[i * 4 + 0];
            uint8_t tile = OAM[i * 4 + 1];
            uint8_t attr = OAM[i * 4 + 2];
            uint8_t x    = OAM[i * 4 + 3];
            bool flipH   = (attr & 0x40) != 0;
            bool flipV   = (attr & 0x80) != 0;
            uint16_t patternAddr = ((PPUCTRL & 0x08) ? 0x1000 : 0x0000) + (tile * 16);

            for (int row = 0; row < 8; row++) {
                int actualRow = flipV ? (7 - row) : row;
                uint8_t lowByte  = readVRAM(patternAddr + actualRow);
                uint8_t highByte = readVRAM(patternAddr + actualRow + 8);
                for (int col = 0; col < 8; col++) {
                    int bit = flipH ? col : (7 - col);
                    uint8_t paletteIndex = ((lowByte >> bit) & 1) | (((highByte >> bit) & 1) << 1);
                    if (!paletteIndex) continue;

                    uint32_t color = 0xFFFFFFFF; 
                    if (paletteIndex == 1) color = 0xFFFFFF00; // Yellow
                    if (paletteIndex == 2) color = 0xFFFF00FF; // Magenta
                    if (paletteIndex == 3) color = 0xFF00FFFF; // Cyan

                    int px = x + col;
                    int py = y + row;
                    if (px < SCREEN_WIDTH && py < SCREEN_HEIGHT) {
                        framebuffer[py * SCREEN_WIDTH + px] = color;
                    }
                }
            }
        }
    }

    void render() {
        if (PPUMASK & 0x08) {
            renderBackground();
        } else {
            // Fill black
            for (int i = 0; i < SCREEN_WIDTH * SCREEN_HEIGHT; i++) {
                framebuffer[i] = 0xFF000000;
            }
        }
        if (PPUMASK & 0x10) {
            renderSprites();
        }
    }
};

// ---------------------------------------------------------------------
//                              APU (stub)
// ---------------------------------------------------------------------
class APU {
public:
    void writeRegister(uint16_t addr, uint8_t val) {
        (void)addr; (void)val;
    }
    uint8_t readRegister(uint16_t addr) {
        (void)addr;
        return 0;
    }
    void step() {
        // No real audio logic here
    }
};

// ---------------------------------------------------------------------
//                       INPUT (Controller)
// ---------------------------------------------------------------------
class Controller {
public:
    // 7 6 5 4 3 2 1 0
    // A B Select Start Up Down Left Right
    uint8_t state = 0;
    uint8_t shiftReg = 0;
    bool strobe = false;

    void write(uint8_t val) {
        bool newStrobe = (val & 1) != 0;
        if (!strobe && newStrobe) {
            shiftReg = state;
        }
        strobe = newStrobe;
        if (strobe) {
            shiftReg = state;
        }
    }
    uint8_t read() {
        uint8_t ret = shiftReg & 1;
        shiftReg >>= 1;
        return ret;
    }
};

// ---------------------------------------------------------------------
//                              CPU
// ---------------------------------------------------------------------
class CPU {
public:
    uint8_t A=0, X=0, Y=0, SP=0xFD;
    // P = NV-BDIZC
    uint8_t P=0x24; 
    uint16_t PC=0xC000;

    uint8_t RAM[2048];
    Cartridge* cart;
    PPU* ppu;
    APU* apu;
    Controller* controller;

    uint8_t read(uint16_t addr) {
        if (addr < 0x2000) {
            return RAM[addr & 0x07FF];
        } else if (addr < 0x4000) {
            return ppu->readRegister(addr);
        } else if (addr == 0x4016) {
            return controller->read();
        } else if (addr == 0x4017) {
            return 0; // second controller not implemented
        } else if (addr < 0x4018) {
            if (addr < 0x4014) {
                return apu->readRegister(addr);
            }
            return 0;
        } else if (addr >= 0x8000) {
            size_t sz = cart->prgROM.size();
            if (sz == 16384) {
                return cart->prgROM[addr & 0x3FFF];
            } else {
                return cart->prgROM[addr & 0x7FFF];
            }
        }
        return 0;
    }

    void write(uint16_t addr, uint8_t val) {
        if (addr < 0x2000) {
            RAM[addr & 0x07FF] = val;
        } else if (addr < 0x4000) {
            ppu->writeRegister(addr, val);
        } else if (addr == 0x4014) {
            // OAM DMA
            uint16_t base = val << 8;
            for (int i = 0; i < 256; i++) {
                ppu->OAM[i] = read(base + i);
            }
        } else if (addr == 0x4016) {
            controller->write(val);
        } else if (addr < 0x4018) {
            apu->writeRegister(addr, val);
        } else {
            // ignore writes to ROM
        }
    }

    void setNZ(uint8_t value) {
        if (value & 0x80) P |= 0x80; else P &= ~0x80;
        if (value == 0)   P |= 0x02; else P &= ~0x02;
    }

    void reset() {
        A=0; X=0; Y=0; P=0x24; SP=0xFD;
        uint8_t lo = read(0xFFFC);
        uint8_t hi = read(0xFFFD);
        PC = makeWord(lo, hi);
    }

    void nmi() {
        push((PC >> 8) & 0xFF);
        push(PC & 0xFF);
        push(P & ~0x10);
        P |= 0x04;
        uint16_t lo = read(0xFFFA);
        uint16_t hi = read(0xFFFB);
        PC = (hi << 8) | lo;
    }

    void irq() {
        if (P & 0x04) return;
        push((PC >> 8) & 0xFF);
        push(PC & 0xFF);
        push(P & ~0x10);
        P |= 0x04;
        uint16_t lo = read(0xFFFE);
        uint16_t hi = read(0xFFFF);
        PC = (hi << 8) | lo;
    }

    void push(uint8_t val) {
        write(0x0100 + SP, val);
        SP--;
    }
    uint8_t pop() {
        SP++;
        return read(0x0100 + SP);
    }

    // Addressing modes
    uint8_t imm() { return read(PC++); }
    uint16_t imm16() { 
        uint8_t lo = read(PC++);
        uint8_t hi = read(PC++);
        return makeWord(lo, hi);
    }
    uint16_t zpg()   { return imm(); }
    uint16_t zpgX()  { return (imm() + X) & 0xFF; }
    uint16_t zpgY()  { return (imm() + Y) & 0xFF; }
    uint16_t abs_()  { return imm16(); }
    uint16_t absX(bool = false) { return abs_() + X; }
    uint16_t absY(bool = false) { return abs_() + Y; }
    uint16_t ind() {
        uint16_t ptr = imm16();
        uint8_t lo = read(ptr);
        uint8_t hi = read((ptr & 0xFF00) | ((ptr+1) & 0x00FF));
        return makeWord(lo, hi);
    }
    uint16_t indX() {
        uint8_t base = imm();
        uint8_t effZp = base + X;
        uint8_t lo = read(effZp & 0xFF);
        uint8_t hi = read((effZp + 1) & 0xFF);
        return makeWord(lo, hi);
    }
    uint16_t indY(bool = false) {
        uint8_t base = imm();
        uint8_t lo = read(base & 0xFF);
        uint8_t hi = read((base+1) & 0xFF);
        return makeWord(lo, hi) + Y;
    }

    void opADC(uint8_t val) {
        uint16_t sum = A + val + (P & 1);
        if (sum > 0xFF) P |= 0x01; else P &= ~0x01;
        A = sum & 0xFF;
        setNZ(A);
        bool overflow = (~(A ^ val) & (A ^ sum) & 0x80) != 0;
        if (overflow) P |= 0x40; else P &= ~0x40;
    }
    void opSBC(uint8_t val) {
        opADC(val ^ 0xFF);
    }
    void opCMP(uint8_t lhs, uint8_t rhs) {
        uint16_t tmp = lhs - rhs;
        if (lhs >= rhs) P |= 0x01; else P &= ~0x01;
        tmp &= 0xFF;
        if (tmp == 0) P |= 0x02; else P &= ~0x02;
        if (tmp & 0x80) P |= 0x80; else P &= ~0x80;
    }

    void step() {
        uint8_t opcode = read(PC++);
        switch (opcode) {
            // LDA
            case 0xA9: { A = imm(); setNZ(A); } break;
            case 0xA5: { A = read(zpg()); setNZ(A); } break;
            case 0xB5: { A = read(zpgX()); setNZ(A); } break;
            case 0xAD: { A = read(abs_()); setNZ(A); } break;
            case 0xBD: { A = read(absX()); setNZ(A); } break;
            case 0xB9: { A = read(absY()); setNZ(A); } break;
            case 0xA1: { A = read(indX()); setNZ(A); } break;
            case 0xB1: { A = read(indY()); setNZ(A); } break;

            // LDX
            case 0xA2: { X = imm(); setNZ(X); } break;
            case 0xA6: { X = read(zpg()); setNZ(X); } break;
            case 0xB6: { X = read(zpgY()); setNZ(X); } break;
            case 0xAE: { X = read(abs_()); setNZ(X); } break;
            case 0xBE: { X = read(absY()); setNZ(X); } break;

            // LDY
            case 0xA0: { Y = imm(); setNZ(Y); } break;
            case 0xA4: { Y = read(zpg()); setNZ(Y); } break;
            case 0xB4: { Y = read(zpgX()); setNZ(Y); } break;
            case 0xAC: { Y = read(abs_()); setNZ(Y); } break;
            case 0xBC: { Y = read(absX()); setNZ(Y); } break;

            // STA
            case 0x85: { write(zpg(), A); } break;
            case 0x95: { write(zpgX(), A); } break;
            case 0x8D: { write(abs_(), A); } break;
            case 0x9D: { write(absX(), A); } break;
            case 0x99: { write(absY(), A); } break;
            case 0x81: { write(indX(), A); } break;
            case 0x91: { write(indY(), A); } break;

            // STX
            case 0x86: { write(zpg(), X); } break;
            case 0x96: { write(zpgY(), X); } break;
            case 0x8E: { write(abs_(), X); } break;

            // STY
            case 0x84: { write(zpg(), Y); } break;
            case 0x94: { write(zpgX(), Y); } break;
            case 0x8C: { write(abs_(), Y); } break;

            // Transfers
            case 0xAA: { X = A; setNZ(X); } break; // TAX
            case 0xA8: { Y = A; setNZ(Y); } break; // TAY
            case 0xBA: { X = SP; setNZ(X); } break; // TSX
            case 0x8A: { A = X; setNZ(A); } break; // TXA
            case 0x98: { A = Y; setNZ(A); } break; // TYA
            case 0x9A: { SP = X; } break;          // TXS

            // INC/DEC
            case 0xE8: { X++; setNZ(X); } break; // INX
            case 0xC8: { Y++; setNZ(Y); } break; // INY
            case 0xCA: { X--; setNZ(X); } break; // DEX
            case 0x88: { Y--; setNZ(Y); } break; // DEY

            // ADC
            case 0x69: { opADC(imm()); } break;
            case 0x65: { opADC(read(zpg())); } break;
            case 0x75: { opADC(read(zpgX())); } break;
            case 0x6D: { opADC(read(abs_())); } break;
            case 0x7D: { opADC(read(absX())); } break;
            case 0x79: { opADC(read(absY())); } break;
            case 0x61: { opADC(read(indX())); } break;
            case 0x71: { opADC(read(indY())); } break;

            // SBC
            case 0xE9: { opSBC(imm()); } break;
            case 0xE5: { opSBC(read(zpg())); } break;
            case 0xF5: { opSBC(read(zpgX())); } break;
            case 0xED: { opSBC(read(abs_())); } break;
            case 0xFD: { opSBC(read(absX())); } break;
            case 0xF9: { opSBC(read(absY())); } break;
            case 0xE1: { opSBC(read(indX())); } break;
            case 0xF1: { opSBC(read(indY())); } break;

            // CMP
            case 0xC9: { opCMP(A, imm()); } break;
            case 0xC5: { opCMP(A, read(zpg())); } break;
            case 0xD5: { opCMP(A, read(zpgX())); } break;
            case 0xCD: { opCMP(A, read(abs_())); } break;
            case 0xDD: { opCMP(A, read(absX())); } break;
            case 0xD9: { opCMP(A, read(absY())); } break;
            case 0xC1: { opCMP(A, read(indX())); } break;
            case 0xD1: { opCMP(A, read(indY())); } break;

            // CPX
            case 0xE0: { opCMP(X, imm()); } break;
            case 0xE4: { opCMP(X, read(zpg())); } break;
            case 0xEC: { opCMP(X, read(abs_())); } break;

            // CPY
            case 0xC0: { opCMP(Y, imm()); } break;
            case 0xC4: { opCMP(Y, read(zpg())); } break;
            case 0xCC: { opCMP(Y, read(abs_())); } break;

            // AND/ORA/EOR
            case 0x29: { A &= imm(); setNZ(A); } break;  // AND
            case 0x09: { A |= imm(); setNZ(A); } break;  // ORA
            case 0x49: { A ^= imm(); setNZ(A); } break;  // EOR

            // ASL A
            case 0x0A: {
                uint8_t c = (A & 0x80) ? 1 : 0;
                A <<= 1;
                if (c) P |= 0x01; else P &= ~0x01;
                setNZ(A);
            } break;
            // LSR A
            case 0x4A: {
                uint8_t c = (A & 0x01);
                A >>= 1;
                if (c) P |= 0x01; else P &= ~0x01;
                setNZ(A);
            } break;
            // ROL A
            case 0x2A: {
                uint8_t c = (P & 0x01);
                uint8_t newC = (A & 0x80) ? 1 : 0;
                A = (A << 1) | c;
                if (newC) P |= 0x01; else P &= ~0x01;
                setNZ(A);
            } break;
            // ROR A
            case 0x6A: {
                uint8_t c = (P & 0x01) << 7;
                uint8_t newC = (A & 0x01);
                A = (A >> 1) | c;
                if (newC) P |= 0x01; else P &= ~0x01;
                setNZ(A);
            } break;

            // JMP
            case 0x4C: { PC = imm16(); } break;
            case 0x6C: { PC = ind(); } break;

            // JSR/RTS
            case 0x20: {
                uint16_t addr = imm16();
                uint16_t ret = PC - 1;
                push((ret >> 8) & 0xFF);
                push(ret & 0xFF);
                PC = addr;
            } break;
            case 0x60: {
                uint8_t lo = pop();
                uint8_t hi = pop();
                PC = makeWord(lo, hi) + 1;
            } break;

            // Branches
            case 0xD0: { // BNE
                int8_t off = (int8_t)imm();
                if (!(P & 0x02)) PC += off;
            } break;
            case 0xF0: { // BEQ
                int8_t off = (int8_t)imm();
                if (P & 0x02) PC += off;
            } break;
            case 0x90: { // BCC
                int8_t off = (int8_t)imm();
                if (!(P & 0x01)) PC += off;
            } break;
            case 0xB0: { // BCS
                int8_t off = (int8_t)imm();
                if (P & 0x01) PC += off;
            } break;
            case 0x10: { // BPL
                int8_t off = (int8_t)imm();
                if (!(P & 0x80)) PC += off;
            } break;
            case 0x30: { // BMI
                int8_t off = (int8_t)imm();
                if (P & 0x80) PC += off;
            } break;
            case 0x50: { // BVC
                int8_t off = (int8_t)imm();
                if (!(P & 0x40)) PC += off;
            } break;
            case 0x70: { // BVS
                int8_t off = (int8_t)imm();
                if (P & 0x40) PC += off;
            } break;

            // BIT
            case 0x24: {
                uint8_t val = read(zpg());
                uint8_t tmp = A & val;
                if ((tmp & 0xFF) == 0) P |= 0x02; else P &= ~0x02;
                P = (P & 0x3F) | (val & 0xC0);
            } break;
            case 0x2C: {
                uint8_t val = read(abs_());
                uint8_t tmp = A & val;
                if ((tmp & 0xFF) == 0) P |= 0x02; else P &= ~0x02;
                P = (P & 0x3F) | (val & 0xC0);
            } break;

            // BRK
            case 0x00: {
                PC++;
                push((PC >> 8) & 0xFF);
                push(PC & 0xFF);
                push(P | 0x10);
                P |= 0x04;
                uint8_t lo = read(0xFFFE);
                uint8_t hi = read(0xFFFF);
                PC = makeWord(lo, hi);
            } break;
            // RTI
            case 0x40: {
                uint8_t flags = pop();
                P = flags;
                uint8_t lo = pop();
                uint8_t hi = pop();
                PC = makeWord(lo, hi);
            } break;

            // NOP or unimplemented
            default: 
                // Do nothing
                break;
        }
    }
};

// ---------------------------------------------------------------------
//                              NES
// ---------------------------------------------------------------------
class NES {
public:
    Cartridge cart;
    CPU cpu;
    PPU ppu;
    APU apu;
    Controller controller;

    bool loadROM(const char* path) {
        if (!cart.load(path)) return false;
        cpu.cart        = &cart;
        cpu.ppu         = &ppu;
        cpu.apu         = &apu;
        cpu.controller  = &controller;
        ppu.chrROM      = &cart.chrROM;
        reset();
        return true;
    }

    void reset() {
        cpu.reset();
    }

    void runFrame() {
        // Naive approach: step CPU a bunch, then do a single PPU render
        for (uint32_t i = 0; i < MASTER_CYCLES_PER_FRAME; i++) {
            cpu.step();
            apu.step();
        }

        // Trigger NMI if enabled
        if (ppu.PPUCTRL & 0x80) {
            cpu.nmi();
        }
        // Render once at end of frame
        ppu.render();
    }
};

// ---------------------------------------------------------------------
//                              MAIN
// ---------------------------------------------------------------------
int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cout << "Usage: " << argv[0] << " ROM\n";
        return 1;
    }

    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_EVENTS | SDL_INIT_AUDIO) < 0) {
        std::cerr << "Failed to initialize SDL: " << SDL_GetError() << std::endl;
        return 1;
    }

    SDL_Window* window = SDL_CreateWindow("Vibe NES Emulator",
                                          SDL_WINDOWPOS_CENTERED,
                                          SDL_WINDOWPOS_CENTERED,
                                          SCREEN_WIDTH * 2,
                                          SCREEN_HEIGHT * 2,
                                          SDL_WINDOW_SHOWN);
    if (!window) {
        std::cerr << "Failed to create window: " << SDL_GetError() << std::endl;
        SDL_Quit();
        return 1;
    }

    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    if (!renderer) {
        std::cerr << "Failed to create renderer: " << SDL_GetError() << std::endl;
        SDL_DestroyWindow(window);
        SDL_Quit();
        return 1;
    }

    SDL_Texture* texture = SDL_CreateTexture(renderer,
                                             SDL_PIXELFORMAT_ARGB8888,
                                             SDL_TEXTUREACCESS_STREAMING,
                                             SCREEN_WIDTH,
                                             SCREEN_HEIGHT);
    if (!texture) {
        std::cerr << "Failed to create texture: " << SDL_GetError() << std::endl;
        SDL_DestroyRenderer(renderer);
        SDL_DestroyWindow(window);
        SDL_Quit();
        return 1;
    }

    NES nes;
    if (!nes.loadROM(argv[1])) {
        std::cerr << "Failed to load ROM.\n";
        return 1;
    }

    bool running = true;
    SDL_Event e;

    // VIBE MODE toggle
    bool vibeMode = false;

    const int FPS = 60;
    const int frameDelay = 1000 / FPS;
    Uint32 frameStart;
    int frameTime;

    while (running) {
        frameStart = SDL_GetTicks();

        while (SDL_PollEvent(&e)) {
            if (e.type == SDL_QUIT) {
                running = false;
            } else if (e.type == SDL_KEYDOWN) {
                if (e.key.keysym.sym == SDLK_ESCAPE) {
                    running = false;
                }
                // NES Controller mapping
                switch (e.key.keysym.sym) {
                    case SDLK_z:     nes.controller.state |= 0x80; break; // A
                    case SDLK_x:     nes.controller.state |= 0x40; break; // B
                    case SDLK_SPACE: nes.controller.state |= 0x20; break; // Select
                    case SDLK_RETURN:nes.controller.state |= 0x10; break; // Start
                    case SDLK_UP:    nes.controller.state |= 0x08; break;
                    case SDLK_DOWN:  nes.controller.state |= 0x04; break;
                    case SDLK_LEFT:  nes.controller.state |= 0x02; break;
                    case SDLK_RIGHT: nes.controller.state |= 0x01; break;
                    // Toggle vibe mode
                    case SDLK_v:
                        vibeMode = !vibeMode;
                        std::cout << (vibeMode ? "[VIBE MODE ON]\n" : "[VIBE MODE OFF]\n");
                        break;
                }
            } else if (e.type == SDL_KEYUP) {
                switch (e.key.keysym.sym) {
                    case SDLK_z:     nes.controller.state &= ~0x80; break;
                    case SDLK_x:     nes.controller.state &= ~0x40; break;
                    case SDLK_SPACE: nes.controller.state &= ~0x20; break;
                    case SDLK_RETURN:nes.controller.state &= ~0x10; break;
                    case SDLK_UP:    nes.controller.state &= ~0x08; break;
                    case SDLK_DOWN:  nes.controller.state &= ~0x04; break;
                    case SDLK_LEFT:  nes.controller.state &= ~0x02; break;
                    case SDLK_RIGHT: nes.controller.state &= ~0x01; break;
                }
            }
        }

        // Run 1 frame
        nes.runFrame();

        // If vibeMode is on, swirl colors in the framebuffer
        if (vibeMode) {
            for (int i = 0; i < SCREEN_WIDTH * SCREEN_HEIGHT; i++) {
                uint32_t pix = nes.ppu.framebuffer[i];
                // ARGB
                uint8_t a = (pix >> 24) & 0xFF; // always 0xFF
                uint8_t r = (pix >> 16) & 0xFF;
                uint8_t g = (pix >>  8) & 0xFF;
                uint8_t b = (pix >>  0) & 0xFF;
                // Channel rotation: R->G, G->B, B->R
                uint8_t nr = g;
                uint8_t ng = b;
                uint8_t nb = r;
                nes.ppu.framebuffer[i] = (a << 24) | (nr << 16) | (ng << 8) | nb;
            }
        }

        // Update texture
        SDL_UpdateTexture(texture, nullptr, nes.ppu.framebuffer, SCREEN_WIDTH * sizeof(uint32_t));
        // Render
        SDL_RenderClear(renderer);
        SDL_RenderCopy(renderer, texture, nullptr, nullptr);
        SDL_RenderPresent(renderer);

        frameTime = SDL_GetTicks() - frameStart;
        if (frameDelay > frameTime) {
            SDL_Delay(frameDelay - frameTime);
        }
    }

    SDL_DestroyTexture(texture);
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 0;
}
