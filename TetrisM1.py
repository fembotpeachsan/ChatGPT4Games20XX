import sys
import pygame
import random
import numpy as np

# Initialize Pygame and mixer with desired audio settings (44100 Hz, 16-bit, mono, small buffer)
pygame.mixer.pre_init(frequency=44100, size=-16, channels=1, buffer=512)
pygame.init()

# Game window dimensions
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 25

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)
GREEN = (0, 255, 0)
COLORS = [RED, BLUE, GREEN]  # colors for pieces (randomly chosen for each tetromino)

# Tetromino shapes (each shape is a list of rotations, each rotation is a 5x5 grid of 'O' and '.')
SHAPES = [
    [   # I shape
        ['.....',
         '.....',
         '.....',
         'OOOO.',  # horizontal I
         '.....'],
        ['.....',
         '..O..',
         '..O..',
         '..O..',  # vertical I
         '..O..']
    ],
    [   # T shape
        ['.....',
         '.....',
         '..O..',
         '.OOO.',  # T pointing up
         '.....'],
        ['.....',
         '..O..',
         '.OO..',
         '..O..',
         '.....'],
        ['.....',
         '.....',
         '.OOO.',
         '..O..',  # T pointing down
         '.....'],
        ['.....',
         '..O..',
         '..OO.',
         '..O..',
         '.....']
    ],
    [   # Z shape
        ['.....',
         '.....',
         '..OO.',
         '.OO..',  # Z shape
         '.....'],
        ['.....',
         '.....',
         '.OO..',
         '..OO.',
         '.....']
    ],
    [   # S shape
        ['.....',
         '.....',
         '.OO..',
         '..OO.',  # S shape
         '.....'],
        ['.....',
         '.....',
         '..OO.',
         '.OO..',
         '.....']
    ],
    [   # L shape
        ['.....',
         '..O..',
         '..O..',
         '..OO.',  # L pointing right
         '.....'],
        ['.....',
         '...O.',
         '.OOO.',  # L pointing down
         '.....',
         '.....'],
        ['.....',
         '.OO..',
         '.O...',
         '.O...',  # L pointing left (rotated 180)
         '.....'],
        ['.....',
         '.....',
         '.OOO.',
         '...O.',  # L pointing up
         '.....']
    ],
    [   # J shape (mirror of L)
        ['.....',
         '..O..',
         '..O..',
         '.OO..',  # J pointing left
         '.....'],
        ['.....',
         '.O...',
         '.OOO.',  # J pointing down
         '.....',
         '.....'],
        ['.....',
         '..OO.',
         '...O.',
         '...O.',  # J pointing right (rotated 180)
         '.....'],
        ['.....',
         '.....',
         '.OOO.',
         '.O...',  # J pointing up
         '.....']
    ],
    [   # O shape (square)
         ['.....',
          '.....',
          '.OO..',
          '.OO..',
          '.....']  # square (same in all rotations)
    ]
]

# Audio generation settings
SAMPLE_RATE = 44100

def generate_wave(frequency, duration, waveform='sine'):
    """Generate a waveform (sine or square or noise) for given frequency and duration."""
    length = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, length, endpoint=False)
    if waveform == 'sine':
        wave = np.sin(2 * np.pi * frequency * t)
    elif waveform == 'square':
        # square wave: sign of sine (values -1 or 1)
        wave = np.sign(np.sin(2 * np.pi * frequency * t))
    elif waveform == 'noise':
        # white noise: random samples between -1 and 1
        wave = np.random.uniform(-1, 1, size=length)
    else:
        wave = np.sin(2 * np.pi * frequency * t)  # default to sine
    # Apply a quick linear fade-in and fade-out (5ms) to avoid clicks
    fade_samples = int(0.005 * SAMPLE_RATE)
    if len(wave) > 2 * fade_samples:
        # fade-in
        wave[:fade_samples] *= np.linspace(0, 1, fade_samples)
        # fade-out
        wave[-fade_samples:] *= np.linspace(1, 0, fade_samples)
    # Convert to 16-bit signed integers
    audio_samples = (wave * 32767).astype(np.int16)
    return audio_samples

def generate_chirp(f_start, f_end, duration):
    """Generate a linear frequency sweep (chirp) from f_start to f_end over given duration."""
    length = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, length, endpoint=False)
    # Linear interpolation of frequency over time
    f_t = f_start + (f_end - f_start) * (t / duration)
    # Integrate frequency to get phase: phase(t) = 2π * ∫ f(t) dt
    phase = 2 * np.pi * (f_start * t + 0.5 * (f_end - f_start) * (t**2) / duration)
    wave = np.sin(phase)
    # Apply fade-out at end to avoid abrupt stop
    fade_samples = int(0.005 * SAMPLE_RATE)
    if len(wave) > fade_samples:
        wave[-fade_samples:] *= np.linspace(1, 0, fade_samples)
    audio_samples = (wave * 32767).astype(np.int16)
    return audio_samples

