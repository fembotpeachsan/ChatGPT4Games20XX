import tkinter as tk
from tkinter import filedialog, messagebox
try:
    from PIL import Image, ImageTk
except ImportError:
    Image = ImageTk = None  # If Pillow is not installed, we will handle later.

# --- Global NES Constants ---
SCREEN_WIDTH = 256
SCREEN_HEIGHT = 240

# NES 64-color palette (RGB values for each of the 64 NES color indices).
# These are hex strings for convenience; we will convert to RGB tuples.
NES_PALETTE_HEX = [
    "585858","00237C","0D1099","300092","4F006C","600035","5C0500","461800",
    "272D00","093E00","004500","004106","003545","000000","000000","000000",
    "A1A1A1","0B53D7","3337FE","6621F7","9515BE","AC166E","A62721","864300",
    "596200","2D7A00","0C8500","007F2A","006D85","000000","000000","000000",
    "FFFFFF","51A5FE","8084FE","BC6AFE","F15BFE","FE5EC4","FE7269","E19321",
    "ADB600","79D300","51DF21","3AD974","39C3DF","424242","000000","000000",
    "FFFFFF","B5D9FE","CACAFE","E3BEFE","F9B8FE","FEBAE7","FEC3BC","F4D199",
    "DEE086","C6EC87","B2F29D","A7F0C3","A8E7F0","ACACAC","000000","000000"
]
NES_PALETTE = [(int(c[0:2],16), int(c[2:4],16), int(c[4:6],16)) for c in NES_PALETTE_HEX]

# CPU Flags bit positions
FLAG_C = 0x01  # Carry
FLAG_Z = 0x02  # Zero
FLAG_I = 0x04  # Interrupt Disable
FLAG_D = 0x08  # Decimal (unused on NES)
FLAG_B = 0x10  # Break
FLAG_U = 0x20  # Unused (always 1 in status)
FLAG_V = 0x40  # Overflow
FLAG_N = 0x80  # Negative

# Memory
RAM_SIZE = 0x0800  # 2KB internal RAM

# Controller bits order: A, B, Select, Start, Up, Down, Left, Right
BUTTON_A = 0x01
BUTTON_B = 0x02
BUTTON_SELECT = 0x04
BUTTON_START = 0x08
BUTTON_UP = 0x10
BUTTON_DOWN = 0x20
BUTTON_LEFT = 0x40
BUTTON_RIGHT = 0x80

# --- NES Emulator Classes ---

