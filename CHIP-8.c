/******************************************************************************
 * CHIP-8 Emulator - "Whole Engine" Example
 * 
 * This is a single-file emulator in C that implements:
 *   - Classic Chip-8 opcodes
 *   - Timers (delay & sound)
 *   - Graphics via SDL2 (64x32 monochrome display)
 *   - Keyboard input mapping for 16 keys
 *
 * To compile (on Linux/macOS, with SDL2 installed):
 *   gcc chip8_emulator.c -o chip8_emulator -lSDL2 -O2
 *   ./chip8_emulator roms/YourGame.ch8
 *
 * On Windows (MinGW), similar:
 *   gcc chip8_emulator.c -IC:/SDL2/include -LC:/SDL2/lib -lSDL2 -o chip8_emulator.exe
 * 
 * This is a reference implementation and can be improved for better performance,
 * debugging, etc. Enjoy hacking on it!
 *****************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <SDL2/SDL.h>

/* --------------------- Chip-8 Constants --------------------- */
#define MEMORY_SIZE   4096
#define NUM_REGISTERS 16
#define STACK_SIZE    16
#define KEYPAD_SIZE   16
#define VIDEO_WIDTH   64
#define VIDEO_HEIGHT  32
#define VIDEO_SIZE    (VIDEO_WIDTH * VIDEO_HEIGHT)

/* Typically, Chip-8 programs start at 0x200 */
#define START_ADDRESS 0x200

/* Fontset is placed in memory at 0x50 by convention (80 bytes) */
static const uint8_t chip8_fontset[80] = {
    0xF0, 0x90, 0x90, 0x90, 0xF0, // 0
    0x20, 0x60, 0x20, 0x20, 0x70, // 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0, // 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0, // 3
    0x90, 0x90, 0xF0, 0x10, 0x10, // 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0, // 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0, // 6
    0xF0, 0x10, 0x20, 0x40, 0x40, // 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0, // 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0, // 9
    0xF0, 0x90, 0xF0, 0x90, 0x90, // A
    0xE0, 0x90, 0xE0, 0x90, 0xE0, // B
    0xF0, 0x80, 0x80, 0x80, 0xF0, // C
    0xE0, 0x90, 0x90, 0x90, 0xE0, // D
    0xF0, 0x80, 0xF0, 0x80, 0xF0, // E
    0xF0, 0x80, 0xF0, 0x80, 0x80  // F
};

/* -------------- Chip-8 Emulator Structure -------------- */
typedef struct {
    uint8_t  memory[MEMORY_SIZE];      // 4K memory
    uint8_t  V[NUM_REGISTERS];         // 16 registers (V0-VF)
    uint16_t I;                        // Index register
    uint16_t pc;                       // Program counter
    uint16_t stack[STACK_SIZE];        // Call stack
    uint8_t  sp;                       // Stack pointer
    uint8_t  delay_timer;              // Delay timer
    uint8_t  sound_timer;              // Sound timer
    uint8_t  keypad[KEYPAD_SIZE];      // 16-key hex keypad
    uint8_t  video[VIDEO_SIZE];        // 64x32 monochrome display buffer
    uint16_t opcode;                   // Current opcode
} Chip8;

/* -------------- SDL Window/Renderer Settings -------------- */
static const int WINDOW_SCALE = 10; // Each Chip-8 pixel => 10×10 screen pixels
static SDL_Window   *window   = NULL;
static SDL_Renderer *renderer = NULL;

/* -------------- Function Prototypes -------------- */
bool  initSDL(void);
void  destroySDL(void);
void  chip8_init(Chip8 *chip8);
void  chip8_loadROM(Chip8 *chip8, const char *filename);
void  chip8_emulateCycle(Chip8 *chip8);
void  chip8_executeOpcode(Chip8 *chip8);
void  chip8_drawVideo(Chip8 *chip8);
void  chip8_handleInput(Chip8 *chip8);