# Generate background music (procedural melody using square waves)
melody_notes = [261.63, 329.63, 392.00, 523.25, 392.00, 329.63, 293.66, 329.63]  # C4, E4, G4, C5, G4, E4, D4, E4 (Hz)
note_dur = 0.25  # each note 0.25 seconds
bg_wave = np.array([], dtype=np.int16)
for freq in melody_notes:
    tone = generate_wave(freq, note_dur, waveform='square')
    bg_wave = np.concatenate((bg_wave, tone))
# Ensure the loop is smooth by fading out end (already done in generate_wave for last note)
bg_sound = pygame.sndarray.make_sound(bg_wave)
bg_sound.set_volume(0.4)  # background music at lower volume

# Sound effects
move_wave   = generate_wave(440.0, 0.03, waveform='square')   # short A4 square wave
rotate_wave = generate_wave(660.0, 0.03, waveform='square')   # short E5 square wave
drop_wave   = generate_wave(300.0, 0.1,  waveform='sine')     # slightly longer drop sound
lock_wave   = generate_wave(150.0, 0.2,  waveform='sine')     # low-frequency thud for locking
# Line clear: combine multiple sine tones (C4, E4, G4 chord)
clear_duration = 0.3
t = np.linspace(0, clear_duration, int(SAMPLE_RATE * clear_duration), endpoint=False)
chord = (np.sin(2*np.pi*261.63*t) + np.sin(2*np.pi*329.63*t) + np.sin(2*np.pi*392.00*t)) / 3.0  # normalized sum
# Apply fade to chord as well
fade_samples = int(0.005 * SAMPLE_RATE)
if len(chord) > 2 * fade_samples:
    chord[:fade_samples] *= np.linspace(0, 1, fade_samples)
    chord[-fade_samples:] *= np.linspace(1, 0, fade_samples)
clear_wave = (chord * 32767).astype(np.int16)
# Game over chirp: from 800 Hz down to 200 Hz over 1 second
gameover_wave = generate_chirp(800.0, 200.0, 1.0)

# Create Sound objects from arrays
move_sound    = pygame.sndarray.make_sound(move_wave)
rotate_sound  = pygame.sndarray.make_sound(rotate_wave)
drop_sound    = pygame.sndarray.make_sound(drop_wave)
lock_sound    = pygame.sndarray.make_sound(lock_wave)
clear_sound   = pygame.sndarray.make_sound(clear_wave)
gameover_sound= pygame.sndarray.make_sound(gameover_wave)
# Set volumes for balance
move_sound.set_volume(0.5)
rotate_sound.set_volume(0.5)
drop_sound.set_volume(0.6)
lock_sound.set_volume(0.6)
clear_sound.set_volume(0.8)
gameover_sound.set_volume(0.8)

class Tetromino:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = random.choice(COLORS)
        self.rotation = 0