class CPU6502:
    """MOS 6502 CPU Emulation."""
    def __init__(self, bus):
        self.bus = bus  # reference to memory I/O (the Bus)
        # Registers
        self.A = 0   # Accumulator
        self.X = 0   # X index
        self.Y = 0   # Y index
        self.SP = 0xFD  # Stack Pointer (init to 0xFD as per reset)
        self.PC = 0    # Program Counter
        self.STATUS = 0x24  # Processor status (IRQ disabled by default, FLAG_U set)
    
    def reset(self):
        # On reset, read vector at $FFFC to set PC
        lo = self.bus.read(0xFFFC)
        hi = self.bus.read(0xFFFD)
        self.PC = (hi << 8) | lo
        self.SP = 0xFD
        self.STATUS = 0x24  # Flags: U and I set
        # Note: A, X, Y remain undefined on real reset, but we'll zero them
        self.A = 0
        self.X = 0
        self.Y = 0
    
    def set_flag(self, flag, condition):
        if condition:
            self.STATUS |= flag
        else:
            self.STATUS &= ~flag
    
    def get_flag(self, flag):
        return (self.STATUS & flag) != 0
    
    def push(self, value):
        """Push a byte onto the stack."""
        self.bus.write(0x0100 | self.SP, value & 0xFF)
        self.SP = (self.SP - 1) & 0xFF
    
    def pop(self):
        """Pop a byte from the stack."""
        self.SP = (self.SP + 1) & 0xFF
        return self.bus.read(0x0100 | self.SP)
    
    def fetch_byte(self):
        byte = self.bus.read(self.PC)
        self.PC = (self.PC + 1) & 0xFFFF
        return byte
    
    def fetch_word(self):
        # 6502 is little-endian
        lo = self.fetch_byte()
        hi = self.fetch_byte()
        return lo | (hi << 8)
    
    # Addressing mode helpers to get effective address or value
    def addr_zero_page(self):
        return self.fetch_byte()  # zero-page address (0x00xx)
    def addr_zero_page_x(self):
        addr = (self.fetch_byte() + self.X) & 0xFF
        return addr
    def addr_zero_page_y(self):
        addr = (self.fetch_byte() + self.Y) & 0xFF
        return addr
    def addr_absolute(self):
        return self.fetch_word()
    def addr_absolute_x(self, check_page_cross=False):
        base = self.fetch_word()
        addr = (base + self.X) & 0xFFFF
        if check_page_cross and (addr & 0xFF00) != (base & 0xFF00):
            self.bus.cycles += 1  # extra cycle for page boundary crossing
        return addr
    def addr_absolute_y(self, check_page_cross=False):
        base = self.fetch_word()
        addr = (base + self.Y) & 0xFFFF
        if check_page_cross and (addr & 0xFF00) != (base & 0xFF00):
            self.bus.cycles += 1
        return addr
    def addr_indirect(self):
        # 6502 bug: the indirect read wraps on page boundary
        ptr = self.fetch_word()
        lo = self.bus.read(ptr)
        # If vector crosses page boundary, wrap around within the same page
        if (ptr & 0xFF) == 0xFF:
            hi = self.bus.read(ptr & 0xFF00)  # wrap around
        else:
            hi = self.bus.read(ptr + 1)
        return lo | (hi << 8)
    def addr_indirect_x(self):
        # Indexed indirect ([d,X])
        zp_addr = (self.fetch_byte() + self.X) & 0xFF
        lo = self.bus.read(zp_addr)
        hi = self.bus.read((zp_addr + 1) & 0xFF)
        return lo | (hi << 8)
    def addr_indirect_y(self, check_page_cross=False):
        # Indirect indexed ([d],Y)
        zp_addr = self.fetch_byte() & 0xFF
        lo = self.bus.read(zp_addr)
        hi = self.bus.read((zp_addr + 1) & 0xFF)
        base = lo | (hi << 8)
        addr = (base + self.Y) & 0xFFFF
        if check_page_cross and (addr & 0xFF00) != (base & 0xFF00):
            self.bus.cycles += 1
        return addr
    
    # Read/write operations through the bus (memory)
    def read(self, addr):
        return self.bus.read(addr)
    def write(self, addr, data):
        self.bus.write(addr, data & 0xFF)
    
    # Helpers to update Zero and Negative flags based on a value
    def update_zn(self, value):
        self.set_flag(FLAG_Z, (value & 0xFF) == 0)
        self.set_flag(FLAG_N, (value & 0x80) != 0)
    
    # CPU Instruction implementations:
    def adc(self, value):
        # Add with Carry
        a = self.A
        c = 1 if self.get_flag(FLAG_C) else 0
        result = a + value + c
        # Set carry
        self.set_flag(FLAG_C, result > 0xFF)
        # Set overflow (if sign bits of a and value are same, but differ from result)
        self.set_flag(FLAG_V, (~(a ^ value) & (a ^ result) & 0x80) != 0)
        self.A = result & 0xFF
        self.update_zn(self.A)
    
    def sbc(self, value):
        # Subtract with Carry (Carry clear means borrow)
        self.adc((~value) & 0xFF)
    
    def and_(self, value):
        self.A &= value
        self.update_zn(self.A)
    
    def ora(self, value):
        self.A |= value
        self.update_zn(self.A)
    
    def eor(self, value):
        self.A ^= value
        self.update_zn(self.A)
    
    def asl(self, addr=None):
        if addr is None:
            # Accumulator
            self.set_flag(FLAG_C, (self.A & 0x80) != 0)
            self.A = (self.A << 1) & 0xFF
            self.update_zn(self.A)
        else:
            val = self.bus.read(addr)
            self.set_flag(FLAG_C, (val & 0x80) != 0)
            val = (val << 1) & 0xFF
            self.bus.write(addr, val)
            self.update_zn(val)
    
    def lsr(self, addr=None):
        if addr is None:
            self.set_flag(FLAG_C, (self.A & 0x01) != 0)
            self.A = (self.A >> 1) & 0xFF
            self.update_zn(self.A)
        else:
            val = self.bus.read(addr)
            self.set_flag(FLAG_C, (val & 0x01) != 0)
            val = val >> 1
            self.bus.write(addr, val)
            self.update_zn(val)
    
    def rol(self, addr=None):
        carry_in = 1 if self.get_flag(FLAG_C) else 0
        if addr is None:
            carry_out = (self.A & 0x80) != 0
            self.A = ((self.A << 1) & 0xFF) | carry_in
            self.set_flag(FLAG_C, carry_out)
            self.update_zn(self.A)
        else:
            val = self.bus.read(addr)
            carry_out = (val & 0x80) != 0
            new_val = ((val << 1) & 0xFF) | carry_in
            self.bus.write(addr, new_val)
            self.set_flag(FLAG_C, carry_out)
            self.update_zn(new_val)
    
    def ror(self, addr=None):
        carry_in = 1 if self.get_flag(FLAG_C) else 0
        if addr is None:
            carry_out = (self.A & 0x01) != 0
            self.A = (carry_in << 7) | (self.A >> 1)
            self.set_flag(FLAG_C, carry_out)
            self.update_zn(self.A)
        else:
            val = self.bus.read(addr)
            carry_out = (val & 0x01) != 0
            new_val = (carry_in << 7) | (val >> 1)
            self.bus.write(addr, new_val)
            self.set_flag(FLAG_C, carry_out)
            self.update_zn(new_val)
    
    def cmp(self, reg, value):
        # Compare reg (A, X, or Y) with value
        result = reg - value
        self.set_flag(FLAG_C, result >= 0)
        self.update_zn(result & 0xFF)
    
    def bit_test(self, value):
        # BIT test: set Z to result of AND, N to high bit of value, V to bit6 of value
        self.set_flag(FLAG_Z, (self.A & value) == 0)
        self.set_flag(FLAG_N, (value & 0x80) != 0)
        self.set_flag(FLAG_V, (value & 0x40) != 0)
    
    def execute_instruction(self):
        """Fetch and execute one CPU instruction, return number of cycles used."""
        opcode = self.fetch_byte()
        # Base cycle counts for each opcode (without page-cross penalties)
        # A partial list for demonstration (complete list should cover all 256 opcodes or at least all official ones).
        # For brevity, not all opcodes are enumerated in comments; our logic covers main ones.
        # We will handle branch and page-cross cycle additions in code.
        cycles_base = {
            0x00: 7,  # BRK
            0x01: 6,  # ORA (ind,X)
            0x05: 3,  # ORA zpg
            0x06: 5,  # ASL zpg
            0x08: 3,  # PHP
            0x09: 2,  # ORA #imm
            0x0A: 2,  # ASL A
            0x0D: 4,  # ORA abs
            0x0E: 6,  # ASL abs
            0x10: 2,  # BPL (branch - may add 1 or 2 cycles)
            0x11: 5,  # ORA (ind),Y (+1 if page crossed)
            0x15: 4,  # ORA zpg,X
            0x16: 6,  # ASL zpg,X
            0x18: 2,  # CLC
            0x19: 4,  # ORA abs,Y (+1 if page crossed)
            0x1D: 4,  # ORA abs,X (+1 if page crossed)
            0x1E: 7,  # ASL abs,X
            0x20: 6,  # JSR abs
            0x21: 6,  # AND (ind,X)
            0x24: 3,  # BIT zpg
            0x25: 3,  # AND zpg
            0x26: 5,  # ROL zpg
            0x28: 4,  # PLP
            0x29: 2,  # AND #imm
            0x2A: 2,  # ROL A
            0x2C: 4,  # BIT abs
            0x2D: 4,  # AND abs
            0x2E: 6,  # ROL abs
            0x30: 2,  # BMI
            0x31: 5,  # AND (ind),Y (+1 if page crossed)
            0x35: 4,  # AND zpg,X
            0x36: 6,  # ROL zpg,X
            0x38: 2,  # SEC
            0x39: 4,  # AND abs,Y (+1 if page crossed)
            0x3D: 4,  # AND abs,X (+1 if page crossed)
            0x3E: 7,  # ROL abs,X
            0x40: 6,  # RTI
            0x41: 6,  # EOR (ind,X)
            0x45: 3,  # EOR zpg
            0x46: 5,  # LSR zpg
            0x48: 3,  # PHA
            0x49: 2,  # EOR #imm
            0x4A: 2,  # LSR A
            0x4C: 3,  # JMP abs
            0x4D: 4,  # EOR abs
            0x4E: 6,  # LSR abs
            0x50: 2,  # BVC
            0x51: 5,  # EOR (ind),Y (+1 if page crossed)
            0x55: 4,  # EOR zpg,X
            0x56: 6,  # LSR zpg,X
            0x58: 2,  # CLI
            0x59: 4,  # EOR abs,Y (+1 if page crossed)
            0x5D: 4,  # EOR abs,X (+1 if page crossed)
            0x5E: 7,  # LSR abs,X
            0x60: 6,  # RTS
            0x61: 6,  # ADC (ind,X)
            0x65: 3,  # ADC zpg
            0x66: 5,  # ROR zpg
            0x68: 4,  # PLA
            0x69: 2,  # ADC #imm
            0x6A: 2,  # ROR A
            0x6C: 5,  # JMP (ind)
            0x6D: 4,  # ADC abs
            0x6E: 6,  # ROR abs
            0x70: 2,  # BVS
            0x71: 5,  # ADC (ind),Y (+1 if page crossed)
            0x75: 4,  # ADC zpg,X
            0x76: 6,  # ROR zpg,X
            0x78: 2,  # SEI
            0x79: 4,  # ADC abs,Y (+1 if page crossed)
            0x7D: 4,  # ADC abs,X (+1 if page crossed)
            0x7E: 7,  # ROR abs,X
            0x81: 6,  # STA (ind,X)
            0x84: 3,  # STY zpg
            0x85: 3,  # STA zpg
            0x86: 3,  # STX zpg
            0x88: 2,  # DEY
            0x8A: 2,  # TXA
            0x8C: 4,  # STY abs
            0x8D: 4,  # STA abs
            0x8E: 4,  # STX abs
            0x90: 2,  # BCC
            0x91: 6,  # STA (ind),Y
            0x94: 4,  # STY zpg,X
            0x95: 4,  # STA zpg,X
            0x96: 4,  # STX zpg,Y
            0x98: 2,  # TYA
            0x99: 5,  # STA abs,Y
            0x9A: 2,  # TXS
            0x9D: 5,  # STA abs,X
            0xA0: 2,  # LDY #imm
            0xA1: 6,  # LDA (ind,X)
            0xA2: 2,  # LDX #imm
            0xA4: 3,  # LDY zpg
            0xA5: 3,  # LDA zpg
            0xA6: 3,  # LDX zpg
            0xA8: 2,  # TAY
            0xA9: 2,  # LDA #imm
            0xAA: 2,  # TAX
            0xAC: 4,  # LDY abs
            0xAD: 4,  # LDA abs
            0xAE: 4,  # LDX abs
            0xB0: 2,  # BCS
            0xB1: 5,  # LDA (ind),Y (+1 if page crossed)
            0xB4: 4,  # LDY zpg,X
            0xB5: 4,  # LDA zpg,X
            0xB6: 4,  # LDX zpg,Y
            0xB8: 2,  # CLV
            0xB9: 4,  # LDA abs,Y (+1 if page crossed)
            0xBA: 2,  # TSX
            0xBC: 4,  # LDY abs,X (+1 if page crossed)
            0xBD: 4,  # LDA abs,X (+1 if page crossed)
            0xBE: 4,  # LDX abs,Y (+1 if page crossed)
            0xC0: 2,  # CPY #imm
            0xC1: 6,  # CMP (ind,X)
            0xC4: 3,  # CPY zpg
            0xC5: 3,  # CMP zpg
            0xC6: 5,  # DEC zpg
            0xC8: 2,  # INY
            0xC9: 2,  # CMP #imm
            0xCA: 2,  # DEX
            0xCC: 4,  # CPY abs
            0xCD: 4,  # CMP abs
            0xCE: 6,  # DEC abs
            0xD0: 2,  # BNE
            0xD1: 5,  # CMP (ind),Y (+1 if page crossed)
            0xD5: 4,  # CMP zpg,X
            0xD6: 6,  # DEC zpg,X
            0xD8: 2,  # CLD
            0xD9: 4,  # CMP abs,Y (+1 if page crossed)
            0xDD: 4,  # CMP abs,X (+1 if page crossed)
            0xDE: 7,  # DEC abs,X
            0xE0: 2,  # CPX #imm
            0xE1: 6,  # SBC (ind,X)
            0xE4: 3,  # CPX zpg
            0xE5: 3,  # SBC zpg
            0xE6: 5,  # INC zpg
            0xE8: 2,  # INX
            0xE9: 2,  # SBC #imm
            0xEA: 2,  # NOP
            0xEC: 4,  # CPX abs
            0xED: 4,  # SBC abs
            0xEE: 6,  # INC abs
            0xF0: 2,  # BEQ
            0xF1: 5,  # SBC (ind),Y (+1 if page crossed)
            0xF5: 4,  # SBC zpg,X
            0xF6: 6,  # INC zpg,X
            0xF8: 2,  # SED
            0xF9: 4,  # SBC abs,Y (+1 if page crossed)
            0xFD: 4,  # SBC abs,X (+1 if page crossed)
            0xFE: 7,  # INC abs,X
        }
        # Set base cycles for this opcode, will add extras later if needed
        cycles = cycles_base.get(opcode, 2)
        
        # Decode and execute the opcode
        if opcode == 0x00:  # BRK - Force Interrupt
            self.fetch_byte()  # BRK has an unused padding byte after opcode
            self.set_flag(FLAG_B, True)
            self.push((self.PC >> 8) & 0xFF)
            self.push(self.PC & 0xFF)
            self.push(self.STATUS)
            self.set_flag(FLAG_I, True)
            self.PC = self.bus.read(0xFFFE) | (self.bus.read(0xFFFF) << 8)
        elif opcode == 0x01:  # ORA (Indirect,X)
            addr = self.addr_indirect_x()
            self.ora(self.bus.read(addr))
        elif opcode == 0x05:  # ORA Zero Page
            addr = self.addr_zero_page()
            self.ora(self.bus.read(addr))
        elif opcode == 0x06:  # ASL Zero Page
            addr = self.addr_zero_page()
            self.asl(addr)
        elif opcode == 0x08:  # PHP
            # Push SR with B flag and U flag set
            flags = self.STATUS | FLAG_B | FLAG_U
            self.push(flags)
        elif opcode == 0x09:  # ORA Immediate
            value = self.fetch_byte()
            self.ora(value)
        elif opcode == 0x0A:  # ASL A
            self.asl()
        elif opcode == 0x0D:  # ORA Absolute
            addr = self.addr_absolute()
            self.ora(self.bus.read(addr))
        elif opcode == 0x0E:  # ASL Absolute
            addr = self.addr_absolute()
            self.asl(addr)
        elif opcode == 0x10:  # BPL (Branch if Positive)
            offset = self.fetch_byte()
            if not self.get_flag(FLAG_N):  # Negative flag clear => positive
                # branch taken
                cycles += 1
                new_pc = (self.PC + ((offset ^ 0x80) - 0x80)) & 0xFFFF  # sign-extend offset
                if (new_pc & 0xFF00) != (self.PC & 0xFF00):
                    cycles += 1  # page boundary crossed
                self.PC = new_pc
        elif opcode == 0x11:  # ORA (Indirect),Y
            addr = self.addr_indirect_y(check_page_cross=True)
            self.ora(self.bus.read(addr))
        elif opcode == 0x15:  # ORA Zero Page,X
            addr = self.addr_zero_page_x()
            self.ora(self.bus.read(addr))
        elif opcode == 0x16:  # ASL Zero Page,X
            addr = self.addr_zero_page_x()
            self.asl(addr)
        elif opcode == 0x18:  # CLC
            self.set_flag(FLAG_C, False)
        elif opcode == 0x19:  # ORA Absolute,Y
            addr = self.addr_absolute_y(check_page_cross=True)
            self.ora(self.bus.read(addr))
        elif opcode == 0x1D:  # ORA Absolute,X
            addr = self.addr_absolute_x(check_page_cross=True)
            self.ora(self.bus.read(addr))
        elif opcode == 0x1E:  # ASL Absolute,X
            addr = self.addr_absolute_x()  # ASL abs,X ignores page penalty
            self.asl(addr)
        elif opcode == 0x20:  # JSR Absolute
            addr = self.addr_absolute()  # get target address
            # Push address of last byte of JSR (PC-1) onto stack
            return_addr = (self.PC - 1) & 0xFFFF
            self.push((return_addr >> 8) & 0xFF)
            self.push(return_addr & 0xFF)
            self.PC = addr
        elif opcode == 0x21:  # AND (Indirect,X)
            addr = self.addr_indirect_x()
            self.and_(self.bus.read(addr))
        elif opcode == 0x24:  # BIT Zero Page
            addr = self.addr_zero_page()
            self.bit_test(self.bus.read(addr))
        elif opcode == 0x25:  # AND Zero Page
            addr = self.addr_zero_page()
            self.and_(self.bus.read(addr))
        elif opcode == 0x26:  # ROL Zero Page
            addr = self.addr_zero_page()
            self.rol(addr)
        elif opcode == 0x28:  # PLP
            self.STATUS = self.pop()
            # The B flag and unused flag bits 4 and 5 in the status are not actual flags, ensure proper state:
            self.STATUS |= FLAG_U
            self.STATUS &= ~FLAG_B
        elif opcode == 0x29:  # AND Immediate
            val = self.fetch_byte()
            self.and_(val)
        elif opcode == 0x2A:  # ROL A
            self.rol()
        elif opcode == 0x2C:  # BIT Absolute
            addr = self.addr_absolute()
            self.bit_test(self.bus.read(addr))
        elif opcode == 0x2D:  # AND Absolute
            addr = self.addr_absolute()
            self.and_(self.bus.read(addr))
        elif opcode == 0x2E:  # ROL Absolute
            addr = self.addr_absolute()
            self.rol(addr)
        elif opcode == 0x30:  # BMI (Branch if Minus)
            offset = self.fetch_byte()
            if self.get_flag(FLAG_N):
                cycles += 1
                new_pc = (self.PC + ((offset ^ 0x80) - 0x80)) & 0xFFFF
                if (new_pc & 0xFF00) != (self.PC & 0xFF00):
                    cycles += 1
                self.PC = new_pc
        elif opcode == 0x31:  # AND (Indirect),Y
            addr = self.addr_indirect_y(check_page_cross=True)
            self.and_(self.bus.read(addr))
        elif opcode == 0x35:  # AND Zero Page,X
            addr = self.addr_zero_page_x()
            self.and_(self.bus.read(addr))
        elif opcode == 0x36:  # ROL Zero Page,X
            addr = self.addr_zero_page_x()
            self.rol(addr)
        elif opcode == 0x38:  # SEC
            self.set_flag(FLAG_C, True)
        elif opcode == 0x39:  # AND Absolute,Y
            addr = self.addr_absolute_y(check_page_cross=True)
            self.and_(self.bus.read(addr))
        elif opcode == 0x3D:  # AND Absolute,X
            addr = self.addr_absolute_x(check_page_cross=True)
            self.and_(self.bus.read(addr))
        elif opcode == 0x3E:  # ROL Absolute,X
            addr = self.addr_absolute_x()
            self.rol(addr)
        elif opcode == 0x40:  # RTI
            # Pull flags, then PC from stack
            self.STATUS = self.pop()
            self.STATUS |= FLAG_U
            self.STATUS &= ~FLAG_B
            lo = self.pop()
            hi = self.pop()
            self.PC = lo | (hi << 8)
        elif opcode == 0x41:  # EOR (Indirect,X)
            addr = self.addr_indirect_x()
            self.eor(self.bus.read(addr))
        elif opcode == 0x45:  # EOR Zero Page
            addr = self.addr_zero_page()
            self.eor(self.bus.read(addr))
        elif opcode == 0x46:  # LSR Zero Page
            addr = self.addr_zero_page()
            self.lsr(addr)
        elif opcode == 0x48:  # PHA
            self.push(self.A)
        elif opcode == 0x49:  # EOR Immediate
            val = self.fetch_byte()
            self.eor(val)
        elif opcode == 0x4A:  # LSR A
            self.lsr()
        elif opcode == 0x4C:  # JMP Absolute
            addr = self.addr_absolute()
            self.PC = addr
        elif opcode == 0x4D:  # EOR Absolute
            addr = self.addr_absolute()
            self.eor(self.bus.read(addr))
        elif opcode == 0x4E:  # LSR Absolute
            addr = self.addr_absolute()
            self.lsr(addr)
        elif opcode == 0x50:  # BVC (Branch if Overflow Clear)
            offset = self.fetch_byte()
            if not self.get_flag(FLAG_V):
                cycles += 1
                new_pc = (self.PC + ((offset ^ 0x80) - 0x80)) & 0xFFFF
                if (new_pc & 0xFF00) != (self.PC & 0xFF00):
                    cycles += 1
                self.PC = new_pc
        elif opcode == 0x51:  # EOR (Indirect),Y
            addr = self.addr_indirect_y(check_page_cross=True)
            self.eor(self.bus.read(addr))
        elif opcode == 0x55:  # EOR Zero Page,X
            addr = self.addr_zero_page_x()
            self.eor(self.bus.read(addr))
        elif opcode == 0x56:  # LSR Zero Page,X
            addr = self.addr_zero_page_x()
            self.lsr(addr)
        elif opcode == 0x58:  # CLI
            self.set_flag(FLAG_I, False)
        elif opcode == 0x59:  # EOR Absolute,Y
            addr = self.addr_absolute_y(check_page_cross=True)
            self.eor(self.bus.read(addr))
        elif opcode == 0x5D:  # EOR Absolute,X
            addr = self.addr_absolute_x(check_page_cross=True)
            self.eor(self.bus.read(addr))
        elif opcode == 0x5E:  # LSR Absolute,X
            addr = self.addr_absolute_x()
            self.lsr(addr)
        elif opcode == 0x60:  # RTS
            lo = self.pop()
            hi = self.pop()
            self.PC = (lo | (hi << 8)) + 1
            self.PC &= 0xFFFF
        elif opcode == 0x61:  # ADC (Indirect,X)
            addr = self.addr_indirect_x()
            self.adc(self.bus.read(addr))
        elif opcode == 0x65:  # ADC Zero Page
            addr = self.addr_zero_page()
            self.adc(self.bus.read(addr))
        elif opcode == 0x66:  # ROR Zero Page
            addr = self.addr_zero_page()
            self.ror(addr)
        elif opcode == 0x68:  # PLA
            self.A = self.pop()
            self.update_zn(self.A)
        elif opcode == 0x69:  # ADC Immediate
            val = self.fetch_byte()
            self.adc(val)
        elif opcode == 0x6A:  # ROR A
            self.ror()
        elif opcode == 0x6C:  # JMP (Indirect)
            addr = self.addr_indirect()
            self.PC = addr
        elif opcode == 0x6D:  # ADC Absolute
            addr = self.addr_absolute()
            self.adc(self.bus.read(addr))
        elif opcode == 0x6E:  # ROR Absolute
            addr = self.addr_absolute()
            self.ror(addr)
        elif opcode == 0x70:  # BVS (Branch if Overflow Set)
            offset = self.fetch_byte()
            if self.get_flag(FLAG_V):
                cycles += 1
                new_pc = (self.PC + ((offset ^ 0x80) - 0x80)) & 0xFFFF
                if (new_pc & 0xFF00) != (self.PC & 0xFF00):
                    cycles += 1
                self.PC = new_pc
        elif opcode == 0x71:  # ADC (Indirect),Y
            addr = self.addr_indirect_y(check_page_cross=True)
            self.adc(self.bus.read(addr))
        elif opcode == 0x75:  # ADC Zero Page,X
            addr = self.addr_zero_page_x()
            self.adc(self.bus.read(addr))
        elif opcode == 0x76:  # ROR Zero Page,X
            addr = self.addr_zero_page_x()
            self.ror(addr)
        elif opcode == 0x78:  # SEI
            self.set_flag(FLAG_I, True)
        elif opcode == 0x79:  # ADC Absolute,Y
            addr = self.addr_absolute_y(check_page_cross=True)
            self.adc(self.bus.read(addr))
        elif opcode == 0x7D:  # ADC Absolute,X
            addr = self.addr_absolute_x(check_page_cross=True)
            self.adc(self.bus.read(addr))
        elif opcode == 0x7E:  # ROR Absolute,X
            addr = self.addr_absolute_x()
            self.ror(addr)
        elif opcode == 0x81:  # STA (Indirect,X)
            addr = self.addr_indirect_x()
            self.bus.write(addr, self.A)
        elif opcode == 0x84:  # STY Zero Page
            addr = self.addr_zero_page()
            self.bus.write(addr, self.Y)
        elif opcode == 0x85:  # STA Zero Page
            addr = self.addr_zero_page()
            self.bus.write(addr, self.A)
        elif opcode == 0x86:  # STX Zero Page
            addr = self.addr_zero_page()
            self.bus.write(addr, self.X)
        elif opcode == 0x88:  # DEY
            self.Y = (self.Y - 1) & 0xFF
            self.update_zn(self.Y)
        elif opcode == 0x8A:  # TXA
            self.A = self.X
            self.update_zn(self.A)
        elif opcode == 0x8C:  # STY Absolute
            addr = self.addr_absolute()
            self.bus.write(addr, self.Y)
        elif opcode == 0x8D:  # STA Absolute
            addr = self.addr_absolute()
            self.bus.write(addr, self.A)
        elif opcode == 0x8E:  # STX Absolute
            addr = self.addr_absolute()
            self.bus.write(addr, self.X)
        elif opcode == 0x90:  # BCC
            offset = self.fetch_byte()
            if not self.get_flag(FLAG_C):
                cycles += 1
                new_pc = (self.PC + ((offset ^ 0x80) - 0x80)) & 0xFFFF
                if (new_pc & 0xFF00) != (self.PC & 0xFF00):
                    cycles += 1
                self.PC = new_pc
        elif opcode == 0x91:  # STA (Indirect),Y
            addr = self.addr_indirect_y()
            self.bus.write(addr, self.A)
        elif opcode == 0x94:  # STY Zero Page,X
            addr = self.addr_zero_page_x()
            self.bus.write(addr, self.Y)
        elif opcode == 0x95:  # STA Zero Page,X
            addr = self.addr_zero_page_x()
            self.bus.write(addr, self.A)
        elif opcode == 0x96:  # STX Zero Page,Y
            addr = self.addr_zero_page_y()
            self.bus.write(addr, self.X)
        elif opcode == 0x98:  # TYA
            self.A = self.Y
            self.update_zn(self.A)
        elif opcode == 0x99:  # STA Absolute,Y
            addr = self.addr_absolute_y()
            self.bus.write(addr, self.A)
        elif opcode == 0x9A:  # TXS
            self.SP = self.X
        elif opcode == 0x9D:  # STA Absolute,X
            addr = self.addr_absolute_x()
            self.bus.write(addr, self.A)
        elif opcode == 0xA0:  # LDY Immediate
            self.Y = self.fetch_byte()
            self.update_zn(self.Y)
        elif opcode == 0xA1:  # LDA (Indirect,X)
            addr = self.addr_indirect_x()
            self.A = self.bus.read(addr)
            self.update_zn(self.A)
        elif opcode == 0xA2:  # LDX Immediate
            self.X = self.fetch_byte()
            self.update_zn(self.X)
        elif opcode == 0xA4:  # LDY Zero Page
            addr = self.addr_zero_page()
            self.Y = self.bus.read(addr)
            self.update_zn(self.Y)
        elif opcode == 0xA5:  # LDA Zero Page
            addr = self.addr_zero_page()
            self.A = self.bus.read(addr)
            self.update_zn(self.A)
        elif opcode == 0xA6:  # LDX Zero Page
            addr = self.addr_zero_page()
            self.X = self.bus.read(addr)
            self.update_zn(self.X)
        elif opcode == 0xA8:  # TAY
            self.Y = self.A
            self.update_zn(self.Y)
        elif opcode == 0xA9:  # LDA Immediate
            self.A = self.fetch_byte()
            self.update_zn(self.A)
        elif opcode == 0xAA:  # TAX
            self.X = self.A
            self.update_zn(self.X)
        elif opcode == 0xAC:  # LDY Absolute
            addr = self.addr_absolute()
            self.Y = self.bus.read(addr)
            self.update_zn(self.Y)
        elif opcode == 0xAD:  # LDA Absolute
            addr = self.addr_absolute()
            self.A = self.bus.read(addr)
            self.update_zn(self.A)
        elif opcode == 0xAE:  # LDX Absolute
            addr = self.addr_absolute()
            self.X = self.bus.read(addr)
            self.update_zn(self.X)
        elif opcode == 0xB0:  # BCS
            offset = self.fetch_byte()
            if self.get_flag(FLAG_C):
                cycles += 1
                new_pc = (self.PC + ((offset ^ 0x80) - 0x80)) & 0xFFFF
                if (new_pc & 0xFF00) != (self.PC & 0xFF00):
                    cycles += 1
                self.PC = new_pc
        elif opcode == 0xB1:  # LDA (Indirect),Y
            addr = self.addr_indirect_y(check_page_cross=True)
            self.A = self.bus.read(addr)
            self.update_zn(self.A)
        elif opcode == 0xB4:  # LDY Zero Page,X
            addr = self.addr_zero_page_x()
            self.Y = self.bus.read(addr)
            self.update_zn(self.Y)
        elif opcode == 0xB5:  # LDA Zero Page,X
            addr = self.addr_zero_page_x()
            self.A = self.bus.read(addr)
            self.update_zn(self.A)
        elif opcode == 0xB6:  # LDX Zero Page,Y
            addr = self.addr_zero_page_y()
            self.X = self.bus.read(addr)
            self.update_zn(self.X)
        elif opcode == 0xB8:  # CLV
            self.set_flag(FLAG_V, False)
        elif opcode == 0xB9:  # LDA Absolute,Y
            addr = self.addr_absolute_y(check_page_cross=True)
            self.A = self.bus.read(addr)
            self.update_zn(self.A)
        elif opcode == 0xBA:  # TSX
            self.X = self.SP
            self.update_zn(self.X)
        elif opcode == 0xBC:  # LDY Absolute,X
            addr = self.addr_absolute_x(check_page_cross=True)
            self.Y = self.bus.read(addr)
            self.update_zn(self.Y)
        elif opcode == 0xBD:  # LDA Absolute,X
            addr = self.addr_absolute_x(check_page_cross=True)
            self.A = self.bus.read(addr)
            self.update_zn(self.A)
        elif opcode == 0xBE:  # LDX Absolute,Y
            addr = self.addr_absolute_y(check_page_cross=True)
            self.X = self.bus.read(addr)
            self.update_zn(self.X)
        elif opcode == 0xC0:  # CPY Immediate
            value = self.fetch_byte()
            self.cmp(self.Y, value)
        elif opcode == 0xC1:  # CMP (Indirect,X)
            addr = self.addr_indirect_x()
            self.cmp(self.A, self.bus.read(addr))
        elif opcode == 0xC4:  # CPY Zero Page
            addr = self.addr_zero_page()
            self.cmp(self.Y, self.bus.read(addr))
        elif opcode == 0xC5:  # CMP Zero Page
            addr = self.addr_zero_page()
            self.cmp(self.A, self.bus.read(addr))
        elif opcode == 0xC6:  # DEC Zero Page
            addr = self.addr_zero_page()
            val = (self.bus.read(addr) - 1) & 0xFF
            self.bus.write(addr, val)
            self.update_zn(val)
        elif opcode == 0xC8:  # INY
            self.Y = (self.Y + 1) & 0xFF
            self.update_zn(self.Y)
        elif opcode == 0xC9:  # CMP Immediate
            value = self.fetch_byte()
            self.cmp(self.A, value)
        elif opcode == 0xCA:  # DEX
            self.X = (self.X - 1) & 0xFF
            self.update_zn(self.X)
        elif opcode == 0xCC:  # CPY Absolute
            addr = self.addr_absolute()
            self.cmp(self.Y, self.bus.read(addr))
        elif opcode == 0xCD:  # CMP Absolute
            addr = self.addr_absolute()
            self.cmp(self.A, self.bus.read(addr))
        elif opcode == 0xCE:  # DEC Absolute
            addr = self.addr_absolute()
            val = (self.bus.read(addr) - 1) & 0xFF
            self.bus.write(addr, val)
            self.update_zn(val)
        elif opcode == 0xD0:  # BNE
            offset = self.fetch_byte()
            if not self.get_flag(FLAG_Z):
                cycles += 1
                new_pc = (self.PC + ((offset ^ 0x80) - 0x80)) & 0xFFFF
                if (new_pc & 0xFF00) != (self.PC & 0xFF00):
                    cycles += 1
                self.PC = new_pc
        elif opcode == 0xD1:  # CMP (Indirect),Y
            addr = self.addr_indirect_y(check_page_cross=True)
            self.cmp(self.A, self.bus.read(addr))
        elif opcode == 0xD5:  # CMP Zero Page,X
            addr = self.addr_zero_page_x()
            self.cmp(self.A, self.bus.read(addr))
        elif opcode == 0xD6:  # DEC Zero Page,X
            addr = self.addr_zero_page_x()
            val = (self.bus.read(addr) - 1) & 0xFF
            self.bus.write(addr, val)
            self.update_zn(val)
        elif opcode == 0xD8:  # CLD
            self.set_flag(FLAG_D, False)
        elif opcode == 0xD9:  # CMP Absolute,Y
            addr = self.addr_absolute_y(check_page_cross=True)
            self.cmp(self.A, self.bus.read(addr))
        elif opcode == 0xDD:  # CMP Absolute,X
            addr = self.addr_absolute_x(check_page_cross=True)
            self.cmp(self.A, self.bus.read(addr))
        elif opcode == 0xDE:  # DEC Absolute,X
            addr = self.addr_absolute_x()
            val = (self.bus.read(addr) - 1) & 0xFF
            self.bus.write(addr, val)
            self.update_zn(val)
        elif opcode == 0xE0:  # CPX Immediate
            value = self.fetch_byte()
            self.cmp(self.X, value)
        elif opcode == 0xE1:  # SBC (Indirect,X)
            addr = self.addr_indirect_x()
            self.sbc(self.bus.read(addr))
        elif opcode == 0xE4:  # CPX Zero Page
            addr = self.addr_zero_page()
            self.cmp(self.X, self.bus.read(addr))
        elif opcode == 0xE5:  # SBC Zero Page
            addr = self.addr_zero_page()
            self.sbc(self.bus.read(addr))
        elif opcode == 0xE6:  # INC Zero Page
            addr = self.addr_zero_page()
            val = (self.bus.read(addr) + 1) & 0xFF
            self.bus.write(addr, val)
            self.update_zn(val)
        elif opcode == 0xE8:  # INX
            self.X = (self.X + 1) & 0xFF
            self.update_zn(self.X)
        elif opcode == 0xE9:  # SBC Immediate
            val = self.fetch_byte()
            self.sbc(val)
        elif opcode == 0xEA:  # NOP
            pass  # do nothing
        elif opcode == 0xEC:  # CPX Absolute
            addr = self.addr_absolute()
            self.cmp(self.X, self.bus.read(addr))
        elif opcode == 0xED:  # SBC Absolute
            addr = self.addr_absolute()
            self.sbc(self.bus.read(addr))
        elif opcode == 0xEE:  # INC Absolute
            addr = self.addr_absolute()
            val = (self.bus.read(addr) + 1) & 0xFF
            self.bus.write(addr, val)
            self.update_zn(val)
        elif opcode == 0xF0:  # BEQ
            offset = self.fetch_byte()
            if self.get_flag(FLAG_Z):
                cycles += 1
                new_pc = (self.PC + ((offset ^ 0x80) - 0x80)) & 0xFFFF
                if (new_pc & 0xFF00) != (self.PC & 0xFF00):
                    cycles += 1
                self.PC = new_pc
        elif opcode == 0xF1:  # SBC (Indirect),Y
            addr = self.addr_indirect_y(check_page_cross=True)
            self.sbc(self.bus.read(addr))
        elif opcode == 0xF5:  # SBC Zero Page,X
            addr = self.addr_zero_page_x()
            self.sbc(self.bus.read(addr))
        elif opcode == 0xF6:  # INC Zero Page,X
            addr = self.addr_zero_page_x()
            val = (self.bus.read(addr) + 1) & 0xFF
            self.bus.write(addr, val)
            self.update_zn(val)
        elif opcode == 0xF8:  # SED
            self.set_flag(FLAG_D, True)
        elif opcode == 0xF9:  # SBC Absolute,Y
            addr = self.addr_absolute_y(check_page_cross=True)
            self.sbc(self.bus.read(addr))
        elif opcode == 0xFD:  # SBC Absolute,X
            addr = self.addr_absolute_x(check_page_cross=True)
            self.sbc(self.bus.read(addr))
        elif opcode == 0xFE:  # INC Absolute,X
            addr = self.addr_absolute_x()
            val = (self.bus.read(addr) + 1) & 0xFF
            self.bus.write(addr, val)
            self.update_zn(val)
        else:
            # Unsupported/illegal opcode
            # For simplicity, we'll treat any unknown opcode as NOP
            # In a full emulator, you might implement unofficial opcodes or handle gracefully.
            pass
        
        return cycles