/* --------------- SDL Setup --------------- */
bool initSDL(void) {
    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_AUDIO | SDL_INIT_TIMER) < 0) {
        fprintf(stderr, "SDL could not initialize! SDL_Error: %s\n", SDL_GetError());
        return false;
    }

    window = SDL_CreateWindow("Chip-8 Emulator",
                              SDL_WINDOWPOS_CENTERED,
                              SDL_WINDOWPOS_CENTERED,
                              VIDEO_WIDTH  * WINDOW_SCALE,
                              VIDEO_HEIGHT * WINDOW_SCALE,
                              SDL_WINDOW_SHOWN);

    if (!window) {
        fprintf(stderr, "Window could not be created! SDL_Error: %s\n", SDL_GetError());
        return false;
    }

    renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    if (!renderer) {
        fprintf(stderr, "Renderer could not be created! SDL Error: %s\n", SDL_GetError());
        return false;
    }

    // Set logical size so we can easily draw the 64×32 grid scaled up
    SDL_RenderSetLogicalSize(renderer, VIDEO_WIDTH, VIDEO_HEIGHT);

    return true;
}

void destroySDL(void) {
    if (renderer) SDL_DestroyRenderer(renderer);
    if (window)   SDL_DestroyWindow(window);
    SDL_Quit();
}

/* --------------- Chip-8 Initialization --------------- */
void chip8_init(Chip8 *chip8) {
    memset(chip8->memory, 0, MEMORY_SIZE);
    memset(chip8->V, 0, NUM_REGISTERS);
    memset(chip8->video, 0, VIDEO_SIZE);
    memset(chip8->stack, 0, STACK_SIZE * sizeof(uint16_t));
    memset(chip8->keypad, 0, KEYPAD_SIZE);

    chip8->pc     = START_ADDRESS;
    chip8->opcode = 0;
    chip8->I      = 0;
    chip8->sp     = 0;
    chip8->delay_timer = 0;
    chip8->sound_timer = 0;

    // Load fontset into memory (beginning at 0x50)
    for (int i = 0; i < 80; i++) {
        chip8->memory[0x50 + i] = chip8_fontset[i];
    }

    // Seed random number generator (for opcode 0xC000)
    srand((unsigned int)time(NULL));
}

/* --------------- Loading a ROM into Memory --------------- */
void chip8_loadROM(Chip8 *chip8, const char *filename) {
    FILE *rom = fopen(filename, "rb");
    if (!rom) {
        fprintf(stderr, "Failed to open ROM: %s\n", filename);
        exit(EXIT_FAILURE);
    }

    // Read ROM into memory starting at 0x200
    fread(&chip8->memory[START_ADDRESS], 1, MEMORY_SIZE - START_ADDRESS, rom);
    fclose(rom);
}

/* --------------- Emulate One CPU Cycle --------------- */
void chip8_emulateCycle(Chip8 *chip8) {
    // Fetch opcode (2 bytes)
    chip8->opcode = (chip8->memory[chip8->pc] << 8) | chip8->memory[chip8->pc + 1];

    // Increment PC before we execute anything
    chip8->pc += 2;

    // Decode & execute opcode
    chip8_executeOpcode(chip8);

    // Update timers
    if (chip8->delay_timer > 0) {
        chip8->delay_timer--;
    }
    if (chip8->sound_timer > 0) {
        if (chip8->sound_timer == 1) {
            // Simple beep or console message
            fprintf(stderr, "BEEP!\n");
        }
        chip8->sound_timer--;
    }
}

