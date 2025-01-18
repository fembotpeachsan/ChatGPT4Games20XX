; ----------------------------------------------------------------------------
; NES ROM Header (iNES format)
; ----------------------------------------------------------------------------
.segment "HEADER"
    .byte "NES", $1A   ; Signature
    .byte 1            ; Number of 16KB PRG-ROM banks
    .byte 1            ; Number of 8KB CHR-ROM banks
    .byte $00          ; Flags 6
    .byte $00          ; Flags 7
    .byte $00, $00, $00 ; Unused padding

; ----------------------------------------------------------------------------
; Segments
; ----------------------------------------------------------------------------
.segment "CODE"
.org $8000            ; Start of PRG-ROM

; ----------------------------------------------------------------------------
; Zero Page / Variables
; ----------------------------------------------------------------------------
.segment "BSS"
.nmi_flag: .res 1     ; Set to nonzero each NMI (vertical blank)
.color_index: .res 1  ; Tracks which background color is active

; ----------------------------------------------------------------------------
; Read-Only Data (Palette, etc.)
; ----------------------------------------------------------------------------
.segment "RODATA"

; A small palette: 4 background colors. The rest are placeholder.
; $3F00-$3F0F = background + sprite palettes
palette:
    .byte $22, $01, $11, $21  ; Background palette (4 entries)
    .byte $0F, $00, $10, $30  ; Sprite palette 1
    .byte $0F, $06, $16, $26  ; Sprite palette 2
    .byte $0F, $09, $19, $29  ; Sprite palette 3

; Some background colors we can cycle through when pressing A (just a few NES color values)
bg_colors:
    .byte $22, $0F, $30, $16

; ----------------------------------------------------------------------------
; RESET Routine
; ----------------------------------------------------------------------------
.segment "CODE"

RESET:
    SEI              ; Disable interrupts
    CLD              ; Clear decimal mode

    LDX #$FF         ; Initialize stack pointer
    TXS

    ; Basic PPU setup:
    LDA #$00
    STA $2000        ; Disable NMI for a moment, no background/sprite
    STA $2001

    ; Clear OAM (sprite) memory just in case
    LDA #$00
    LDX #$00
clearOAM:
    STA $2003
    STA $2004
    INX
    BNE clearOAM

    ; Initialize variables
    LDA #$00
    STA nmi_flag
    STA color_index

    ; Enable NMI and turn on background:
    ; bit 7 of $2000 = 1 => Enable NMI
    ; bit 3 of $2001 = 1 => Show background
    LDA #%10000000
    STA $2000
    LDA #%00001000
    STA $2001

    CLI              ; Enable interrupts

main_loop:
    JSR wait_vblank  ; Wait for vertical blank
    JSR read_input   ; Check controller input
    JMP main_loop

; ----------------------------------------------------------------------------
; Subroutines
; ----------------------------------------------------------------------------

; Waits for the next NMI (vertical blank)
wait_vblank:
    ; Wait for NMI to set nmi_flag
    LDA nmi_flag
    BEQ wait_vblank
    STA nmi_flag     ; Clear the flag
    RTS

; Reads the first controller (at $4016), checks for "A button" to cycle color
read_input:
    ; Strobe the controller (write 1 then 0 to $4016)
    LDA #$01
    STA $4016
    LDA #$00
    STA $4016

    ; Read 8 bits for controller 1
    LDX #8
read_bits:
    LDA $4016        ; A = bit0 of controller state
    AND #$01         ; Isolate the lowest bit
    BNE button_pressed
next_bit:
    LSR A            ; shift out that bit (not truly necessary here)
    DEX
    BNE read_bits
    RTS

button_pressed:
    ; If we detect ANY button, cycle the color
    JSR cycle_color
    JMP next_bit

; Cycles the background color by writing new entry to $3F00
cycle_color:
    INC color_index
    LDA color_index
    AND #$03              ; Limit to 0..3
    STA color_index

    TAX                   ; X = color_index
    LDA bg_colors, X      ; Load next background color
    ; We must safely write to PPU in vblank:
    ; Set PPU address to $3F00 (background color)
    LDA #$3F
    STA $2006
    LDA #$00
    STA $2006

    ; Now write the color
    LDA bg_colors, X
    STA $2007

    RTS

; ----------------------------------------------------------------------------
; NMI Handler (Executes each vertical blank)
; ----------------------------------------------------------------------------
NMI:
    ; Set flag to signal vblank
    INC nmi_flag
    RTI

; ----------------------------------------------------------------------------
; IRQ Handler
; ----------------------------------------------------------------------------
IRQ:
    RTI

; ----------------------------------------------------------------------------
; Interrupt Vectors
; ----------------------------------------------------------------------------
.segment "VECTORS"
    .word NMI       ; NMI vector
    .word RESET     ; Reset vector
    .word IRQ       ; IRQ/BRK vector
