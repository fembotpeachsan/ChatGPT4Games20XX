import pygame
import sys
import random
import numpy as np

# 🔊 Init with proper audio config
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2)

# 🔊 Synth magic
SAMPLE_RATE = 44100
def play_sound(freq=440, duration=100, vol=0.5):
    """Generate bleep-bloop waveforms"""
    length = int(SAMPLE_RATE * duration / 1000)
    t = np.linspace(0, duration/1000, length, False)
    wave = np.sin(2 * np.pi * freq * t)
    audio = (wave * 32767).astype(np.int16)

    # Handle stereo/mono
    if pygame.mixer.get_init()[2] == 2:
        audio = np.stack([audio, audio], axis=-1)

    sound = pygame.sndarray.make_sound(audio)
    sound.set_volume(vol)
    sound.play()

# 🖼️ Display setup
W, H = 600, 400
screen = pygame.display.set_mode((W, H), pygame.NOFRAME)
pygame.display.set_caption("DK VIBES")
clock = pygame.time.Clock()

# 🎨 Neo-retro palette
COLORS = {
    "void": (12, 15, 20),
    "zest": (255, 100, 100),
    "cyan": (0, 255, 255),
    "plum": (101, 67, 133),
    "metal": (178, 190, 195),
    "gold": (255, 215, 0),
    "wood": (89, 60, 31),
    "ember": (255, 80, 0),
    "neon": (200, 255, 0),
    # More colors for variety
    "crimson": (220, 20, 60),
    "teal": (0, 128, 128),
    "indigo": (75, 0, 130),
    "olive": (128, 128, 0),
    "lavender": (230, 230, 250),
    "ruby": (139, 0, 0)
}

# 🕹️ Game states
MENU, PLAY, OVER, WIN, TRANSIT = range(5)

# 🏗️ Level blueprints (Keep base levels)
LEVELS = [
    {  # L1: Classic
        "floors": [
            (0, H-20, W, 20, "metal"),
            (100, H-100, 400, 10, "plum"),
            (0, H-180, 400, 10, "plum"),
            (200, H-260, 400, 10, "plum"),
            (0, H-340, 400, 10, "plum")
        ],
        "ladders": [
            (350, H-100, 80, 20),
            (150, H-180, 80, 20),
            (250, H-260, 80, 20),
            (350, H-340, 80, 20)
        ],
        "dk": (100, 50),
        "princess": (W-100, 50),
        "bg": "void",
        "bpm": 128
    },
    {  # L2: Cyberjungle
        "floors": [
            (0, H-20, W, 20, "metal"),
            (50, H-80, 200, 10, "metal"),
            (350, H-140, 200, 10, "metal"),
            (100, H-200, 300, 10, "metal"),
            (200, H-260, 200, 10, "metal")
        ],
        "ladders": [
            (280, H-80, 120, 15),
            (420, H-140, 120, 15),
            (180, H-200, 120, 15),
            (300, H-260, 120, 15)
        ],
        "dk": (400, 50),
        "princess": (50, 50),
        "bg": (40, 55, 71), # A custom color
        "bpm": 140
    }
]