class Bus:
    """Memory bus connecting CPU, PPU, and Cartridge."""
    def __init__(self):
        # 2KB internal RAM
        self.ram = [0x00] * RAM_SIZE
        # PPU memory: 2KB nametable VRAM and 32-byte palette
        self.vram = [0x00] * 0x800  # will mirror based on cart mirroring type
        self.palette = [0x00] * 0x20
        # OAM (sprite memory)
        self.oam = [0x00] * 256
        # Cartridge ROM/RAM
        self.prg_rom = []   # PRG ROM bytes
        self.prg_ram = [0x00] * 0x2000  # 8KB PRG RAM (if used by cart)
        self.chr_rom = []   # CHR ROM bytes (pattern tables)
        self.chr_ram = []   # if CHR RAM is needed (for carts with 0 CHR ROM)
        # Mirroring type from cartridge ('H' or 'V')
        self.mirroring = 'H'
        # Controller state and shift registers
        self.controller_state = 0x00
        self.controller_shift = 0x00
        self.controller_strobe = False
        self.controller_index = 0
        # Other PPU registers
        self.ppu_ctrl = 0x00    # $2000
        self.ppu_mask = 0x00    # $2001
        self.ppu_status = 0x00  # $2002
        self.ppu_scroll_x = 0
        self.ppu_scroll_y = 0
        self.ppu_addr_temp = 0x0000
        self.ppu_addr_latch = False  # latch toggle for $2005/2006 writes
        # CPU
        self.cpu = CPU6502(self)
        # Cycle counter (not real time, just for managing frames)
        self.cycles = 0
    
    def load_cartridge(self, filepath):
        """Load an iNES format ROM file into memory."""
        with open(filepath, "rb") as f:
            data = f.read()
        # iNES header is 16 bytes
        if data[0:4] != b"NES\x1A":
            raise Exception("Not a valid iNES ROM file")
        prg_banks = data[4]
        chr_banks = data[5]
        flag6 = data[6]
        # flag6 bits: mirroring in bit0, battery in bit1, trainer in bit2, four-screen in bit3
        if flag6 & 0x08:
            # Four-screen mode (rare, e.g. Gauntlet). We will treat it as special mirroring.
            self.mirroring = '4'
        else:
            self.mirroring = 'V' if (flag6 & 0x01) else 'H'
        # Skip trainer if present (512 bytes after header)
        offset = 16
        if flag6 & 0x04:
            offset += 512
        # Load PRG ROM
        prg_size = prg_banks * 16384
        self.prg_rom = list(data[offset: offset + prg_size])
        offset += prg_size
        # Load CHR ROM (if size is 0, that means the cart uses CHR RAM instead)
        chr_size = chr_banks * 8192
        if chr_size == 0:
            # allocate 8KB CHR RAM
            self.chr_ram = [0x00] * 8192
            self.chr_rom = []
        else:
            self.chr_rom = list(data[offset: offset + chr_size])
        # If only one PRG bank (16KB), mirror it into 0xC000-0xFFFF
        if prg_banks == 1:
            self.prg_rom = self.prg_rom * 2
        # Reset CPU and clear memory
        self.ram = [0x00] * RAM_SIZE
        self.vram = [0x00] * 0x800
        self.palette = [0x00] * 0x20
        self.oam = [0x00] * 256
        self.cpu.reset()
        # Clear PPU scroll/addr toggles
        self.ppu_addr_latch = False
        # Clear controller
        self.controller_state = 0x00
        self.controller_shift = 0x00
        self.controller_strobe = False
        self.controller_index = 0
    
    # Memory read/write methods
    def read(self, addr):
        addr &= 0xFFFF
        if addr < 0x2000:
            # Internal RAM (2KB mirrored each 0x800 bytes)
            return self.ram[addr % RAM_SIZE]
        elif addr < 0x4000:
            # PPU registers (mirrored every 8 bytes)
            reg = addr & 0x2007
            if reg == 0x2002:  # PPUSTATUS
                # Reading PPUSTATUS: return status register, then clear vblank flag and address latch
                value = self.ppu_status
                # Clear VBlank flag (bit 7) after read
                self.ppu_status &= 0x7F
                # Reset latch for $2005/2006 writes
                self.ppu_addr_latch = False
                return value
            elif reg == 0x2004:  # OAMDATA
                # Read OAM at OAMADDR (OAMADDR is in bits 0-7 of ppu_ctrl? Actually in $2003 write-only)
                # For simplicity, we'll not simulate OAMADDR and just assume sequential reads are from start
                return self.oam[0]  # (not fully implemented)
            elif reg == 0x2007:  # PPUDATA
                # Reading from PPU memory
                # PPU address is held in ppu_addr_temp or internal latch? 
                # For simplicity, assume ppu_addr_temp holds the current VRAM address.
                addr = self.ppu_addr_temp & 0x3FFF
                # Palette reads:
                if addr >= 0x3F00:
                    # Read from palette memory (with mirroring of universal background)
                    index = addr & 0x1F
                    # Handle palette mirror: palette indices where index%4==0 all mirror the universal background at $3F00
                    if (index & 0x03) == 0:
                        index = 0
                    data = self.palette[index]
                else:
                    # Nametable or CHR memory:
                    if addr < 0x2000:
                        # Pattern table (CHR ROM/RAM)
                        if self.chr_rom:
                            data = self.chr_rom[addr]
                        else:
                            data = self.chr_ram[addr]
                    else:
                        # Nametable VRAM (2KB mirrored)
                        # Apply mirroring:
                        if self.mirroring == 'H':
                            # horizontal mirroring: mirror vertical, i.e., if addr >= 0x2800 subtract 0x0800
                            if addr & 0x0800:
                                addr = addr - 0x0800
                        elif self.mirroring == 'V':
                            # vertical mirroring: mirror horizontal, if addr in right half subtract 0x0400
                            if addr & 0x0400:
                                addr = addr - 0x0400
                        # else if '4' (four-screen), we would not mirror (but we didn't implement separate 4-screen memory)
                        addr_index = addr & 0x07FF
                        data = self.vram[addr_index]
                    # (For true accuracy, PPU reads have a buffered behavior, but we skip that.)
                # Increment VRAM address after read by 1 or 32 depending on $2000 setting
                if self.ppu_ctrl & 0x04:
                    self.ppu_addr_temp = (self.ppu_addr_temp + 32) & 0xFFFF
                else:
                    self.ppu_addr_temp = (self.ppu_addr_temp + 1) & 0xFFFF
                return data & 0xFF
            else:
                # Other PPU registers ($2000, $2001, $2003, $2005, $2006) are write-only or not readable
                return 0
        elif addr < 0x4020:
            # APU and I/O registers
            if addr == 0x4016:
                # Controller 1 polling
                if self.controller_strobe:
                    # If strobe is high, return A bit (bit0 of controller) constantly
                    bit = 1 if (self.controller_state & 0x01) else 0
                else:
                    # Return current shift register bit
                    bit = 1 if (self.controller_shift & 0x01) else 0
                    # Shift or keep index
                    if self.controller_index < 8:
                        self.controller_shift >>= 1
                        self.controller_index += 1
                    else:
                        bit = 1  # after 8 reads, NES returns 1 on subsequent reads
                return bit
            # Unused or unimplemented registers (sound, expansion) return 0
            return 0
        elif addr < 0x6000:
            # Normally cartridge expansion ROM or other hardware (uncommon)
            return 0
        elif addr < 0x8000:
            # Cartridge PRG RAM (if present)
            return self.prg_ram[addr - 0x6000]
        else:
            # Cartridge PRG ROM
            return self.prg_rom[addr - 0x8000]
    
    def write(self, addr, data):
        addr &= 0xFFFF
        data &= 0xFF
        if addr < 0x2000:
            # Internal RAM
            self.ram[addr % RAM_SIZE] = data
        elif addr < 0x4000:
            reg = addr & 0x2007
            if reg == 0x2000:  # PPUCTRL
                self.ppu_ctrl = data
                # Nametable selection bits (0-1) might affect scroll base
                # We'll incorporate this into scroll offsets when rendering.
            elif reg == 0x2001:  # PPUMASK
                self.ppu_mask = data
            elif reg == 0x2003:  # OAMADDR
                # Set OAM address (for writes via 0x2004). Not fully emulated.
                pass
            elif reg == 0x2004:  # OAMDATA
                # Write to OAM (sprite memory) at OAMADDR
                # We will simply write to first OAM entry for demo
                self.oam[0] = data
            elif reg == 0x2005:  # PPUSCROLL
                # First write sets scroll X, second sets scroll Y
                if not self.ppu_addr_latch:
                    # First write
                    # Horizontal scroll (3 lower bits fine X, 5 bits coarse X)
                    self.ppu_scroll_x = data
                    self.ppu_addr_latch = True
                else:
                    # Second write
                    self.ppu_scroll_y = data
                    self.ppu_addr_latch = False
            elif reg == 0x2006:  # PPUADDR
                # First write sets high byte, second sets low byte of VRAM address
                if not self.ppu_addr_latch:
                    # High 6 bits (only 14-bit address allowed)
                    self.ppu_addr_temp = ((data & 0x3F) << 8) | (self.ppu_addr_temp & 0x00FF)
                    self.ppu_addr_latch = True
                else:
                    self.ppu_addr_temp = (self.ppu_addr_temp & 0xFF00) | data
                    # After full address is set, we might use it for subsequent PPUDATA access
                    self.ppu_addr_latch = False
                # Note: We do not directly use ppu_addr_temp for rendering until needed.
            elif reg == 0x2007:  # PPUDATA (write)
                addr = self.ppu_addr_temp & 0x3FFF
                if addr >= 0x3F00:
                    # Palette write
                    index = addr & 0x1F
                    if (index & 0x03) == 0:
                        # Mirror universal background across all 0x??00,0x??04,0x??08,0x??0C, etc.
                        self.palette[0x00] = data
                        self.palette[0x04] = data
                        self.palette[0x08] = data
                        self.palette[0x0C] = data
                        self.palette[0x10] = data
                        self.palette[0x14] = data
                        self.palette[0x18] = data
                        self.palette[0x1C] = data
                    else:
                        self.palette[index] = data
                else:
                    if addr < 0x2000:
                        # CHR ROM/RAM write (usually CHR ROM is read-only; CHR RAM can be written)
                        if self.chr_rom:
                            # Typically CHR ROM is not writable; ignoring or could write to CHR RAM if used
                            pass
                        else:
                            self.chr_ram[addr] = data
                    else:
                        # Nametable VRAM write (with mirroring)
                        if self.mirroring == 'H':
                            if addr & 0x0800:
                                addr = addr - 0x0800
                        elif self.mirroring == 'V':
                            if addr & 0x0400:
                                addr = addr - 0x0400
                        index = addr & 0x07FF
                        self.vram[index] = data
                # Auto-increment VRAM address after write
                if self.ppu_ctrl & 0x04:
                    self.ppu_addr_temp = (self.ppu_addr_temp + 32) & 0xFFFF
                else:
                    self.ppu_addr_temp = (self.ppu_addr_temp + 1) & 0xFFFF
        elif addr < 0x4020:
            if addr == 0x4014:
                # OAMDMA: DMA transfer of 256 bytes from CPU memory page (data * 0x100) to OAM
                page = data
                start_addr = page * 0x100
                # Read 256 bytes from start_addr and write to OAM (starting at index 0)
                for i in range(256):
                    self.oam[i] = self.read((start_addr + i) & 0xFFFF)
                # During DMA, 513 or 514 CPU cycles occur (depending on alignment). For simplicity, ignore timing.
            elif addr == 0x4016:
                # Controller strobe
                self.controller_strobe = (data & 1) != 0
                if self.controller_strobe:
                    # When strobe is high, latch controller state and reset index
                    self.controller_shift = self.controller_state
                    self.controller_index = 0
                else:
                    # When strobe goes low, prepare to shift out bits (already latched above)
                    self.controller_shift = self.controller_state
                    self.controller_index = 0
            # Note: Sound registers ($4000-$4013, $4015, $4017) are not implemented.
        elif addr < 0x6000:
            # Expansion or other I/O, not used
            pass
        elif addr < 0x8000:
            # PRG RAM
            self.prg_ram[addr - 0x6000] = data
        else:
            # PRG ROM is typically read-only; writes might go to battery RAM on some carts (not in mapper0)
            pass