class Tetris:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Playfield grid initialized with 0 (empty)
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        self.current_piece = self.new_piece()
        self.game_over = False
        self.score = 0

    def new_piece(self):
        shape = random.choice(SHAPES)
        # Start new piece at horizontal center, top of the grid
        return Tetromino(self.width // 2, 0, shape)

    def valid_move(self, piece, dx, dy, dr):
        """Check if piece can move by (dx,dy) and rotate by dr without collision."""
        # Check all blocks of the piece in the new position/rotation
        new_rotation = (piece.rotation + dr) % len(piece.shape)
        for i, row in enumerate(piece.shape[new_rotation]):
            for j, cell in enumerate(row):
                if cell == 'O':
                    new_x = piece.x + j + dx
                    new_y = piece.y + i + dy
                    # Out of bounds or collision
                    if new_x < 0 or new_x >= self.width or new_y < 0 or new_y >= self.height:
                        return False
                    if self.grid[new_y][new_x] != 0:
                        return False
        return True

    def clear_lines(self):
        """Clear full lines from the grid and return the count of lines cleared."""
        lines_cleared = 0
        for i, row in enumerate(self.grid):
            if all(cell != 0 for cell in row):
                lines_cleared += 1
                # Remove the full line and insert an empty line at the top
                del self.grid[i]
                self.grid.insert(0, [0 for _ in range(self.width)])
        return lines_cleared

    def lock_piece(self, piece):
        """Lock the current piece into the grid and spawn a new piece."""
        for i, row in enumerate(piece.shape[piece.rotation % len(piece.shape)]):
            for j, cell in enumerate(row):
                if cell == 'O':
                    self.grid[piece.y + i][piece.x + j] = piece.color
        # Clear any completed lines
        lines = self.clear_lines()
        if lines > 0:
            self.score += lines * 100  # update score for cleared lines
        # Spawn a new piece
        self.current_piece = self.new_piece()
        # Check for game over (if new piece immediately collides)
        if not self.valid_move(self.current_piece, 0, 0, 0):
            self.game_over = True
        return lines

    def update(self):
        """Move the piece down by one step, or lock it if it can't move down further."""
        if not self.game_over:
            if self.valid_move(self.current_piece, 0, 1, 0):
                self.current_piece.y += 1
            else:
                self.lock_piece(self.current_piece)

    def draw(self, screen):
        """Draw the grid and current falling piece."""
        # Draw settled blocks
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, cell, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE-1, GRID_SIZE-1))
        # Draw current falling piece
        if self.current_piece:
            shape_matrix = self.current_piece.shape[self.current_piece.rotation % len(self.current_piece.shape)]
            for i, row in enumerate(shape_matrix):
                for j, cell in enumerate(row):
                    if cell == 'O':
                        pygame.draw.rect(screen, self.current_piece.color,
                                         ((self.current_piece.x + j) * GRID_SIZE, 
                                          (self.current_piece.y + i) * GRID_SIZE,
                                          GRID_SIZE-1, GRID_SIZE-1))

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    game = Tetris(WIDTH // GRID_SIZE, HEIGHT // GRID_SIZE)

    # Start background music loop
    bg_sound.play(loops=-1)

    game_over_sound_played = False
    fall_time = 0
    fall_speed = 50  # milliseconds per automatic fall step (lower = faster)

    while True:
        # Track state before update to detect locking events
        old_piece = game.current_piece
        old_score = game.score

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if game.valid_move(game.current_piece, -1, 0, 0):
                        game.current_piece.x -= 1
                        move_sound.play()
                if event.key == pygame.K_RIGHT:
                    if game.valid_move(game.current_piece, 1, 0, 0):
                        game.current_piece.x += 1
                        move_sound.play()
                if event.key == pygame.K_DOWN:
                    if game.valid_move(game.current_piece, 0, 1, 0):
                        game.current_piece.y += 1
                        drop_sound.play()
                if event.key == pygame.K_UP:
                    # rotate clockwise (dr = 1)
                    if game.valid_move(game.current_piece, 0, 0, 1):
                        game.current_piece.rotation = (game.current_piece.rotation + 1) % len(game.current_piece.shape)
                        rotate_sound.play()
                if event.key == pygame.K_SPACE:
                    # Hard drop: move piece down until it can't
                    drop_sound.play()
                    while game.valid_move(game.current_piece, 0, 1, 0):
                        game.current_piece.y += 1
                    # Lock the piece once it has reached the bottom
                    game.lock_piece(game.current_piece)
                    # (We will handle playing lock/clear sounds after the loop)

        # Game automatic falling based on timer
        delta_time = clock.get_rawtime()
        clock.tick()  # advance the clock
        fall_time += delta_time
        if fall_time >= fall_speed:
            game.update()
            fall_time = 0

        # Check if a piece was locked/spawned a new piece this frame
        if game.current_piece is not old_piece:
            # A new piece was created, meaning the old one locked in place
            # Determine if lines were cleared by comparing score change
            if game.score > old_score:
                # One or more lines cleared
                clear_sound.play()
            else:
                # No line cleared, just a normal lock
                lock_sound.play()

        # Draw everything
        screen.fill(BLACK)
        game.draw(screen)
        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {game.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if game.game_over:
            # If game over occurs, play the game over sound once
            if not game_over_sound_played:
                gameover_sound.play()
                game_over_sound_played = True
            # Display "Game Over" text
            font_game_over = pygame.font.Font(None, 48)
            go_text = font_game_over.render("Game Over", True, RED)
            screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//2 - 30))
            # Optionally, we could display "Press any key to restart" here
            # Check for key press to restart
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    game = Tetris(WIDTH // GRID_SIZE, HEIGHT // GRID_SIZE)
                    game_over_sound_played = False
                    # Note: background music continues; we could reset score and loop
                    break

        pygame.display.flip()
        clock.tick(60)  # limit to 60 FPS

if __name__ == "__main__":
    main()
# Compare this snippet from testv0.py:
