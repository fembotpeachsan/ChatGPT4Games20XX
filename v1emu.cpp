/********************************************************************
 *  Simplified Full-Blown NES Emulator Example (Single-File)
 *  ---------------------------------------------------------
 *  NOTE: This code is still incomplete for a production-level
 *  emulator. It illustrates how you might expand your skeleton.
 *  It’s not cycle-accurate, nor does it handle all mappers, APU, or
 *  PPU details. However, it includes:
 *    - A 6502 CPU with an opcode switch for many opcodes.
 *    - Basic memory mapping and PPU register simulation.
 *    - Primitive nametable rendering, ignoring many edge cases.
 *    - Simple sprite rendering logic.
 *    - APU stubs so the CPU doesn’t break (no real audio).
 *    - SDL input for a standard NES controller.
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

// We do a simplified approach: run ~29781 CPU "steps" each frame (roughly).
// A more accurate approach would tie CPU cycles to PPU cycles, etc.

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

    // For this example, we’ll only handle NROM (Mapper 0) style:
    //   - no bank switching
    //   - 16KB or 32KB PRG ROM
    //   - 8KB CHR ROM or CHR RAM
    // In real NES land, there are ~100+ mappers, each with special memory logic.
    bool load(const char* path) {
        std::ifstream rom(path, std::ios::binary);
        if (!rom.good()) {
            std::cerr << "Could not open ROM file.\n";
            return false;
        }
        // Read header
        char header[16];
        rom.read(header, 16);
        if (strncmp(header, "NES\x1A", 4) != 0) {
            std::cerr << "Not a valid iNES ROM.\n";
            return false;
        }

        // iNES format
        uint8_t prgCount = static_cast<uint8_t>(header[4]);
        uint8_t chrCount = static_cast<uint8_t>(header[5]);
        // There are flags in header[6..7], we’ll skip detailed parsing for now.
        size_t prgSize = prgCount * 16384;
        size_t chrSize = chrCount * 8192;

        // Check for trainer
        bool trainerPresent = header[6] & 0x04;
        if (trainerPresent) {
            // skip 512 bytes of trainer
            rom.seekg(512, std::ios_base::cur);
        }

        // Read PRG
        prgROM.resize(prgSize);
        rom.read(reinterpret_cast<char*>(prgROM.data()), prgSize);

        // Read CHR
        if (chrSize > 0) {
            chrROM.resize(chrSize);
            rom.read(reinterpret_cast<char*>(chrROM.data()), chrSize);
        } else {
            // If CHR size = 0, we have CHR RAM instead (8KB by default).
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
//                        PPU
// ---------------------------------------------------------------------
class PPU {
public:
    // Framebuffer (ARGB) that we render to the screen
    uint32_t framebuffer[SCREEN_WIDTH * SCREEN_HEIGHT];

    // 2KB internal VRAM for nametables in a simplified NROM (2 nametables mirrored).
    uint8_t nametable[2048];

    // 256 bytes OAM (sprite) memory
    uint8_t OAM[256];

    // Registers
    // We’ll store the “PPU registers” in these fields. Real PPU has 8 registers
    // but we’ll only track enough to do some basic rendering.
    uint8_t PPUCTRL   = 0;
    uint8_t PPUMASK   = 0;
    uint8_t PPUSTATUS = 0;
    uint8_t OAMADDR   = 0;
    uint8_t OAMDATA   = 0;
    uint8_t PPUSCROLL = 0;
    uint8_t PPUADDR   = 0;
    uint8_t PPUDATA   = 0;

    // The address latch for $2005/$2006 (scroll/fake for demonstration)
    bool    latch       = false;
    uint16_t vramAddr   = 0;     // Current VRAM address
    uint16_t tempAddr   = 0;     // Temporary VRAM address (for scrolling)
    uint8_t  fineX      = 0;

    // Pointer to CHR ROM (or CHR RAM) from the cartridge
    std::vector<uint8_t>* chrROM;

    PPU() {
        // Clear the framebuffer and nametable
        memset(framebuffer, 0, sizeof(framebuffer));
        memset(nametable, 0, sizeof(nametable));
        memset(OAM, 0, sizeof(OAM));
    }

    void writeRegister(uint16_t addr, uint8_t val) {
        switch (addr & 7) {
            case 0: // PPUCTRL ($2000)
                PPUCTRL = val;
                // Our simplified example: if PPUCTRL bit 7 = 1, generate NMI on VBlank
                break;
            case 1: // PPUMASK ($2001)
                PPUMASK = val;
                break;
            case 2: // PPUSTATUS ($2002) - read-only in real hardware
                // writes here do nothing in real hardware
                break;
            case 3: // OAMADDR ($2003)
                OAMADDR = val;
                break;
            case 4: // OAMDATA ($2004)
                OAM[OAMADDR++] = val;
                break;
            case 5: // PPUSCROLL ($2005)
                if (!latch) {
                    // first write
                    // We store coarse X in tempAddr
                    tempAddr = (tempAddr & 0xFFE0) | (val >> 3);
                    fineX = val & 0x07;
                    latch = true;
                } else {
                    // second write
                    // We store coarse Y in tempAddr
                    tempAddr = (tempAddr & 0x8FFF) | ((val & 0x07) << 12);
                    tempAddr = (tempAddr & 0xFC1F) | ((val & 0xF8) << 2);
                    latch = false;
                }
                break;
            case 6: // PPUADDR ($2006)
                if (!latch) {
                    tempAddr = (tempAddr & 0x00FF) | ((val & 0x3F) << 8);
                    latch = true;
                } else {
                    tempAddr = (tempAddr & 0xFF00) | val;
                    vramAddr = tempAddr;
                    latch = false;
                }
                break;
            case 7: // PPUDATA ($2007)
                writeVRAM(vramAddr, val);
                // Increment vramAddr by either 1 or 32 depending on PPUCTRL bit 2
                if (PPUCTRL & 0x04) vramAddr += 32; else vramAddr += 1;
                break;
        }
    }

    uint8_t readRegister(uint16_t addr) {
        uint8_t data = 0;
        switch (addr & 7) {
            case 2: // PPUSTATUS ($2002)
                // Return the PPUSTATUS, then clear the latch
                data = PPUSTATUS;
                // Clear vblank flag
                PPUSTATUS &= 0x7F;
                latch = false;
                break;
            case 4: // OAMDATA ($2004)
                data = OAM[OAMADDR];
                break;
            case 7: // PPUDATA ($2007)
                data = readVRAM(vramAddr);
                // Increment vramAddr
                if (PPUCTRL & 0x04) vramAddr += 32; else vramAddr += 1;
                break;
            default:
                // Not typically readable or no effect
                break;
        }
        return data;
    }

    void writeVRAM(uint16_t addr, uint8_t val) {
        addr &= 0x3FFF;
        if (addr < 0x2000) {
            // CHR RAM if present, or do nothing if read-only CHR
            if (chrROM->size() > addr) {
                (*chrROM)[addr] = val; // only works if we have CHR RAM
            }
        } else if (addr < 0x3F00) {
            // Nametable
            nametable[addr & 0x07FF] = val;
        } else {
            // Palette - ignoring details
            // Could store in a palette array. Here we do nothing special.
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
            // Palette
            return 0;
        }
    }

    // --- Simplified background rendering function ---
    // This function reads the nametable, fetches pattern data from CHR,
    // and draws the background. We ignore attribute tables, scrolling, etc.
    // Perfect for demonstration.
    void renderBackground() {
        // For demonstration, read from nametable 0 (0x2000-0x23FF).
        uint16_t baseNametableAddr = 0x2000;
        for (int row = 0; row < 30; row++) {
            for (int col = 0; col < 32; col++) {
                uint16_t ntAddr = baseNametableAddr + row * 32 + col;
                uint8_t tileIndex = nametable[ntAddr & 0x07FF];
                // Each tile is 8x8, from pattern table 0 or 1?
                // We check PPUCTRL bit 4 for background pattern table
                uint16_t patternAddr = ((PPUCTRL & 0x10) ? 0x1000 : 0x0000) + (tileIndex * 16);
                // For each row in tile
                for (int fineY = 0; fineY < 8; fineY++) {
                    uint8_t lowByte  = readVRAM(patternAddr + fineY);
                    uint8_t highByte = readVRAM(patternAddr + fineY + 8);
                    for (int fineX = 0; fineX < 8; fineX++) {
                        int bit = 7 - fineX;
                        uint8_t paletteIndex = ((lowByte  >> bit) & 1) | (((highByte >> bit) & 1) << 1);
                        // We’ll pick a color. Real NES uses palette at 0x3F00 + ...
                        uint32_t color;
                        switch (paletteIndex) {
                            case 0: color = 0xFF606060; break; // Gray
                            case 1: color = 0xFFFF0000; break; // Red
                            case 2: color = 0xFF00FF00; break; // Green
                            case 3: color = 0xFF0000FF; break; // Blue
                        }
                        int screenX = col * 8 + fineX;
                        int screenY = row * 8 + fineY;
                        if (screenX < SCREEN_WIDTH && screenY < SCREEN_HEIGHT) {
                            framebuffer[screenY * SCREEN_WIDTH + screenX] = color;
                        }
                    }
                }
            }
        }
    }

    // Very simplified sprite rendering
    void renderSprites() {
        // Each sprite takes 4 bytes in OAM:
        // [0] = Y position
        // [1] = tile index
        // [2] = attributes
        // [3] = X position
        for (int i = 0; i < 64; i++) {
            uint8_t y       = OAM[i * 4 + 0];
            uint8_t tile    = OAM[i * 4 + 1];
            uint8_t attr    = OAM[i * 4 + 2];
            uint8_t x       = OAM[i * 4 + 3];
            bool flipH      = (attr & 0x40) != 0;
            bool flipV      = (attr & 0x80) != 0;
            uint16_t patternAddr = ((PPUCTRL & 0x08) ? 0x1000 : 0x0000) + (tile * 16);

            for (int row = 0; row < 8; row++) {
                int actualRow = flipV ? (7 - row) : row;
                uint8_t lowByte  = readVRAM(patternAddr + actualRow);
                uint8_t highByte = readVRAM(patternAddr + actualRow + 8);
                for (int col = 0; col < 8; col++) {
                    int bit = flipH ? col : (7 - col);
                    uint8_t paletteIndex = ((lowByte  >> bit) & 1) | (((highByte >> bit) & 1) << 1);
                    if (paletteIndex == 0) {
                        // Transparent
                        continue;
                    }
                    uint32_t color;
                    switch (paletteIndex) {
                        case 1: color = 0xFFFFFF00; break; // Yellow
                        case 2: color = 0xFFFF00FF; break; // Magenta
                        case 3: color = 0xFF00FFFF; break; // Cyan
                        default: color = 0xFFFFFFFF; break;
                    }
                    int px = x + col;
                    int py = y + row;
                    if (px < SCREEN_WIDTH && py < SCREEN_HEIGHT) {
                        // Overwrite background color
                        framebuffer[py * SCREEN_WIDTH + px] = color;
                    }
                }
            }
        }
    }

    void render() {
        // If background rendering is enabled (PPUMASK bit 3)
        if (PPUMASK & 0x08) {
            renderBackground();
        } else {
            // fill black
            for (int i = 0; i < SCREEN_WIDTH * SCREEN_HEIGHT; i++) {
                framebuffer[i] = 0xFF000000;
            }
        }

        // If sprite rendering is enabled (PPUMASK bit 4)
        if (PPUMASK & 0x10) {
            renderSprites();
        }
    }
};

// ---------------------------------------------------------------------
//                              APU
// ---------------------------------------------------------------------
// For demonstration, we’ll only stub out the APU register writes and
// do nothing else. Real NES APU is quite involved.
class APU {
public:
    void writeRegister(uint16_t addr, uint8_t val) {
        // stub
        (void)addr; (void)val;
    }
    uint8_t readRegister(uint16_t addr) {
        // stub
        (void)addr;
        return 0;
    }
    void step() {
        // stub: in a real APU, we’d generate audio samples here
    }
};

// ---------------------------------------------------------------------
//                       INPUT (Controller)
// ---------------------------------------------------------------------
class Controller {
public:
    // Typical NES controller bits:
    // 7 6 5 4 3 2 1 0
    // A B Select Start Up Down Left Right
    // We store the latched state here.
    uint8_t state     = 0;
    uint8_t shiftReg  = 0;
    bool strobe       = false;

    // Write to controller port (4016)
    void write(uint8_t val) {
        // If bit 0 of val is set, we strobe
        bool newStrobe = (val & 1) != 0;
        if (!strobe && newStrobe) {
            // Latch the current state into shiftReg
            shiftReg = state;
        }
        strobe = newStrobe;
        if (strobe) {
            // Continually load the shiftReg
            shiftReg = state;
        }
    }
    // Read from controller port (4016)
    uint8_t read() {
        // Return the lowest bit of shiftReg, then shift right
        uint8_t ret = shiftReg & 1;
        shiftReg >>= 1;
        return ret;
    }
};

// ---------------------------------------------------------------------
//                            CPU
// ---------------------------------------------------------------------
class CPU {
public:
    // Registers
    uint8_t  A=0, X=0, Y=0, SP=0xFD;
    // P = NV-BDIZC
    //   N=128, V=64, B=16, D=8, I=4, Z=2, C=1
    uint8_t  P=0x24; // default

    uint16_t PC=0xC000;

    // CPU internal RAM (2KB)
    uint8_t RAM[2048];

    // Pointers to external devices
    Cartridge* cart;
    PPU*       ppu;
    APU*       apu;
    Controller* controller;

    // For memory reads/writes
    uint8_t read(uint16_t addr) {
        // Basic memory map for NROM
        if (addr < 0x2000) {
            return RAM[addr & 0x07FF]; // 2KB mirrored
        } else if (addr < 0x4000) {
            // PPU registers, mirrored every 8 bytes up to 0x3FFF
            return ppu->readRegister(addr);
        } else if (addr == 0x4016) {
            // Controller 1
            return controller->read();
        } else if (addr == 0x4017) {
            // Controller 2 stub
            return 0;
        } else if (addr < 0x4018) {
            // APU or I/O
            if (addr < 0x4014) {
                // Some APU register reads
                return apu->readRegister(addr);
            }
            // OAM DMA register or so. Simplify by ignoring for reads.
            return 0;
        } else if (addr >= 0x8000) {
            // PRG ROM
            // If 16KB, mirror at 0xC000
            size_t sz = cart->prgROM.size();
            if (sz == 16384) {
                // mirrored
                return cart->prgROM[addr & 0x3FFF];
            } else {
                // 32KB
                return cart->prgROM[addr & 0x7FFF];
            }
        }
        return 0;
    }

    void write(uint16_t addr, uint8_t val) {
        if (addr < 0x2000) {
            RAM[addr & 0x07FF] = val;
        } else if (addr < 0x4000) {
            // PPU registers
            ppu->writeRegister(addr, val);
        } else if (addr == 0x4014) {
            // OAM DMA
            // 0x4014 is the high byte of the source address in CPU page
            uint16_t base = val << 8;
            for (int i = 0; i < 256; i++) {
                ppu->OAM[i] = read(base + i);
            }
        } else if (addr == 0x4016) {
            // Controller strobe
            controller->write(val);
        } else if (addr < 0x4018) {
            // APU registers
            apu->writeRegister(addr, val);
        } else if (addr >= 0x8000) {
            // Some cartridges have RAM in 0x6000-0x7FFF or even in PRG area if
            // they use special mappers, but for NROM, we ignore writes to PRG.
        }
    }

    // Flag helpers
    void setNZ(uint8_t value) {
        // Set N if bit 7 is set
        if (value & 0x80) P |= 0x80; else P &= ~0x80;
        // Set Z if value == 0
        if (value == 0) P |= 0x02; else P &= ~0x02;
    }

    // CPU reset
    void reset() {
        // Clear regs
        A=0; X=0; Y=0; P=0x24; SP=0xFD;
        // Read reset vector at 0xFFFC
        uint8_t lo = read(0xFFFC);
        uint8_t hi = read(0xFFFD);
        PC = makeWord(lo, hi);
    }

    // NMI handling
    void nmi() {
        // Push PC high, PC low, then P
        push((PC >> 8) & 0xFF);
        push(PC & 0xFF);
        // Clear bit 4 (B) but set bit 5 (unofficial "bit 5" usage), also clear bit 2 (I=1)
        push(P & ~0x10);
        P |= 0x04; // set I=1
        // Jump to NMI vector at 0xFFFA
        uint16_t lo = read(0xFFFA);
        uint16_t hi = read(0xFFFB);
        PC = (hi << 8) | lo;
    }

    // IRQ handling
    void irq() {
        if (P & 0x04) return; // if I=1, ignore
        push((PC >> 8) & 0xFF);
        push(PC & 0xFF);
        push(P & ~0x10);
        P |= 0x04;
        uint16_t lo = read(0xFFFE);
        uint16_t hi = read(0xFFFF);
        PC = (hi << 8) | lo;
    }

    // Stack push/pop
    void push(uint8_t val) {
        write(0x0100 + SP, val);
        SP--;
    }
    uint8_t pop() {
        SP++;
        return read(0x0100 + SP);
    }

    // Addressing modes
    uint8_t imm() {
        return read(PC++);
    }
    uint16_t imm16() {
        uint8_t lo = read(PC++);
        uint8_t hi = read(PC++);
        return makeWord(lo, hi);
    }
    uint16_t zpg() {
        return imm();
    }
    uint16_t zpgX() {
        return (imm() + X) & 0xFF;
    }
    uint16_t zpgY() {
        return (imm() + Y) & 0xFF;
    }
    uint16_t abs_() {
        return imm16();
    }
    uint16_t absX(bool checkPageBoundary = false) {
        uint16_t base = imm16();
        uint16_t addr = base + X;
        // For read instructions, we might do something with page crossing,
        // but we’ll skip for simplicity.
        return addr;
    }
    uint16_t absY(bool checkPageBoundary = false) {
        uint16_t base = imm16();
        uint16_t addr = base + Y;
        return addr;
    }
    uint16_t ind() {
        // Indirect JMP bug if low byte is 0xFF
        uint16_t ptr = imm16();
        uint8_t lo = read(ptr);
        uint8_t hi = read((ptr & 0xFF00) | ((ptr+1) & 0x00FF));
        return makeWord(lo, hi);
    }
    uint16_t indX() {
        // (zp + X)
        uint8_t base = imm();
        uint8_t effZp = base + X;
        uint8_t lo = read(effZp & 0xFF);
        uint8_t hi = read((effZp+1) & 0xFF);
        return makeWord(lo, hi);
    }
    uint16_t indY(bool checkPageBoundary = false) {
        // (zp), Y
        uint8_t base = imm();
        uint8_t lo = read(base & 0xFF);
        uint8_t hi = read((base+1) & 0xFF);
        uint16_t addr = makeWord(lo, hi) + Y;
        return addr;
    }

    // ADC, SBC helpers
    void opADC(uint8_t val) {
        uint16_t sum = A + val + (P & 0x01);
        // set or clear carry
        if (sum > 0xFF) P |= 0x01; else P &= ~0x01;
        // set or clear zero, negative
        A = sum & 0xFF;
        setNZ(A);
        // Overflow check
        // If bit 7 changes from the sum unexpectedly, set V
        bool overflow = (~(A ^ val) & (A ^ sum) & 0x80) != 0;
        if (overflow) P |= 0x40; else P &= ~0x40;
    }
    void opSBC(uint8_t val) {
        opADC(val ^ 0xFF); // Trick: SBC = ADC of one’s complement
    }

    // CMP
    void opCMP(uint8_t lhs, uint8_t rhs) {
        uint16_t tmp = lhs - rhs;
        // carry set if lhs >= rhs
        if (lhs >= rhs) P |= 0x01; else P &= ~0x01;
        // zero if equal
        tmp &= 0xFF;
        if ((tmp & 0xFF) == 0) P |= 0x02; else P &= ~0x02;
        // negative if bit 7 set
        if (tmp & 0x80) P |= 0x80; else P &= ~0x80;
    }

    // The main “step” function: fetch/decode/execute one instruction
    void step() {
        uint8_t opcode = read(PC++);
        switch (opcode) {
            // LDA
            case 0xA9: { // imm
                A = imm();
                setNZ(A);
            } break;
            case 0xA5: { // zpg
                A = read(zpg());
                setNZ(A);
            } break;
            case 0xB5: { // zpg,X
                A = read(zpgX());
                setNZ(A);
            } break;
            case 0xAD: { // abs
                A = read(abs_());
                setNZ(A);
            } break;
            case 0xBD: { // abs,X
                A = read(absX());
                setNZ(A);
            } break;
            case 0xB9: { // abs,Y
                A = read(absY());
                setNZ(A);
            } break;
            case 0xA1: { // (ind,X)
                A = read(indX());
                setNZ(A);
            } break;
            case 0xB1: { // (ind),Y
                A = read(indY());
                setNZ(A);
            } break;

            // LDX
            case 0xA2: {
                X = imm();
                setNZ(X);
            } break;
            case 0xA6: {
                X = read(zpg());
                setNZ(X);
            } break;
            case 0xB6: {
                X = read(zpgY());
                setNZ(X);
            } break;
            case 0xAE: {
                X = read(abs_());
                setNZ(X);
            } break;
            case 0xBE: {
                X = read(absY());
                setNZ(X);
            } break;

            // LDY
            case 0xA0: {
                Y = imm();
                setNZ(Y);
            } break;
            case 0xA4: {
                Y = read(zpg());
                setNZ(Y);
            } break;
            case 0xB4: {
                Y = read(zpgX());
                setNZ(Y);
            } break;
            case 0xAC: {
                Y = read(abs_());
                setNZ(Y);
            } break;
            case 0xBC: {
                Y = read(absX());
                setNZ(Y);
            } break;

            // STA
            case 0x85: {
                write(zpg(), A);
            } break;
            case 0x95: {
                write(zpgX(), A);
            } break;
            case 0x8D: {
                write(abs_(), A);
            } break;
            case 0x9D: {
                write(absX(), A);
            } break;
            case 0x99: {
                write(absY(), A);
            } break;
            case 0x81: {
                write(indX(), A);
            } break;
            case 0x91: {
                write(indY(), A);
            } break;

            // STX
            case 0x86: {
                write(zpg(), X);
            } break;
            case 0x96: {
                write(zpgY(), X);
            } break;
            case 0x8E: {
                write(abs_(), X);
            } break;

            // STY
            case 0x84: {
                write(zpg(), Y);
            } break;
            case 0x94: {
                write(zpgX(), Y);
            } break;
            case 0x8C: {
                write(abs_(), Y);
            } break;

            // TAX
            case 0xAA: {
                X = A;
                setNZ(X);
            } break;
            // TAY
            case 0xA8: {
                Y = A;
                setNZ(Y);
            } break;
            // TSX
            case 0xBA: {
                X = SP;
                setNZ(X);
            } break;
            // TXA
            case 0x8A: {
                A = X;
                setNZ(A);
            } break;
            // TYA
            case 0x98: {
                A = Y;
                setNZ(A);
            } break;
            // TXS
            case 0x9A: {
                SP = X;
            } break;

            // INX
            case 0xE8: {
                X++;
                setNZ(X);
            } break;
            // INY
            case 0xC8: {
                Y++;
                setNZ(Y);
            } break;
            // DEX
            case 0xCA: {
                X--;
                setNZ(X);
            } break;
            // DEY
            case 0x88: {
                Y--;
                setNZ(Y);
            } break;

            // ADC
            case 0x69: {
                opADC(imm());
            } break;
            case 0x65: {
                opADC(read(zpg()));
            } break;
            case 0x75: {
                opADC(read(zpgX()));
            } break;
            case 0x6D: {
                opADC(read(abs_()));
            } break;
            case 0x7D: {
                opADC(read(absX()));
            } break;
            case 0x79: {
                opADC(read(absY()));
            } break;
            case 0x61: {
                opADC(read(indX()));
            } break;
            case 0x71: {
                opADC(read(indY()));
            } break;

            // SBC
            case 0xE9: {
                opSBC(imm());
            } break;
            case 0xE5: {
                opSBC(read(zpg()));
            } break;
            case 0xF5: {
                opSBC(read(zpgX()));
            } break;
            case 0xED: {
                opSBC(read(abs_()));
            } break;
            case 0xFD: {
                opSBC(read(absX()));
            } break;
            case 0xF9: {
                opSBC(read(absY()));
            } break;
            case 0xE1: {
                opSBC(read(indX()));
            } break;
            case 0xF1: {
                opSBC(read(indY()));
            } break;

            // CMP
            case 0xC9: {
                uint8_t val = imm();
                opCMP(A, val);
            } break;
            case 0xC5: {
                opCMP(A, read(zpg()));
            } break;
            case 0xD5: {
                opCMP(A, read(zpgX()));
            } break;
            case 0xCD: {
                opCMP(A, read(abs_()));
            } break;
            case 0xDD: {
                opCMP(A, read(absX()));
            } break;
            case 0xD9: {
                opCMP(A, read(absY()));
            } break;
            case 0xC1: {
                opCMP(A, read(indX()));
            } break;
            case 0xD1: {
                opCMP(A, read(indY()));
            } break;

            // CPX
            case 0xE0: {
                uint8_t val = imm();
                opCMP(X, val);
            } break;
            case 0xE4: {
                opCMP(X, read(zpg()));
            } break;
            case 0xEC: {
                opCMP(X, read(abs_()));
            } break;

            // CPY
            case 0xC0: {
                uint8_t val = imm();
                opCMP(Y, val);
            } break;
            case 0xC4: {
                opCMP(Y, read(zpg()));
            } break;
            case 0xCC: {
                opCMP(Y, read(abs_()));
            } break;

            // AND
            case 0x29: {
                A &= imm();
                setNZ(A);
            } break;

            // ORA
            case 0x09: {
                A |= imm();
                setNZ(A);
            } break;

            // EOR
            case 0x49: {
                A ^= imm();
                setNZ(A);
            } break;

            // ASL A
            case 0x0A: {
                uint8_t c = (A & 0x80) ? 1 : 0;
                A <<= 1;
                if (c) P |= 0x01; else P &= ~0x01;
                setNZ(A);
            } break;

            // LSR A
            case 0x4A: {
                uint8_t c = (A & 0x01) ? 1 : 0;
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

            // JMP abs
            case 0x4C: {
                PC = imm16();
            } break;
            // JMP (ind)
            case 0x6C: {
                PC = ind();
            } break;

            // JSR
            case 0x20: {
                uint16_t addr = imm16();
                // Push PC-1
                uint16_t ret = PC - 1;
                push((ret >> 8) & 0xFF);
                push(ret & 0xFF);
                PC = addr;
            } break;
            // RTS
            case 0x60: {
                uint8_t lo = pop();
                uint8_t hi = pop();
                PC = makeWord(lo, hi) + 1;
            } break;

            // BNE
            case 0xD0: {
                int8_t offset = (int8_t)imm();
                if (!(P & 0x02)) { // Z=0 -> jump
                    PC += offset;
                }
            } break;
            // BEQ
            case 0xF0: {
                int8_t offset = (int8_t)imm();
                if (P & 0x02) {
                    PC += offset;
                }
            } break;
            // BCC
            case 0x90: {
                int8_t offset = (int8_t)imm();
                if (!(P & 0x01)) {
                    PC += offset;
                }
            } break;
            // BCS
            case 0xB0: {
                int8_t offset = (int8_t)imm();
                if (P & 0x01) {
                    PC += offset;
                }
            } break;
            // BPL
            case 0x10: {
                int8_t offset = (int8_t)imm();
                if (!(P & 0x80)) {
                    PC += offset;
                }
            } break;
            // BMI
            case 0x30: {
                int8_t offset = (int8_t)imm();
                if (P & 0x80) {
                    PC += offset;
                }
            } break;
            // BVC
            case 0x50: {
                int8_t offset = (int8_t)imm();
                if (!(P & 0x40)) {
                    PC += offset;
                }
            } break;
            // BVS
            case 0x70: {
                int8_t offset = (int8_t)imm();
                if (P & 0x40) {
                    PC += offset;
                }
            } break;

            // BIT
            case 0x24: {
                uint8_t val = read(zpg());
                uint8_t tmp = A & val;
                if ((tmp & 0x00FF) == 0) P |= 0x02; else P &= ~0x02;
                // bit 7 -> N, bit 6 -> V
                P = (P & 0x3F) | (val & 0xC0);
            } break;
            case 0x2C: {
                uint8_t val = read(abs_());
                uint8_t tmp = A & val;
                if ((tmp & 0x00FF) == 0) P |= 0x02; else P &= ~0x02;
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
                // many opcodes left out for brevity
                break;
        }
    }
};

// ---------------------------------------------------------------------
//                            NES
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
        // Hook them up
        cpu.cart = &cart;
        cpu.ppu = &ppu;
        cpu.apu = &apu;
        cpu.controller = &controller;

        ppu.chrROM = &cart.chrROM;
        reset();
        return true;
    }

    void reset() {
        cpu.reset();
    }

    void runFrame() {
        // In a naive approach, we just run a bunch of CPU instructions,
        // then do a single PPU render. In a real emulator, CPU and PPU run
        // concurrently, interleaving cycle by cycle.
        for (uint32_t i = 0; i < MASTER_CYCLES_PER_FRAME; i++) {
            cpu.step();
            // APU step (stub)
            apu.step();
        }

        // Check for NMI at VBlank (if PPUCTRL bit 7 = 1).
        // Our simplified approach: we always trigger NMI at the end of the frame,
        // if the bit is set in PPUCTRL.
        if (ppu.PPUCTRL & 0x80) {
            cpu.nmi();
        }

        // Render the frame
        ppu.render();
    }
};

// ---------------------------------------------------------------------
//                            MAIN
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
    const int FPS = 60;
    const int frameDelay = 1000 / FPS;
    Uint32 frameStart;
    int frameTime;

    while (running) {
        frameStart = SDL_GetTicks();

        // Poll events
        while (SDL_PollEvent(&e)) {
            if (e.type == SDL_QUIT) {
                running = false;
            } else if (e.type == SDL_KEYDOWN) {
                if (e.key.keysym.sym == SDLK_ESCAPE) {
                    running = false;
                }
                // Basic controller mapping:
                // A B Select Start Up Down Left Right
                // 7 6   5     4     3   2    1    0
                // Let’s do a rough mapping to keyboard:
                // [Z]=A, [X]=B, [SPACE]=Select, [RETURN]=Start
                // [Up/Down/Left/Right]
                switch (e.key.keysym.sym) {
                    case SDLK_z:     nes.controller.state |= 0x80; break; // A
                    case SDLK_x:     nes.controller.state |= 0x40; break; // B
                    case SDLK_SPACE: nes.controller.state |= 0x20; break; // Select
                    case SDLK_RETURN:nes.controller.state |= 0x10; break; // Start
                    case SDLK_UP:    nes.controller.state |= 0x08; break;
                    case SDLK_DOWN:  nes.controller.state |= 0x04; break;
                    case SDLK_LEFT:  nes.controller.state |= 0x02; break;
                    case SDLK_RIGHT: nes.controller.state |= 0x01; break;
                    default: break;
                }
            } else if (e.type == SDL_KEYUP) {
                switch (e.key.keysym.sym) {
                    case SDLK_z:     nes.controller.state &= ~0x80; break; // A
                    case SDLK_x:     nes.controller.state &= ~0x40; break; // B
                    case SDLK_SPACE: nes.controller.state &= ~0x20; break; // Select
                    case SDLK_RETURN:nes.controller.state &= ~0x10; break; // Start
                    case SDLK_UP:    nes.controller.state &= ~0x08; break;
                    case SDLK_DOWN:  nes.controller.state &= ~0x04; break;
                    case SDLK_LEFT:  nes.controller.state &= ~0x02; break;
                    case SDLK_RIGHT: nes.controller.state &= ~0x01; break;
                    default: break;
                }
            }
        }

        // Run 1 frame
        nes.runFrame();

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

    // Cleanup
    SDL_DestroyTexture(texture);
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 0;
}