# NES Emulator main class tying it all together
class NESEmulator:
    def __init__(self):
        self.bus = Bus()
        self.cpu = self.bus.cpu
        # Initialize variables for rendering and vibe mode
        self.framebuffer = [0] * (SCREEN_WIDTH * SCREEN_HEIGHT)  # will hold pixel colors (RGB or palette index)
        self.vibe_mode = False
        self.vibe_offset = 0
    
    def load_rom(self, filepath):
        self.bus.load_cartridge(filepath)
    
    def reset(self):
        self.cpu.reset()
        # Clear PPU status flags
        self.bus.ppu_status = 0x00
    
    def step_frame(self):
        """Run the CPU until one frame's worth of CPU cycles have been executed, then render the frame."""
        cycles_per_frame = 29780  # ~29780 CPU cycles per frame for NTSC (approximation)
        self.bus.cycles = 0
        # Run CPU until we've simulated enough cycles for one frame
        while self.bus.cycles < cycles_per_frame:
            # Execute one CPU instruction
            cycles = self.cpu.execute_instruction()
            self.bus.cycles += cycles
            # PPU would normally run ~3 cycles per CPU, updating vblank, sprite hit, etc.
            # We simplify and handle vblank flag when frame completes.
        # At this point, we've simulated one frame of CPU time. Now produce the video output.
        self.render_frame()
        # Set the VBlank flag (PPUSTATUS bit 7) to indicate the frame has been drawn
        self.bus.ppu_status |= 0x80
        # In vibe mode, advance the color cycling
        if self.vibe_mode:
            self.vibe_offset = (self.vibe_offset + 1) % 64
    
    def render_frame(self):
        """Render the background and sprites into the framebuffer for the current PPU memory state."""
        # Determine base pattern table for background from PPUCTRL bit 4
        base_table = 0x1000 if (self.bus.ppu_ctrl & 0x10) else 0x0000
        # Extract scroll values (we combine fine and coarse scroll from registers)
        # In our implementation, scroll_x and scroll_y registers hold the values written via $2005
        coarse_scroll_x = (self.bus.ppu_scroll_x >> 3) & 0x1F  # 5-bit coarse scroll X (tile units)
        fine_scroll_x = self.bus.ppu_scroll_x & 0x07           # 3-bit fine scroll X (pixel offset within tile)
        coarse_scroll_y = (self.bus.ppu_scroll_y >> 3) & 0x1F
        fine_scroll_y = self.bus.ppu_scroll_y & 0x07
        # Nametable bits from $2000 (bits 0-1) might act as high bits of coarse X/Y for starting nametable
        nt_select = self.bus.ppu_ctrl & 0x03  # 0-3
        # Incorporate nametable selection into scroll origin
        # bit0 -> add 256 to scrollX if 1, bit1 -> add 240 to scrollY if 1
        scroll_x = coarse_scroll_x * 8 + fine_scroll_x + ((nt_select & 0x01) * 256)
        scroll_y = coarse_scroll_y * 8 + fine_scroll_y + ((nt_select & 0x02) * 240)
        # Iterate over each pixel of the 256x240 frame
        for py in range(SCREEN_HEIGHT):
            for px in range(SCREEN_WIDTH):
                # Calculate the corresponding nametable address and tile
                # Effective coordinates in the 512x480 nametable space (with wrap-around via mirroring)
                eff_x = (scroll_x + px) % 512
                eff_y = (scroll_y + py) % 480
                # Determine which nametable (0-3) these coords fall in (each nametable is 256x240)
                nt_index = (0 if eff_x < 256 else 1) + (0 if eff_y < 240 else 2)
                # Apply mirroring to map to physical nametable memory
                if self.bus.mirroring == 'H':
                    # Horizontal: nametables 0 and 1 are on top, 2 mirrors 0, 3 mirrors 1
                    if nt_index == 2: nt_index = 0
                    if nt_index == 3: nt_index = 1
                elif self.bus.mirroring == 'V':
                    # Vertical: nametables 0 and 2 are left, 1 mirrors 0, 3 mirrors 2
                    if nt_index == 1: nt_index = 0
                    if nt_index == 3: nt_index = 2
                elif self.bus.mirroring == '4':
                    # Four-screen (not fully implemented, treat as no mirroring)
                    pass
                # Compute indices within the nametable
                nx = eff_x % 256
                ny = eff_y % 240
                tile_col = nx // 8
                tile_row = ny // 8
                fine_x = nx % 8
                fine_y = ny % 8
                # Nametable base address for chosen nametable (0->0x2000,1->0x2400,2->0x2800,3->0x2C00)
                nt_base = 0x2000
                if nt_index == 1:
                    nt_base = 0x2400
                elif nt_index == 2:
                    nt_base = 0x2800
                elif nt_index == 3:
                    nt_base = 0x2C00
                # Nametable memory index of the tile number
                nametable_addr = nt_base + (tile_row * 32) + tile_col
                # Apply mirroring logic to fetch the correct nametable data from VRAM
                addr = nametable_addr
                if self.bus.mirroring == 'H':
                    if addr & 0x0800: addr -= 0x0800
                elif self.bus.mirroring == 'V':
                    if addr & 0x0400: addr -= 0x0400
                tile_index = self.bus.vram[addr & 0x07FF]
                # Pattern table address for this tile's graphics
                pattern_addr = base_table + tile_index * 16
                # Fetch the pattern table bytes for this tile row
                if pattern_addr < len(self.bus.chr_rom):
                    byte1 = self.bus.chr_rom[pattern_addr + fine_y]
                    byte2 = self.bus.chr_rom[pattern_addr + fine_y + 8]
                else:
                    # If CHR RAM or out-of-range, handle accordingly
                    if self.bus.chr_rom:
                        # If out-of-range CHR ROM address (shouldn't happen with correct tile_index)
                        byte1 = byte2 = 0
                    else:
                        # CHR RAM case
                        byte1 = self.bus.chr_ram[pattern_addr + fine_y]
                        byte2 = self.bus.chr_ram[pattern_addr + fine_y + 8]
                # Extract the bit corresponding to fine_x (bit7 = x=0)
                bit0 = (byte1 >> (7 - fine_x)) & 1
                bit1 = (byte2 >> (7 - fine_x)) & 1
                color_index = (bit1 << 1) | bit0
                # Determine palette index:
                if color_index == 0:
                    # Index 0 = background transparent pixel. Use universal background color from palette $3F00.
                    pal_index = self.bus.palette[0x00]
                else:
                    # Each background palette is 4 bytes: choose which palette based on attribute table.
                    # The attribute table is at $23C0 for nametable 0, etc. Each byte covers a 32x32 pixel area (4x4 tiles).
                    # We will simplify by using palette 0 for all for now.
                    pal_base = 0x01  # start at $3F01 (first background palette's first entry)
                    # In a full implementation, we'd fetch attribute bytes to choose palette 0-3.
                    pal_index = self.bus.palette[pal_base + ((color_index - 1) % 3)]
                # Apply vibe mode color cycling if enabled
                if self.vibe_mode:
                    pal_index = (pal_index + self.vibe_offset) & 0x3F
                # Convert palette index to actual RGB color
                rgb = NES_PALETTE[pal_index]
                # Store in framebuffer
                pos = py * SCREEN_WIDTH + px
                self.framebuffer[pos] = rgb
    
    def get_frame_image(self):
        """Return a Pillow Image for the current framebuffer."""
        # Create an RGB image from the framebuffer pixel data
        if Image is None:
            # If Pillow is not available, create a Tk PhotoImage with a color string (less efficient)
            # We'll build a color string per line for demonstration if needed.
            photo = tk.PhotoImage(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
            for y in range(SCREEN_HEIGHT):
                line = ""
                for x in range(SCREEN_WIDTH):
                    r, g, b = self.framebuffer[y*SCREEN_WIDTH + x]
                    line += "#%02x%02x%02x " % (r, g, b)
                photo.put(line, to=(0, y))
            return photo
        else:
            # Use Pillow to create image from data
            img = Image.new("RGB", (SCREEN_WIDTH, SCREEN_HEIGHT))
            img.putdata(self.framebuffer)
            return ImageTk.PhotoImage(img)


# --- Tkinter GUI Setup ---

class NESGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Python NES Emulator")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        # Create NES emulator core
        self.emulator = NESEmulator()
        # Flag to indicate if a ROM is loaded
        self.rom_loaded = False
        
        # Set up menu
        menubar = tk.Menu(root)
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open ROM...", command=self.open_rom)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        # Emulation menu
        emu_menu = tk.Menu(menubar, tearoff=0)
        emu_menu.add_command(label="Reset", command=self.reset_emulator)
        self.vibe_var = tk.BooleanVar(value=False)
        emu_menu.add_checkbutton(label="Vibe Mode", variable=self.vibe_var, command=self.toggle_vibe)
        menubar.add_cascade(label="Emulation", menu=emu_menu)
        # Debug menu
        debug_menu = tk.Menu(menubar, tearoff=0)
        debug_menu.add_command(label="CPU State", command=self.show_cpu_state)
        menubar.add_cascade(label="Debug", menu=debug_menu)
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menubar)
        
        # Canvas for display (scaled or centered to 600x400 if needed)
        self.canvas = tk.Canvas(root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, bg="black")
        # We'll place the canvas at the center of window 600x400
        self.canvas.place(x= (600-SCREEN_WIDTH)//2, y=(400-SCREEN_HEIGHT)//2)
        
        # Bind keyboard events for controller input
        root.bind("<KeyPress>", self.on_key_press)
        root.bind("<KeyRelease>", self.on_key_release)
        
        # Label to show a message or status (like "No ROM Loaded")
        self.status_label = tk.Label(root, text="Open a ROM to start", fg="gray")
        self.status_label.place(x=5, y=380)
        
        # Debug window handle
        self.cpu_window = None
    
    def open_rom(self):
        # Open file dialog to choose ROM
        filepath = filedialog.askopenfilename(filetypes=[("NES ROMs", "*.nes"), ("All Files", "*.*")])
        if not filepath:
            return
        try:
            self.emulator.load_rom(filepath)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load ROM:\n{e}")
            return
        self.rom_loaded = True
        self.status_label.config(text=f"Loaded ROM: {filepath.split('/')[-1]}")
        # Reset any debug windows
        if self.cpu_window:
            self.cpu_window.destroy()
            self.cpu_window = None
        # Start the emulation loop
        self.run_frame()
    
    def reset_emulator(self):
        if not self.rom_loaded:
            return
        self.emulator.reset()
        # Also reset vibe effect and update UI
        self.vibe_var.set(False)
        self.emulator.vibe_mode = False
        if self.cpu_window:
            self.update_cpu_window()
        # Continue running frames
        self.run_frame()
    
    def toggle_vibe(self):
        # Toggle vibe mode on/off
        self.emulator.vibe_mode = self.vibe_var.get()
    
    def show_cpu_state(self):
        # Create or focus a window showing CPU registers
        if self.cpu_window and tk.Toplevel.winfo_exists(self.cpu_window):
            # If already open, bring to front
            self.cpu_window.deiconify()
            self.cpu_window.lift()
            return
        self.cpu_window = tk.Toplevel(self.root)
        self.cpu_window.title("CPU State")
        self.cpu_window.geometry("200x150")
        # Labels to display registers
        self.cpu_state_label = tk.Label(self.cpu_window, justify="left", font=("Courier", 10))
        self.cpu_state_label.pack(padx=10, pady=10)
        # Update once to show initial state
        self.update_cpu_window()
    
    def update_cpu_window(self):
        if not self.rom_loaded or not self.cpu_window:
            return
        c = self.emulator.cpu
        status_flags = "".join([
            "N" if c.get_flag(FLAG_N) else ".",
            "V" if c.get_flag(FLAG_V) else ".",
            "U" if c.get_flag(FLAG_U) else ".",
            "B" if c.get_flag(FLAG_B) else ".",
            "D" if c.get_flag(FLAG_D) else ".",
            "I" if c.get_flag(FLAG_I) else ".",
            "Z" if c.get_flag(FLAG_Z) else ".",
            "C" if c.get_flag(FLAG_C) else ".",
        ])
        text = (f"PC: {c.PC:04X}\n"
                f"A: {c.A:02X}  X: {c.X:02X}  Y: {c.Y:02X}\n"
                f"SP: {c.SP:02X}\n"
                f"STATUS: {c.STATUS:02X} ({status_flags})")
        self.cpu_state_label.config(text=text)
    
    def show_about(self):
        messagebox.showinfo("About", "NES Emulator in Python\nInspired by NESticle\n\nKeys: Arrows = D-Pad, Z = A, X = B, Enter = Start, Shift = Select")
    
    def on_key_press(self, event):
        # Set controller bits on key press
        if not self.rom_loaded:
            return
        # Map keys to controller bits
        if event.keysym == 'z' or event.keysym == 'Z':
            self.emulator.bus.controller_state |= BUTTON_A
        elif event.keysym == 'x' or event.keysym == 'X':
            self.emulator.bus.controller_state |= BUTTON_B
        elif event.keysym == 'Shift_R' or event.keysym == 'Shift_L':
            # Use Right Shift or Left Shift for Select
            self.emulator.bus.controller_state |= BUTTON_SELECT
        elif event.keysym == 'Return':
            self.emulator.bus.controller_state |= BUTTON_START
        elif event.keysym == 'Up':
            self.emulator.bus.controller_state |= BUTTON_UP
        elif event.keysym == 'Down':
            self.emulator.bus.controller_state |= BUTTON_DOWN
        elif event.keysym == 'Left':
            self.emulator.bus.controller_state |= BUTTON_LEFT
        elif event.keysym == 'Right':
            self.emulator.bus.controller_state |= BUTTON_RIGHT
    
    def on_key_release(self, event):
        # Clear controller bits on key release
        if not self.rom_loaded:
            return
        if event.keysym == 'z' or event.keysym == 'Z':
            self.emulator.bus.controller_state &= ~BUTTON_A
        elif event.keysym == 'x' or event.keysym == 'X':
            self.emulator.bus.controller_state &= ~BUTTON_B
        elif event.keysym == 'Shift_R' or event.keysym == 'Shift_L':
            self.emulator.bus.controller_state &= ~BUTTON_SELECT
        elif event.keysym == 'Return':
            self.emulator.bus.controller_state &= ~BUTTON_START
        elif event.keysym == 'Up':
            self.emulator.bus.controller_state &= ~BUTTON_UP
        elif event.keysym == 'Down':
            self.emulator.bus.controller_state &= ~BUTTON_DOWN
        elif event.keysym == 'Left':
            self.emulator.bus.controller_state &= ~BUTTON_LEFT
        elif event.keysym == 'Right':
            self.emulator.bus.controller_state &= ~BUTTON_RIGHT
    
    def run_frame(self):
        # Run one frame of emulation and schedule the next
        if not self.rom_loaded:
            return
        self.emulator.step_frame()
        # Update canvas with new frame
        frame_image = self.emulator.get_frame_image()
        # Keep a reference to avoid garbage collection of image
        self.canvas.image = frame_image
        self.canvas.create_image(0, 0, anchor=tk.NW, image=frame_image)
        # Update debug window if open
        if self.cpu_window:
            self.update_cpu_window()
        # Schedule next frame (we'll use a small delay to allow UI events)
        self.root.after(1, self.run_frame)

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    gui = NESGUI(root)
    root.mainloop()