# --- 😼 CatGPT's Level Generation Module Fixes 😼 ---
def generate_random_level(level_index):
    """Generates a random level layout."""
    floors_data = [(0, H - 20, W, 20, "metal")] # Base floor always exists
    ladders_data = []

    num_layers = random.randint(4, 6)
    layer_height = max(50, (H - 60) // num_layers) # Ensure minimum layer height

    # Generate platforms layer by layer from bottom up (excluding the base floor index 0)
    prev_layer_floors_data = [floors_data[0]] # Start with the base floor data

    for i in range(num_layers):
        # Calculate target Y for this layer
        layer_y = H - 20 - (i + 1) * layer_height
        # Adjust layer_y slightly to avoid perfect alignment and potential overlap issues
        layer_y += random.randint(-10, 10)
        layer_y = max(50, min(H - 100, layer_y)) # Keep layers within reasonable vertical bounds

        num_platforms_in_layer = random.randint(1, 3)

        current_layer_floors_data = []

        for _ in range(num_platforms_in_layer):
            platform_w = random.randint(100, 300)
            platform_x = random.randint(0, W - platform_w)
            platform_h = random.randint(8, 15)
            # Use colors other than base "metal" and "void" for generated platforms
            platform_color = random.choice([c for c in COLORS.keys() if c not in ["metal", "void"]])

            floors_data.append((platform_x, layer_y, platform_w, platform_h, platform_color))
            current_layer_floors_data.append(floors_data[-1]) # Add the data tuple

        # Add ladders connecting this layer to the one below
        if prev_layer_floors_data and current_layer_floors_data:
            # Try to add a few ladders
            num_ladders_to_attempt = random.randint(1, min(len(prev_layer_floors_data) * 2, len(current_layer_floors_data) * 2, 4))
            
            for _ in range(num_ladders_to_attempt):
                 # Pick a platform on the lower layer and one on the current layer randomly
                 lower_p_tuple = random.choice(prev_layer_floors_data)
                 upper_p_tuple = random.choice(current_layer_floors_data)

                 lower_p_rect = pygame.Rect(lower_p_tuple[0], lower_p_tuple[1], lower_p_tuple[2], lower_p_tuple[3])
                 upper_p_rect = pygame.Rect(upper_p_tuple[0], upper_p_tuple[1], upper_p_tuple[2], upper_p_tuple[3])

                 # Ladder should connect the top of the lower platform to the bottom of the upper platform
                 ladder_y = upper_p_rect.bottom
                 ladder_h = lower_p_rect.top - upper_p_rect.bottom

                 # Determine ladder width first
                 ladder_w = random.randint(15, 25)

                 # Calculate the valid horizontal range for the ladder's left edge
                 # The ladder's left edge (x) must be between:
                 # max(left edge of lower platform, left edge of upper platform)
                 # and
                 # min(right edge of lower platform - ladder_w, right edge of upper platform - ladder_w)
                 ladder_x_start_range = max(lower_p_rect.left, upper_p_rect.left)
                 ladder_x_end_range = min(lower_p_rect.right - ladder_w, upper_p_rect.right - ladder_w)

                 # --- FIX: Check if the range is valid ---
                 if ladder_x_start_range < ladder_x_end_range and ladder_h > 30: # Ensure valid horizontal space and sufficient vertical space
                      ladder_x = random.randint(ladder_x_start_range, ladder_x_end_range)
                      ladders_data.append((ladder_x, ladder_y, ladder_h, ladder_w))
                 # --- End Fix ---


        prev_layer_floors_data = current_layer_floors_data # Move to the next layer

    # Place DK and Princess - try to place them on a platform in the upper half
    upper_half_platforms = [p for p in floors_data if p[1] < H // 2]

    if not upper_half_platforms: # Fallback if no platforms in upper half
        dk_pos = (random.randint(50, W-110), 50)
        princess_pos = (random.randint(50, W-110), 50)
    else:
        # Pick random platforms from the upper half
        dk_p_tuple = random.choice(upper_half_platforms)
        princess_p_tuple = random.choice(upper_half_platforms)

        # Place them on top of the chosen platforms
        dk_pos = (dk_p_tuple[0] + random.randint(10, max(10, dk_p_tuple[2] - 70)), dk_p_tuple[1] - 70)
        princess_pos = (princess_p_tuple[0] + random.randint(10, max(10, princess_p_tuple[2] - 30)), princess_p_tuple[1] - 40)

    # Ensure DK and Princess are within screen bounds (especially top)
    dk_pos = (max(0, min(W-60, dk_pos[0])), max(20, min(H//2 - 60, dk_pos[1]))) # Don't place too high
    princess_pos = (max(0, min(W-20, princess_pos[0])), max(20, min(H//2 - 30, princess_pos[1]))) # Don't place too high


    # Choose a random background color (can be a named color or tuple)
    bg_key_or_tuple = random.choice(list(COLORS.keys()) + [(random.randint(0,50), random.randint(0,50), random.randint(50,100))]) # Include custom dark blues
    bg_color = COLORS.get(bg_key_or_tuple, bg_key_or_tuple) # Resolve named color or use tuple directly

    # Vary BPM based on level index
    base_bpm = 120
    max_bpm = 200 # Cap the BPM
    bpm = min(max_bpm, base_bpm + (level_index % 50) * 2) # Increase BPM gradually, cycle after 50 levels

    return {
        "floors": floors_data,
        "ladders": ladders_data,
        "dk": dk_pos,
        "princess": princess_pos,
        "bg": bg_color,
        "bpm": bpm
    }

# Generate 99 additional random levels and append them
# Start generating from index 2, since 0 and 1 are predefined
num_additional_levels = 99
for i in range(num_additional_levels):
    # Pass the absolute level index (2 to 100) to generate_random_level
    LEVELS.append(generate_random_level(len(LEVELS)))


# --- End of CatGPT's Level Generation Module Fixes ---


class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.level = 0
        self.lives = 3
        self.score = 0 # Added score!
        self.rhythm = 0 # Not used currently, but potential beat-sync feature?
        self.last_barrel = 0

class Platform:
    def __init__(self, x, y, w, h, col):
        self.rect = pygame.Rect(x, y, w, h)
        self.col = COLORS.get(col, col) # Handle both named and tuple colors

    def draw(self):
        pygame.draw.rect(screen, self.col, self.rect)
        # Add some detail for "metal" platforms
        if self.col == COLORS["metal"]:
             for px in range(self.rect.left+5, self.rect.right-5, 15):
                 pygame.draw.circle(screen, COLORS["cyan"], (px, self.rect.centery), 2)
        # Add detail for other colors too!
        elif self.col != COLORS["void"]: # Don't draw dots on void platforms (if any)
             detail_color = COLORS["void"] if self.col in [COLORS["cyan"], COLORS["neon"]] else COLORS["neon"] # Contrast color
             for px in range(self.rect.left+random.randint(3,7), self.rect.right-random.randint(3,7), 20):
                  pygame.draw.rect(screen, detail_color, (px, self.rect.top+random.randint(2, self.rect.height-5), 4, 4))


class Ladder:
    def __init__(self, x, y, h, w):
        self.rect = pygame.Rect(x, y, w, h)
        # Ensure step height is reasonable, avoid division by zero if h is small
        self.step_height = max(1, h // 8)
        self.color = COLORS["wood"] # Ladders are always wood

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        # Draw steps
        for i in range(8):
            step_y = self.rect.top + i * self.step_height
            pygame.draw.rect(screen, COLORS["void"], (self.rect.left, step_y, self.rect.width, 3)) # Use void for steps

class Player:
    def __init__(self):
        self.reset()

    def reset(self):
        # Start near the bottom left
        self.rect = pygame.Rect(50, H-50, 20, 30)
        self.vel = 0
        self.jumping = False
        self.on_ladder = False
        self.frame = 0 # For simple animation
        self.invincible = False # Maybe add invincibility after being hit?
        self.invincibility_timer = 0


    def draw(self):
        # Simple animation/color change
        col = COLORS["zest"] if self.frame % 10 < 5 else COLORS["ember"]
        if self.invincible and self.invincibility_timer % 4 < 2: # Flash when invincible
             col = (100, 100, 100) # Grey out

        pygame.draw.rect(screen, col, self.rect)
        pygame.draw.rect(screen, COLORS["cyan"], (self.rect.x, self.rect.y, 20, 5)) # Headband? Visor?
        self.frame += 1

    def update(self):
        if self.invincible:
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.invincible = False

class Kong:
    def __init__(self, x, y):
        # DK is a bit bigger
        self.rect = pygame.Rect(x, y, 60, 60)
        self.arm_frame = 0 # For arm animation

    def draw(self):
        pygame.draw.ellipse(screen, COLORS["plum"], self.rect) # Body
        # Simple arm animation
        arm_y_offset = 40 if self.arm_frame < 15 else 30
        pygame.draw.rect(screen, COLORS["plum"], (self.rect.left-10, self.rect.y + arm_y_offset, 20, 15)) # Left arm
        pygame.draw.rect(screen, COLORS["plum"], (self.rect.right-10, self.rect.y + arm_y_offset, 20, 15)) # Right arm
        self.arm_frame = (self.arm_frame + 1) % 30


class Princess:
    def __init__(self, x, y):
        # Princess is small
        self.rect = pygame.Rect(x, y, 20, 30)

    def draw(self):
        pygame.draw.ellipse(screen, COLORS["gold"], self.rect) # Body
        pygame.draw.circle(screen, COLORS["neon"], (self.rect.centerx, self.rect.y+10), 3) # "Hair" or accessory

class Barrel:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 18, 18) # Barrel size
        self.speed = 3
        self.dir = random.choice([-1, 1]) # Random horizontal direction
        self.falling = False
        self.vel = 0 # Vertical velocity for falling

    def draw(self):
        pygame.draw.ellipse(screen, COLORS["wood"], self.rect) # Barrel body
        # Add some detail to the barrel
        pygame.draw.line(screen, COLORS["neon"],
                         (self.rect.left+4, self.rect.centery),
                         (self.rect.right-4, self.rect.centery), 3)
        pygame.draw.line(screen, COLORS["neon"],
                         (self.rect.centerx, self.rect.top+4),
                         (self.rect.centerx, self.rect.bottom-4), 3)


def load_level(n):
    """Loads level data by index."""
    if n >= len(LEVELS):
        # If trying to load a level beyond the last one, go to the win state logic instead of crashing or looping.
        # The main loop will handle the WIN state display.
        return None # Indicate no more levels

    data = LEVELS[n]
    # Convert background color string to tuple if necessary
    bg_color = COLORS.get(data["bg"], data["bg"])
    return (
        [Platform(*f) for f in data["floors"]],
        [Ladder(*l) for l in data["ladders"]],
        Kong(*data["dk"]),
        Princess(*data["princess"]),
        bg_color,
        data["bpm"]
    )

def main():
    state = GameState()
    # Load the first level initially
    level_data = load_level(state.level)
    platforms, ladders, dk, princess, bg_color, bpm = level_data if level_data else ([], [], None, None, COLORS["void"], 120) # Handle case if no levels exist (shouldn't happen)
    player = Player()
    barrels = []
    game_state = MENU
    font = pygame.font.Font(None, 36) # Standard font

    last_barrel_spawn_time = pygame.time.get_ticks() # Timer for barrels

    while True:
        # 🎹 Event groove
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if game_state == MENU and e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                play_sound(880, 200, 0.4) # Menu start sound
                game_state = PLAY
            # Check for restart after Game Over or Win
            if (game_state == OVER or game_state == WIN) and e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                 state.reset() # Reset game state
                 # Reload the first level
                 level_data = load_level(state.level)
                 platforms, ladders, dk, princess, bg_color, bpm = level_data if level_data else ([], [], None, None, COLORS["void"], 120) # Handle case if no levels exist
                 player.reset() # Reset player position
                 barrels.clear() # Clear barrels
                 last_barrel_spawn_time = pygame.time.get_ticks() # Reset barrel timer
                 game_state = PLAY # Back to play

            # Player input events only matter in PLAY state
            if game_state == PLAY:
                 if e.type == pygame.KEYDOWN:
                      if e.key == pygame.K_UP and not player.jumping and not player.on_ladder:
                           player.vel = -14 # Apply upward velocity for jump
                           player.jumping = True
                           play_sound(660, 150, 0.5) # Jump sound


        # 🎨 Render canvas
        screen.fill(bg_color) # Fill with background color


        if game_state == MENU:
            title = font.render("DONKEY KONG: NEO RETRO", True, COLORS["neon"])
            prompt = font.render("PRESS ENTER TO RUMBLE", True, COLORS["cyan"])
            screen.blit(title, (W//2 - title.get_width()//2, H//2 - 50))
            screen.blit(prompt, (W//2 - prompt.get_width()//2, H//2 + 50))

        elif game_state == PLAY:
            keys = pygame.key.get_pressed()

            # Update player (for invincibility timer)
            player.update()

            # 🕺 Player moves (using key state for continuous movement)
            move_x = 0
            if keys[pygame.K_LEFT]:
                move_x -= 4
            if keys[pygame.K_RIGHT]:
                move_x += 4
            player.rect.x += move_x
            # Keep player within horizontal bounds
            player.rect.x = max(0, min(W-player.rect.width, player.rect.x))

            # 🪜 Ladder climbing (using key state)
            colliding_ladders = [l for l in ladders if player.rect.colliderect(l.rect)]
            can_climb = len(colliding_ladders) > 0

            # Smooth transition onto ladder
            if can_climb and not player.on_ladder:
                 if keys[pygame.K_UP] or keys[pygame.K_DOWN]:
                      player.on_ladder = True
                      # Snap to ladder center when starting to climb
                      closest_ladder = colliding_ladders[0] # Use the first colliding ladder
                      player.rect.centerx = closest_ladder.rect.centerx


            if player.on_ladder:
                # Check if still on a ladder or close enough to one vertically
                still_on_ladder = False
                for l in ladders:
                     # Check if player is vertically aligned with ladder and within its vertical range + some buffer
                    if abs(player.rect.centerx - l.rect.centerx) < l.rect.width / 2 + player.rect.width / 2 and player.rect.bottom > l.rect.top and player.rect.top < l.rect.bottom:
                         still_on_ladder = True
                         break
                
                if still_on_ladder:
                     player.rect.y += (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * 3 # Climb speed
                     player.vel = 0 # No gravity when on ladder
                     player.jumping = False # Cannot jump when on ladder
                     # Keep player's horizontal position aligned with the closest ladder's center while on it
                     if colliding_ladders: # Only align if actually colliding now
                          closest_ladder = colliding_ladders[0]
                          player.rect.centerx = closest_ladder.rect.centerx

                else:
                    # Fell or climbed off the ladder
                    player.on_ladder = False
                    player.vel = 0 # Start applying gravity immediately

            else:
                # Apply gravity when not on ladder
                player.vel += 0.8
                player.rect.y += player.vel


            # 🪨 Platform collision
            on_ground = False
            for p in platforms:
                # Check for landing on a platform
                if player.rect.colliderect(p.rect) and player.vel >= 0:
                    # Check if falling and landing on top of platform
                    # We need to check the player's position *after* vertical movement
                    # But collision detection works best checking from just above
                    # A simple check: if player's bottom is now below platform's top, but was above it before this frame
                    # This requires storing previous position, or checking more carefully.
                    # Let's stick to the simpler check for now, adjusting threshold.
                    if player.rect.bottom >= p.rect.top and player.rect.top < p.rect.bottom - 5: # Check from above
                        player.rect.bottom = p.rect.top # Snap to top of platform
                        player.vel = 0 # Stop vertical movement
                        player.jumping = False
                        on_ground = True
                # Prevent horizontal movement through platforms if player is trying to move into one from the side
                elif player.rect.colliderect(p.rect):
                     # If player rect is overlapping and not clearly above/below
                     if not (player.rect.bottom <= p.rect.top + 5 or player.rect.top >= p.rect.bottom - 5):
                          if move_x > 0: # Moving right into platform
                               player.rect.right = p.rect.left
                          elif move_x < 0: # Moving left into platform
                               player.rect.left = p.rect.right


            # Prevent falling off the bottom of the screen (death zone)
            if player.rect.top > H:
                 if not player.invincible: # Only lose life if not invincible
                    play_sound(220, 300, 0.7) # Player hit sound
                    state.lives -= 1
                    if state.lives <= 0:
                        play_sound(110, 800, 0.8) # Game over sound
                        game_state = OVER
                    else:
                        player.reset() # Reset player position
                        player.invincible = True # Grant temporary invincibility
                        player.invincibility_timer = 60 # 1 second (assuming 60 FPS)
                        barrels.clear() # Clear barrels on death
                        last_barrel_spawn_time = pygame.time.get_ticks() # Reset barrel timer


            # 🛢️ Barrel spawn
            now = pygame.time.get_ticks()
            # Barrel spawn rate increases with level, caps out
            barrel_spawn_interval = max(800, 2500 - state.level * 20)
            if now - last_barrel_spawn_time > barrel_spawn_interval:
                barrels.append(Barrel(dk.rect.centerx, dk.rect.centery))
                last_barrel_spawn_time = now
                play_sound(330 + state.level * 5, 200, 0.4) # Barrel spawn sound frequency increases with level

            # 🌀 Barrel physics and collision
            barrels_to_remove = []
            for b in barrels:
                if b.falling:
                    b.vel += 0.8 # Apply gravity to falling barrels
                    b.rect.y += b.vel
                    landed_on_platform = False
                    for p in platforms:
                        # Check if falling barrel collides with top of platform
                        if b.rect.colliderect(p.rect) and b.vel > 0 and b.rect.bottom >= p.rect.top and b.rect.top < p.rect.bottom:
                             b.rect.bottom = p.rect.top # Land on platform
                             b.vel = 0
                             b.falling = False
                             # Choose new horizontal direction, maybe bias away from player? 😉
                             b.dir = -1 if player.rect.centerx < b.rect.centerx else 1
                             if random.random() < 0.2: # Small chance to reverse direction randomly
                                  b.dir *= -1

                             landed_on_platform = True
                             break
                    # If barrel didn't land on a platform, check for ladder collision (barrel breaks on ladder)
                    if not landed_on_platform:
                         hit_ladder = False
                         for l in ladders:
                              if b.rect.colliderect(l.rect):
                                   hit_ladder = True
                                   break
                         if hit_ladder:
                              play_sound(180, 100, 0.3) # Barrel breaks sound
                              barrels_to_remove.append(b)
                              continue # Go to next barrel

                else: # Barrel is rolling horizontally
                    b.rect.x += b.speed * b.dir
                    # Check if the barrel is about to roll off a platform edge
                    is_supported = False
                    # Check a point slightly ahead and below the barrel's current position
                    check_point_x = b.rect.centerx + b.dir * b.rect.width / 2
                    check_point_y = b.rect.bottom + 5 # Look a little below
                    check_point_rect = pygame.Rect(check_point_x, check_point_y, 1, 1) # A point rectangle

                    for p in platforms:
                        if check_point_rect.colliderect(p.rect):
                            is_supported = True
                            break

                    # If not supported, start falling
                    if not is_supported:
                         b.falling = True
                         b.vel = 0 # Start fall with no initial vertical velocity

                # Remove barrels that fall off the bottom of the screen
                if b.rect.top > H:
                    barrels_to_remove.append(b)

                # 💥 Collision check between player and barrel
                if player.rect.colliderect(b.rect) and not player.invincible:
                    play_sound(220, 300, 0.7) # Player hit sound
                    state.lives -= 1
                    if state.lives <= 0:
                        play_sound(110, 800, 0.8) # Game over sound
                        game_state = OVER
                    else:
                        player.reset() # Reset player position
                        player.invincible = True # Grant temporary invincibility
                        player.invincibility_timer = 60 # 1 second (assuming 60 FPS)
                        barrels.clear() # Clear all barrels on hit
                        last_barrel_spawn_time = pygame.time.get_ticks() # Reset barrel timer
                    barrels_to_remove.append(b) # Remove the barrel that hit the player
                    break # Only one collision per frame matters

            # Remove barrels marked for removal
            for b in barrels_to_remove:
                 if b in barrels: # Check if it's still in the list (might have been removed by player hit)
                     barrels.remove(b)


            # 🏆 Level complete check - FIX APPLIED HERE
            level_completed = False
            if princess is not None and player.rect.colliderect(princess.rect):
                 level_completed = True

            if level_completed: # Check if player reached princess
                play_sound(1000, 200, 0.6) # Level win sound
                state.score += 100 # Add score for completing a level
                state.level += 1
                
                level_data = load_level(state.level) # Attempt to load the next level

                if level_data is None: # If load_level returns None, it means we finished all levels
                    play_sound(1200, 800, 0.9) # Final win sound
                    game_state = WIN
                else:
                    # Load next level data
                    platforms, ladders, dk, princess, bg_color, bpm = level_data
                    player.reset() # Reset player for next level
                    barrels.clear() # Clear barrels for next level
                    last_barrel_spawn_time = pygame.time.get_ticks() # Reset barrel timer
                    game_state = TRANSIT # Go to transit screen

        elif game_state == TRANSIT:
            text = font.render(f"LEVEL {state.level + 1} ENGAGE", True, COLORS["neon"])
            screen.blit(text, (W//2 - text.get_width()//2, H//2))
            score_text = font.render(f"SCORE: {state.score}", True, COLORS["gold"])
            screen.blit(score_text, (W//2 - score_text.get_width()//2, H//2 + 50))
            pygame.display.flip()
            pygame.time.delay(1500) # Show transit screen for a bit
            game_state = PLAY # Back to play
            # Load level details and set BPM after transit is over
            # Note: level_data, platforms, etc. are already updated in the PLAY state block
            # after the level completion check, so we just switch state here.
            pass # No need to reload data, it was done just before entering TRANSIT


        elif game_state == WIN:
            text = font.render("ULTIMATE VICTORY", True, COLORS["gold"])
            score_text = font.render(f"FINAL SCORE: {state.score}", True, COLORS["gold"])
            restart_prompt = font.render("PRESS ENTER TO PLAY AGAIN", True, COLORS["cyan"])
            screen.blit(text, (W//2 - text.get_width()//2, H//2 - 30))
            screen.blit(score_text, (W//2 - score_text.get_width()//2, H//2 + 20))
            screen.blit(restart_prompt, (W//2 - restart_prompt.get_width()//2, H//2 + 80)) # Add restart prompt

        elif game_state == OVER:
            text = font.render("GAME OVER", True, COLORS["zest"])
            score_text = font.render(f"FINAL SCORE: {state.score}", True, COLORS["gold"])
            restart_prompt = font.render("PRESS ENTER TO RETRY", True, COLORS["cyan"])
            screen.blit(text, (W//2 - text.get_width()//2, H//2 - 30))
            screen.blit(score_text, (W//2 - score_text.get_width()//2, H//2 + 20))
            screen.blit(restart_prompt, (W//2 - restart_prompt.get_width()//2, H//2 + 80)) # Add restart prompt

        # 🖌️ Draw world elements only in PLAY state
        if game_state == PLAY:
            for p in platforms: p.draw()
            for l in ladders: l.draw()
            for b in barrels: b.draw()
            if dk: dk.draw() # Draw DK only if the object exists (should be always in PLAY)
            if princess: princess.draw() # Draw Princess only if the object exists
            player.draw() # Player is drawn last so they are on top

            # 📊 HUD (Lives, Level, Score)
            lives_text = font.render(f"LIVES: {state.lives}", True, COLORS["cyan"])
            level_text = font.render(f"LV: {state.level + 1}/{len(LEVELS)}", True, COLORS["neon"])
            score_text = font.render(f"SCORE: {state.score}", True, COLORS["gold"])
            screen.blit(lives_text, (10, 10))
            screen.blit(level_text, (W // 2 - level_text.get_width() // 2, 10)) # Center level text
            screen.blit(score_text, (W - score_text.get_width() - 10, 10))


        pygame.display.flip() # Update the full screen
        if game_state == PLAY:
             clock.tick(bpm)  # Sync frame rate to level BPM only in PLAY
        else:
             clock.tick(60) # Standard rate for other states


if __name__ == "__main__":
    main()