/* --------------- Execute Current Opcode --------------- */
void chip8_executeOpcode(Chip8 *chip8) {
    switch (chip8->opcode & 0xF000) {
        case 0x0000:
        {
            switch (chip8->opcode & 0x00FF) {
                case 0x00E0: 
                    // 00E0: Clear the display
                    memset(chip8->video, 0, VIDEO_SIZE);
                    break;

                case 0x00EE:
                    // 00EE: Return from a subroutine
                    chip8->sp--;
                    chip8->pc = chip8->stack[chip8->sp];
                    break;

                default:
                    // Some older Chip-8 environments had more calls (0x0NNN), 
                    // but generally not used.
                    fprintf(stderr, "Unknown opcode [0x0000]: 0x%X\n", chip8->opcode);
                    break;
            }
        } break;

        case 0x1000:
            // 1NNN: Jump to address NNN
            chip8->pc = chip8->opcode & 0x0FFF;
            break;

        case 0x2000:
            // 2NNN: Call subroutine at NNN
            chip8->stack[chip8->sp] = chip8->pc;
            chip8->sp++;
            chip8->pc = chip8->opcode & 0x0FFF;
            break;

        case 0x3000:
        {
            // 3XNN: Skip next instruction if Vx == NN
            uint8_t x  = (chip8->opcode & 0x0F00) >> 8;
            uint8_t nn =  chip8->opcode & 0x00FF;
            if (chip8->V[x] == nn) {
                chip8->pc += 2;
            }
        } break;

        case 0x4000:
        {
            // 4XNN: Skip next instruction if Vx != NN
            uint8_t x  = (chip8->opcode & 0x0F00) >> 8;
            uint8_t nn =  chip8->opcode & 0x00FF;
            if (chip8->V[x] != nn) {
                chip8->pc += 2;
            }
        } break;

        case 0x5000:
        {
            // 5XY0: Skip next instruction if Vx == Vy
            uint8_t x = (chip8->opcode & 0x0F00) >> 8;
            uint8_t y = (chip8->opcode & 0x00F0) >> 4;
            if (chip8->V[x] == chip8->V[y]) {
                chip8->pc += 2;
            }
        } break;

        case 0x6000:
        {
            // 6XNN: Set Vx = NN
            uint8_t x  = (chip8->opcode & 0x0F00) >> 8;
            uint8_t nn =  chip8->opcode & 0x00FF;
            chip8->V[x] = nn;
        } break;

        case 0x7000:
        {
            // 7XNN: Set Vx = Vx + NN
            uint8_t x  = (chip8->opcode & 0x0F00) >> 8;
            uint8_t nn =  chip8->opcode & 0x00FF;
            chip8->V[x] += nn;
        } break;

        case 0x8000:
        {
            // 8XY_: Arithmetic and bitwise ops
            uint8_t x = (chip8->opcode & 0x0F00) >> 8;
            uint8_t y = (chip8->opcode & 0x00F0) >> 4;
            switch (chip8->opcode & 0x000F) {
                case 0x0: // 8XY0: Vx = Vy
                    chip8->V[x] = chip8->V[y];
                    break;
                case 0x1: // 8XY1: Vx = Vx OR Vy
                    chip8->V[x] |= chip8->V[y];
                    break;
                case 0x2: // 8XY2: Vx = Vx AND Vy
                    chip8->V[x] &= chip8->V[y];
                    break;
                case 0x3: // 8XY3: Vx = Vx XOR Vy
                    chip8->V[x] ^= chip8->V[y];
                    break;
                case 0x4: // 8XY4: Vx = Vx + Vy, VF = carry
                {
                    uint16_t sum = chip8->V[x] + chip8->V[y];
                    chip8->V[0xF] = (sum > 0xFF) ? 1 : 0;
                    chip8->V[x]   = sum & 0xFF;
                } break;
                case 0x5: // 8XY5: Vx = Vx - Vy, VF = NOT borrow
                {
                    chip8->V[0xF] = (chip8->V[x] >= chip8->V[y]) ? 1 : 0;
                    chip8->V[x]   = chip8->V[x] - chip8->V[y];
                } break;
                case 0x6: // 8XY6: Vx = Vx >> 1, VF = LSB of Vx before shift
                {
                    chip8->V[0xF] = chip8->V[x] & 0x01;
                    chip8->V[x] >>= 1;
                } break;
                case 0x7: // 8XY7: Vx = Vy - Vx, VF = NOT borrow
                {
                    chip8->V[0xF] = (chip8->V[y] >= chip8->V[x]) ? 1 : 0;
                    chip8->V[x]   = chip8->V[y] - chip8->V[x];
                } break;
                case 0xE: // 8XYE: Vx = Vx << 1, VF = MSB of Vx before shift
                {
                    chip8->V[0xF] = (chip8->V[x] & 0x80) >> 7;
                    chip8->V[x] <<= 1;
                } break;
                default:
                    fprintf(stderr, "Unknown opcode [0x8000]: 0x%X\n", chip8->opcode);
                    break;
            }
        } break;

        case 0x9000:
        {
            // 9XY0: Skip next instruction if Vx != Vy
            uint8_t x = (chip8->opcode & 0x0F00) >> 8;
            uint8_t y = (chip8->opcode & 0x00F0) >> 4;
            if (chip8->V[x] != chip8->V[y]) {
                chip8->pc += 2;
            }
        } break;

        case 0xA000:
            // ANNN: Set I = NNN
            chip8->I = chip8->opcode & 0x0FFF;
            break;

        case 0xB000:
            // BNNN: Jump to address NNN + V0
            chip8->pc = (chip8->opcode & 0x0FFF) + chip8->V[0];
            break;

        case 0xC000:
        {
            // CXNN: Set Vx = random byte & NN
            uint8_t x  = (chip8->opcode & 0x0F00) >> 8;
            uint8_t nn =  chip8->opcode & 0x00FF;
            chip8->V[x] = (rand() % 256) & nn;
        } break;

        case 0xD000:
        {
            // DXYN: Display/draw sprite at (Vx, Vy) with N bytes of sprite data
            //       VF = collision
            uint8_t x   = chip8->V[(chip8->opcode & 0x0F00) >> 8];
            uint8_t y   = chip8->V[(chip8->opcode & 0x00F0) >> 4];
            uint8_t rows= chip8->opcode & 0x000F;

            chip8->V[0xF] = 0; // Reset collision flag

            for (int row = 0; row < rows; row++) {
                uint8_t spriteByte = chip8->memory[chip8->I + row];

                for (int col = 0; col < 8; col++) {
                    uint8_t spritePixel = (spriteByte >> (7 - col)) & 1;
                    uint16_t index = ((y + row) % VIDEO_HEIGHT) * VIDEO_WIDTH + ((x + col) % VIDEO_WIDTH);

                    if (spritePixel) {
                        // If pixel is set, check if there's a collision
                        if (chip8->video[index] == 1) {
                            chip8->V[0xF] = 1;
                        }
                        chip8->video[index] ^= 1; // XOR
                    }
                }
            }
        } break;

        case 0xE000:
        {
            // EX9E or EXA1: Key handling
            uint8_t x = (chip8->opcode & 0x0F00) >> 8;
            switch (chip8->opcode & 0x00FF) {
                case 0x9E:
                    // EX9E: Skip next instruction if key with the value of Vx is pressed
                    if (chip8->keypad[chip8->V[x]]) {
                        chip8->pc += 2;
                    }
                    break;
                case 0xA1:
                    // EXA1: Skip next instruction if key with the value of Vx is NOT pressed
                    if (!chip8->keypad[chip8->V[x]]) {
                        chip8->pc += 2;
                    }
                    break;
                default:
                    fprintf(stderr, "Unknown opcode [0xE000]: 0x%X\n", chip8->opcode);
                    break;
            }
        } break;

        case 0xF000:
        {
            // Many sub-commands
            uint8_t x = (chip8->opcode & 0x0F00) >> 8;
            switch (chip8->opcode & 0x00FF) {
                case 0x07:
                    // FX07: Set Vx = delay timer
                    chip8->V[x] = chip8->delay_timer;
                    break;
                case 0x0A:
                {
                    // FX0A: Wait for a key press, store the value of the key in Vx
                    // This effectively pauses until a key is pressed
                    bool key_pressed = false;
                    for (int i = 0; i < KEYPAD_SIZE; i++) {
                        if (chip8->keypad[i]) {
                            chip8->V[x] = i;
                            key_pressed = true;
                            break;
                        }
                    }
                    // If no key is pressed, backtrack the PC so we re-run FX0A
                    if (!key_pressed) {
                        chip8->pc -= 2;
                    }
                } break;
                case 0x15:
                    // FX15: Set delay timer = Vx
                    chip8->delay_timer = chip8->V[x];
                    break;
                case 0x18:
                    // FX18: Set sound timer = Vx
                    chip8->sound_timer = chip8->V[x];
                    break;
                case 0x1E:
                    // FX1E: Set I = I + Vx
                    chip8->I += chip8->V[x];
                    break;
                case 0x29:
                    // FX29: Set I = location of sprite for digit Vx
                    // Each digit is 5 bytes, starting at 0x50
                    chip8->I = 0x50 + (chip8->V[x] * 5);
                    break;
                case 0x33:
                {
                    // FX33: Store BCD representation of Vx in memory at I, I+1, I+2
                    // Vx = ABC => [I]   = A, [I+1] = B, [I+2] = C
                    uint8_t value = chip8->V[x];
                    chip8->memory[chip8->I + 2] = value % 10; value /= 10;
                    chip8->memory[chip8->I + 1] = value % 10; value /= 10;
                    chip8->memory[chip8->I + 0] = value % 10;
                } break;
                case 0x55:
                {
                    // FX55: Store V0 to Vx in memory starting at I
                    for (int i = 0; i <= x; i++) {
                        chip8->memory[chip8->I + i] = chip8->V[i];
                    }
                    // In the original Chip-8, I = I + x + 1 is *not* done, 
                    // but in some modern interpreters it is. We'll skip changing I.
                } break;
                case 0x65:
                {
                    // FX65: Read V0 to Vx from memory starting at I
                    for (int i = 0; i <= x; i++) {
                        chip8->V[i] = chip8->memory[chip8->I + i];
                    }
                    // Same note about I applies here as above.
                } break;
                default:
                    fprintf(stderr, "Unknown opcode [0xF000]: 0x%X\n", chip8->opcode);
                    break;
            }
        } break;

        default:
            fprintf(stderr, "Unknown opcode: 0x%X\n", chip8->opcode);
            break;
    }
}

/* --------------- Draw the 64×32 Video Buffer via SDL --------------- */
void chip8_drawVideo(Chip8 *chip8) {
    SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255); // black
    SDL_RenderClear(renderer);

    // Draw each pixel: white if 1, black if 0
    SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255);
    for (int row = 0; row < VIDEO_HEIGHT; row++) {
        for (int col = 0; col < VIDEO_WIDTH; col++) {
            int pixelIndex = row * VIDEO_WIDTH + col;
            if (chip8->video[pixelIndex]) {
                // Draw 1×1 pixel (SDL logical size is 64×32, 
                // so this will be scaled to WINDOW_SCALE)
                SDL_Rect r;
                r.x = col;
                r.y = row;
                r.w = 1;
                r.h = 1;
                SDL_RenderFillRect(renderer, &r);
            }
        }
    }

    SDL_RenderPresent(renderer);
}

/* --------------- Handle Input (Keyboard) ---------------
 * We map typical hex keys to keyboard keys:
 *   1 2 3 4    -> 1 2 3 4
 *   Q W E R    -> Q W E R
 *   A S D F    -> A S D F
 *   Z X C V    -> Z X C V
 * Adjust as desired.
 */
void chip8_handleInput(Chip8 *chip8) {
    SDL_Event event;
    while (SDL_PollEvent(&event)) {
        if (event.type == SDL_QUIT) {
            exit(EXIT_SUCCESS);
        } 
        else if (event.type == SDL_KEYDOWN) {
            switch (event.key.keysym.sym) {
                case SDLK_1: chip8->keypad[0x1] = 1; break;
                case SDLK_2: chip8->keypad[0x2] = 1; break;
                case SDLK_3: chip8->keypad[0x3] = 1; break;
                case SDLK_4: chip8->keypad[0xC] = 1; break;

                case SDLK_q: chip8->keypad[0x4] = 1; break;
                case SDLK_w: chip8->keypad[0x5] = 1; break;
                case SDLK_e: chip8->keypad[0x6] = 1; break;
                case SDLK_r: chip8->keypad[0xD] = 1; break;

                case SDLK_a: chip8->keypad[0x7] = 1; break;
                case SDLK_s: chip8->keypad[0x8] = 1; break;
                case SDLK_d: chip8->keypad[0x9] = 1; break;
                case SDLK_f: chip8->keypad[0xE] = 1; break;

                case SDLK_z: chip8->keypad[0xA] = 1; break;
                case SDLK_x: chip8->keypad[0x0] = 1; break;
                case SDLK_c: chip8->keypad[0xB] = 1; break;
                case SDLK_v: chip8->keypad[0xF] = 1; break;

                case SDLK_ESCAPE: exit(EXIT_SUCCESS); // Quit on ESC
                default: break;
            }
        } 
        else if (event.type == SDL_KEYUP) {
            switch (event.key.keysym.sym) {
                case SDLK_1: chip8->keypad[0x1] = 0; break;
                case SDLK_2: chip8->keypad[0x2] = 0; break;
                case SDLK_3: chip8->keypad[0x3] = 0; break;
                case SDLK_4: chip8->keypad[0xC] = 0; break;

                case SDLK_q: chip8->keypad[0x4] = 0; break;
                case SDLK_w: chip8->keypad[0x5] = 0; break;
                case SDLK_e: chip8->keypad[0x6] = 0; break;
                case SDLK_r: chip8->keypad[0xD] = 0; break;

                case SDLK_a: chip8->keypad[0x7] = 0; break;
                case SDLK_s: chip8->keypad[0x8] = 0; break;
                case SDLK_d: chip8->keypad[0x9] = 0; break;
                case SDLK_f: chip8->keypad[0xE] = 0; break;

                case SDLK_z: chip8->keypad[0xA] = 0; break;
                case SDLK_x: chip8->keypad[0x0] = 0; break;
                case SDLK_c: chip8->keypad[0xB] = 0; break;
                case SDLK_v: chip8->keypad[0xF] = 0; break;
                default: break;
            }
        }
    }
}

/* --------------- main() --------------- */
int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <Chip8 ROM>\n", argv[0]);
        return EXIT_FAILURE;
    }

    // Initialize SDL
    if (!initSDL()) {
        return EXIT_FAILURE;
    }

    // Create Chip-8 instance & load ROM
    Chip8 chip8;
    chip8_init(&chip8);
    chip8_loadROM(&chip8, argv[1]);

    // Emulation parameters
    const int FPS = 60; 
    const int frameDelay = 1000 / FPS; 
    uint32_t frameStart;
    int frameTime;

    // Main loop
    while (true) {
        frameStart = SDL_GetTicks();

        // Process input (updates chip8->keypad)
        chip8_handleInput(&chip8);

        // Run one CPU cycle
        chip8_emulateCycle(&chip8);

        // Draw video buffer
        chip8_drawVideo(&chip8);

        // Limit to ~60 Hz
        frameTime = SDL_GetTicks() - frameStart;
        if (frameDelay > frameTime) {
            SDL_Delay(frameDelay - frameTime);
        }
    }

    // Clean up
    destroySDL();
    return 0;
}
