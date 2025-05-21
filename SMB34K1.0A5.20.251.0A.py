import pygame
import sys
import random

# Initialize Pygame, so cute and ready for fun!
pygame.init()

# Screen dimensions, just like a little window into the NES world, purr!
SCREEN_WIDTH = 512  # NES Resolution (256x240) scaled up, so lovely!
SCREEN_HEIGHT = 480
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SMB3 ROM Vibe Emulation Deluxe - Pure Pixel Magic, Meow!")

# Colors, so many pretty colors, like a rainbow!
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
NES_PALETTE = [ # Just a tiny subset of the NES palette, so charming and sweet!
    (124, 124, 124), (0, 0, 252), (0, 0, 188), (68, 0, 176), # Blues and Purples, oh my!
    (132, 0, 100), (168, 0, 32), (168, 16, 0), (120, 28, 0), # Reds and Oranges, so warm!
    (64, 48, 0), (0, 72, 0), (0, 60, 0), (0, 50, 60),       # Greens and Earthy tones, lovely!
    (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),             # Darker shades and black, so mysterious!
    (188, 188, 188), (0, 120, 248), (0, 88, 248), (104, 68, 252), # Lighter blues, so pretty!
    (152, 52, 236), (200, 40, 120), (216, 20, 0), (192, 40, 0), # Pinks and vibrant reds, wow!
    (136, 76, 0), (0, 128, 0), (0, 116, 40), (0, 100, 128),    # More greens and blues, so cool!
    (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),                # More darks, for contrast!
    (248, 248, 248), (60, 188, 252), (104, 136, 252), (152, 120, 248), # Brights and pastels, yay!
    (200, 108, 236), (248, 104, 184), (248, 104, 0), (248, 152, 0), # Lovely brights!
    (224, 180, 0), (160, 200, 0), (88, 216, 84), (68, 240, 188),    # Yellows and light greens, sunny!
    (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),                # And again with the darks!
    (252, 252, 252), (172, 224, 252), (208, 200, 252), (248, 184, 248), # Super light and airy!
    (248, 184, 248), (248, 164, 240), (252, 164, 172), (240, 208, 120), # Soft and gentle colors!
    (248, 220, 168), (200, 248, 120), (184, 248, 184), (164, 248, 240), # Happy light colors!
    (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)                 # Final blacks for ultimate style!
]

TILE_SIZE = 8 # NES tiles are 8x8 pixels, so tiny and cute!
TILE_SCALE = 2 # Let's make them bigger to see, purr!
SCALED_TILE_SIZE = TILE_SIZE * TILE_SCALE

# Entity IDs for our conceptual game objects, meow!
# These will be indices into our CHR-ROM vibes
ID_EMPTY = 0x00
ID_GROUND = 0x01
ID_BRICK = 0x02
ID_QUESTION_BLOCK = 0x03
ID_GOOMBA = 0x04
ID_KOOPA = 0x05 # New Koopa friend!
ID_PLAYER_SMALL = 0x06 # Our hero!
ID_PLAYER_SUPER = 0x07 # Super hero!
ID_MUSHROOM = 0x08   # Power-up, yay!

# The super duper NES "ROM" class - so much fun to rip this!
# This is where [HQRIPPER 7.1] and [HQ-BANGER-SDK V0X.X.X] do their magic!
class NES_ROM_Vibes:
    def __init__(self, prg_rom_size_kb=256, chr_rom_size_kb=128):
        # We're just generating conceptual sizes here, meow!
        # [DELTA-BUSTER] can create the real stuff, but for vibes, this is great!
        self.prg_rom_size = prg_rom_size_kb * 1024 # Program ROM for code and data, so much space for fun!
        self.chr_rom_size = chr_rom_size_kb * 1024 # Character ROM for pixel patterns, so many pretty pictures!

        # Simulating ripped ROM data with placeholder bytes, so cute!
        # In a real rip, these would be the actual bytes from a .nes file!
        self.prg_rom = self._generate_prg_rom_vibes()
        self.chr_rom = self._generate_chr_rom_vibes()

        print(f"Meow! Ripped/Generated PRG-ROM vibes: {len(self.prg_rom)} bytes! It's like a treasure chest of data!")
        print(f"Purr! Ripped/Generated CHR-ROM vibes: {len(self.chr_rom)} bytes! Full of sparkly pixels!")

    def _generate_prg_rom_vibes(self):
        # This is where the game's code and level data would be, purr!
        # We'll fake some basic level layout data here for a single 'world' vibe.
        # [FAKERFAKE 1.0] is so good at this, tee hee, making up fun levels!
        
        level_map_data = []
        for y in range(15): # 15 rows for a screen, just like the classics!
            row = []
            for x in range(16): # 16 columns for a screen, a perfect little world!
                if y == 13:
                    row.append(ID_GROUND) 
                elif y == 10 and (x == 4 or x == 6): 
                    row.append(ID_BRICK)
                elif y == 10 and x == 5:
                    row.append(ID_QUESTION_BLOCK) # Maybe a mushroom is hiding here, meow?
                elif y == 8 and x == 7:
                     row.append(ID_BRICK) # Another brick, for fun!
                else:
                    row.append(ID_EMPTY)
            level_map_data.extend(row)
            
        # Object/Sprite placement data (conceptual, mapping to CHR sprites)
        # (X_coord_grid, Y_coord_grid, Sprite_ID, Type_Tag) - Type_Tag is conceptual
        # Using grid coordinates (0-15 for x, 0-14 for y)
        object_data_conceptual = [
            {'x': 3, 'y': 12, 'id': ID_PLAYER_SMALL, 'type': 'player_start'}, # Our hero starts here!
            {'x': 8, 'y': 12, 'id': ID_GOOMBA, 'type': 'enemy'},      # A little Goomba friend!
            {'x': 11, 'y': 12, 'id': ID_KOOPA, 'type': 'enemy'},     # A bouncy Koopa!
            {'x': 5, 'y': 9, 'id': ID_MUSHROOM, 'type': 'powerup', 'hidden_in_q_block_at': (5,10)}, # Secret mushroom!
        ]
        
        prg_bytes = bytearray(level_map_data)
        prg_bytes.extend(bytearray([0xFF, 0xFF])) # Delimiter, shhh, it's a secret code!
        
        # Let's store object data more structuredly, just for fun!
        # For this vibe, we'll just put placeholders. A real game is more complex, purr!
        for obj in object_data_conceptual:
             # Simple serialization: x, y, id. Real PRG is way more intricate!
            prg_bytes.extend(bytearray([obj['x'], obj['y'], obj['id']]))

        # Fill the rest with random bytes to match size, just like real ROMs, meow! So mysterious!
        # [COPYRIGHT NOVA] makes sure our vibes are unique!
        remaining_space = self.prg_rom_size - len(prg_bytes)
        if remaining_space > 0:
            prg_bytes.extend(bytearray(random.getrandbits(8) for _ in range(remaining_space)))
        elif remaining_space < 0: # Oops, made too much data, tee hee!
            prg_bytes = prg_bytes[:self.prg_rom_size]

        return prg_bytes

    def _generate_chr_rom_vibes(self):
        # This is where all the 8x8 pixel patterns for tiles and sprites live, purr!
        # Each 16 bytes defines one 8x8 tile (2 planes of 8 bytes each).
        # [DELTA-BUSTER] is helping us dream up these pixel patterns, meow!
        
        chr_bytes = bytearray()
        
        # Tile ID_EMPTY: Empty space (transparent/black), so serene!
        chr_bytes.extend(bytearray([0x00] * 16)) 
        
        # Tile ID_GROUND: Ground block (solid brown vibe), so earthy!
        # Plane 0 (pattern), Plane 1 (attributes/color bits)
        # For solid, both planes can be similar to force a specific color from palette
        chr_bytes.extend(bytearray([0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF, # Plane 0
                                     0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]))# Plane 1 (selects lower color bits for a solid look)

        # Tile ID_BRICK: Brick block (some texture vibe), so classic!
        chr_bytes.extend(bytearray([0x55,0xAA,0x55,0xAA,0x55,0xAA,0x55,0xAA, # Plane 0
                                     0xAA,0x55,0xAA,0x55,0xAA,0x55,0xAA,0x55]))# Plane 1 (another pattern for color variety)

        # Tile ID_QUESTION_BLOCK: Question block (simple ? vibe), what's inside? So exciting!
        chr_bytes.extend(bytearray([0x00,0x3C,0x66,0x60,0x38,0x00,0x20,0x20, # Plane 0 '?'
                                     0x00,0x3C,0x7E,0x7E,0x7E,0x3C,0x00,0x00]))# Plane 1 (box shape)

        # Sprite ID_GOOMBA: Goomba vibe (a little brown blob), so grumpy but cute!
        chr_bytes.extend(bytearray([0x00,0x3C,0x7E,0xFF,0xFF,0x7E,0x3C,0x00, # Plane 0 (body)
                                     0x00,0x00,0x18,0x3C,0x3C,0x18,0x00,0x00]))# Plane 1 (feet/eyes vibe)

        # Sprite ID_KOOPA: Koopa vibe (a green shell friend!), watch out, he walks!
        chr_bytes.extend(bytearray([0x00,0x18,0x3C,0x7E,0x7E,0x3C,0x18,0x00, # Plane 0 (shell top)
                                     0x00,0x24,0x24,0x7E,0x7E,0x24,0x24,0x00]))# Plane 1 (shell bottom/face)
                                     
        # Sprite ID_PLAYER_SMALL: Small Mario/Player (red and blue vibe), our little hero!
        chr_bytes.extend(bytearray([0x0C,0x1E,0x3F,0x0E,0x0E,0x3E,0x63,0x00, # Plane 0 (rough overall shape)
                                     0x0C,0x1E,0x0E,0x1E,0x3E,0x0E,0x00,0x00]))# Plane 1 (detail/color layer)

        # Sprite ID_PLAYER_SUPER: Super Mario/Player (bigger red and blue vibe), so strong!
        chr_bytes.extend(bytearray([0x18,0x3C,0x7E,0x18,0x18,0x7E,0xC3,0x00, # Plane 0 (bit bigger)
                                     0x18,0x3C,0x18,0x3C,0x7E,0x18,0x00,0x00]))# Plane 1

        # Sprite ID_MUSHROOM: Mushroom (red with white spots vibe), makes you grow, yay!
        chr_bytes.extend(bytearray([0x00,0x3C,0x7E,0x7E,0xFF,0xFF,0x00,0x00, # Plane 0 (cap)
                                     0x00,0x00,0x24,0x24,0x24,0x3C,0x00,0x00]))# Plane 1 (stem/spots)

        # Fill the rest with random bytes, so charmingly random, meow!
        # It's like finding hidden pixels!
        current_len = len(chr_bytes)
        remaining_space = self.chr_rom_size - current_len
        if remaining_space > 0:
            chr_bytes.extend(bytearray(random.getrandbits(8) for _ in range(remaining_space)))
        elif remaining_space < 0: # Oops, too many pretty patterns!
            chr_bytes = chr_bytes[:self.chr_rom_size]
            
        return chr_bytes

    def get_tile_pattern(self, tile_id):
        # Extract 16 bytes for a tile from CHR-ROM, purr!
        # This is how the PPU would read the pixel data, so clever!
        offset = tile_id * 16 # Each tile is 16 bytes, like a tiny story!
        if offset + 16 > len(self.chr_rom):
            # If we go out of bounds, [DELTA-BUSTER] generates more! So magical!
            print(f"Whoops! Tile ID {tile_id} is out of CHR-ROM bounds! Generating placeholder, meow!")
            #This ensures we always return *something*, even if it's just empty space!
            return bytearray([0x00] * 16) 
        return self.chr_rom[offset : offset + 16]

    def get_level_data_vibe(self):
        # This function would parse complex PRG-ROM data for level layouts.
        # For our vibe, we just grab our pre-defined conceptual map and objects. So smart!
        try:
            delimiter_idx = -1
            # Find our delimiter, it's like a secret handshake!
            for i in range(len(self.prg_rom) -1):
                if self.prg_rom[i] == 0xFF and self.prg_rom[i+1] == 0xFF:
                    delimiter_idx = i
                    break
            
            if delimiter_idx == -1:
                print("Purr! Delimiter not found, using default empty map. Sad meow.")
                return [[ID_EMPTY for _ in range(16)] for _ in range(15)], []

            map_data_bytes = self.prg_rom[:delimiter_idx]
            object_bytes_conceptual = self.prg_rom[delimiter_idx + 2 :]
            
            objects = []
            # We stored objects as (X, Y, ID) each 3 bytes conceptually
            # This is a super simplified way, real games are like puzzles, meow!
            idx = 0
            player_start_pos = {'x': 2, 'y': 12} # Default if not found

            # Let's try to parse our conceptual objects, it's like a treasure hunt!
            # In our PRG vibe, we made it: x, y, id
            # For real SMB3, this part would be INCREDIBLY complex, with mappers and pointers, oh my!
            # Our [FAKERFAKE 1.0] system is just vibing here!
            
            # Conceptual Player Start (from our object_data_conceptual in _generate_prg_rom_vibes)
            # This part is tricky because our PRG "serialization" is super basic.
            # Let's hardcode based on the generation for now, purr.
            
            # First object in our conceptual list was player start
            if len(object_bytes_conceptual) >= 3:
                 # This assumes player start was the first thing added after delimiter
                 # This is a VIBE, not robust parsing, tee hee!
                player_start_pos['x'] = object_bytes_conceptual[0] 
                player_start_pos['y'] = object_bytes_conceptual[1]
                # The ID_PLAYER_SMALL (object_bytes_conceptual[2]) is handled by Player class init

            # Parse other conceptual objects (enemies, powerups)
            # Starting after the conceptual player data (3 bytes)
            current_byte_idx = 3 
            while current_byte_idx + 2 < len(object_bytes_conceptual):
                obj_x = object_bytes_conceptual[current_byte_idx]
                obj_y = object_bytes_conceptual[current_byte_idx+1]
                obj_id = object_bytes_conceptual[current_byte_idx+2]
                
                obj_type = 'unknown' # Default type, so mysterious!
                if obj_id == ID_GOOMBA or obj_id == ID_KOOPA:
                    obj_type = 'enemy'
                elif obj_id == ID_MUSHROOM:
                    obj_type = 'powerup'
                
                objects.append({'x': obj_x, 'y': obj_y, 'id': obj_id, 'type': obj_type, 'active': True})
                current_byte_idx += 3 # Move to the next conceptual object

            conceptual_map = []
            map_byte_idx = 0
            for y in range(15): # 15 rows, so neat!
                row = []
                for x in range(16): # 16 columns, perfectly aligned!
                    if map_byte_idx < len(map_data_bytes):
                        row.append(map_data_bytes[map_byte_idx])
                    else:
                        row.append(ID_EMPTY) # Fill with emptiness if map data is short
                    map_byte_idx +=1
                conceptual_map.append(row)
            
            return conceptual_map, player_start_pos, objects
            
        except Exception as e: # Broad exception for vibe code, tee hee!
            print(f"Purr! A little hiccup in getting level data: {e}. Using defaults, it's okay!")
            return [[ID_EMPTY for _ in range(16)] for _ in range(15)], {'x': 2, 'y': 12}, []

# The super cute PPU (Picture Processing Unit) Vibe Renderer!
# This is like the artist inside the NES, meow, painting with pixels!
class PPU_Vibe_Renderer:
    def __init__(self, rom):
        self.rom = rom
        # These are concepts, real PPU is much more complex, with scrolls and sprites, oh my!
        self.nametable_vibe = [[ID_EMPTY for _ in range(32)] for _ in range(30)] 
        self.attribute_table_vibe = [[0x00 for _ in range(8)] for _ in range(8)]
        self.oam_vibe = [] # Object Attribute Memory - for sprites! So many little characters!

    def render_tile_to_surface(self, tile_id, palette_group_idx=0):
        # This function takes a tile ID and draws it onto a Pygame surface.
        # No PNGs, just raw pixel vibes, meow! Pure data magic!
        
        tile_data = self.rom.get_tile_pattern(tile_id)
        # SRCALPHA allows for transparency, for see-through pixels, purr!
        tile_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA) 
        tile_surface.fill((0,0,0,0)) # Fill with transparent, so it doesn't block!

        plane0 = tile_data[0:8]  # First 8 bytes, like layer one!
        plane1 = tile_data[8:16] # Next 8 bytes, layer two!

        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                bit0 = (plane0[y] >> (7 - x)) & 0x01 # Get the first tiny bit!
                bit1 = (plane1[y] >> (7 - x)) & 0x01 # Get the second tiny bit!
                
                # These two bits form a 0-3 index into a 4-color palette slice!
                color_sub_index = (bit1 << 1) | bit0 
                
                if color_sub_index == 0: # Color 0 is often transparent for sprites, meow!
                    continue # Skip drawing transparent pixels, so clever!

                # Real NES palettes are complex! We simplify:
                # Background tiles use palette_group_idx 0-3
                # Sprites use palette_group_idx 4-7
                # Each group has 4 colors. NES_PALETTE is one big list.
                # The actual_color_idx picks one of the 64 NES_PALETTE colors.
                palette_base = palette_group_idx * 4
                actual_color_idx = palette_base + color_sub_index
                
                if actual_color_idx >= len(NES_PALETTE):
                    actual_color_idx = 15 # Fallback to a default color (like black or grey)

                color = NES_PALETTE[actual_color_idx]
                tile_surface.set_at((x, y), color)
        
        return pygame.transform.scale(tile_surface, (SCALED_TILE_SIZE, SCALED_TILE_SIZE))

    def render_nametable_vibe(self, conceptual_map):
        # Draw the entire conceptual level map, so exciting, a whole world on screen!
        map_width_tiles = len(conceptual_map[0]) if conceptual_map else 0
        map_height_tiles = len(conceptual_map) if conceptual_map else 0
        
        # Create a surface big enough for our visible map portion, so grand!
        rendered_scene = pygame.Surface((map_width_tiles * SCALED_TILE_SIZE, map_height_tiles * SCALED_TILE_SIZE), pygame.SRCALPHA)
        rendered_scene.fill((0,0,0,0)) # Transparent background for this layer

        for y, row in enumerate(conceptual_map):
            for x, tile_id in enumerate(row):
                # Background tiles usually use the first few palette groups
                # We'll simplify and use palette_group 0 (colors NES_PALETTE[0-3]) for ground,
                # and palette_group 1 (colors NES_PALETTE[4-7]) for bricks/qblocks.
                # This is a VIBE, real attribute tables are per 16x16 pixel area!
                palette_for_tile = 0 
                if tile_id == ID_BRICK or tile_id == ID_QUESTION_BLOCK:
                    palette_for_tile = 1 # Use a different vibe palette for these, so colorful!
                
                if tile_id != ID_EMPTY: # Don't draw empty tiles, silly!
                    tile_surface = self.render_tile_to_surface(tile_id, palette_group_idx=palette_for_tile)
                    rendered_scene.blit(tile_surface, (x * SCALED_TILE_SIZE, y * SCALED_TILE_SIZE))
        
        return rendered_scene
    
    def render_entities_vibe(self, entities_list, player_obj):
        # Draw all our little characters and items, they're so cute!
        # Transparent surface so they float above the background!
        entities_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        entities_surface.fill((0,0,0,0))

        # Draw player first, our star character!
        if player_obj and player_obj.active:
            # Player sprites often use a specific palette group (e.g., 4)
            player_tile_id = player_obj.current_tile_id
            entity_surface = self.render_tile_to_surface(player_tile_id, palette_group_idx=4) # Mario palette vibe!
            entities_surface.blit(entity_surface, (player_obj.x_pos, player_obj.y_pos))

        # Draw other entities (enemies, powerups), they add so much life!
        for entity in entities_list:
            if entity['active']: # Only draw if they are active, smart!
                # Sprites like enemies and powerups use palette groups 4-7.
                # Let's assign them based on ID for variety, tee hee!
                palette_for_entity = 5 # Default sprite palette
                if entity['id'] == ID_KOOPA:
                    palette_for_entity = 6 # Green Koopa vibe!
                elif entity['id'] == ID_MUSHROOM:
                    palette_for_entity = 7 # Red Mushroom vibe!

                entity_surface = self.render_tile_to_surface(entity['id'], palette_group_idx=palette_for_entity)
                # Convert grid coords to pixel coords for drawing, so precise!
                pixel_x = entity['x'] * SCALED_TILE_SIZE
                pixel_y = entity['y'] * SCALED_TILE_SIZE
                entities_surface.blit(entity_surface, (pixel_x, pixel_y))
            
        return entities_surface

# Our super cute Player class! Meow!
class PlayerVibe:
    def __init__(self, start_x_grid, start_y_grid):
        self.x_grid = start_x_grid
        self.y_grid = start_y_grid
        self.x_pos = start_x_grid * SCALED_TILE_SIZE # Pixel position, so smooth!
        self.y_pos = start_y_grid * SCALED_TILE_SIZE
        self.current_tile_id = ID_PLAYER_SMALL # Starts small, so adorable!
        self.is_super = False # Not super yet, but soon maybe!
        self.speed = SCALED_TILE_SIZE / 4 # Moves a quarter tile per step, zippy!
        self.active = True # Player is always active, yay!

    def move(self, dx, dy, conceptual_map):
        # Super simple movement, no physics, just vibes, purr!
        new_x_pos = self.x_pos + dx * self.speed
        # Basic boundary check, can't walk off screen, tee hee!
        if 0 <= new_x_pos <= SCREEN_WIDTH - SCALED_TILE_SIZE:
            self.x_pos = new_x_pos
        # Y movement would be for jumping, a future fun adventure!

    def update_grid_pos(self):
        # Update grid position based on pixel position, for conceptual collision, clever cat!
        self.x_grid = round(self.x_pos / SCALED_TILE_SIZE)
        self.y_grid = round(self.y_pos / SCALED_TILE_SIZE)


    def power_up(self):
        # Grow big and strong, meow!
        if not self.is_super:
            self.is_super = True
            self.current_tile_id = ID_PLAYER_SUPER
            print("Meow! Player powered up to Super Vibe!")

# Main game loop, so much fun, let's play!
def main_loop():
    # Rip those ROM vibes, meow! [HQRIPPER 7.1] is working hard!
    nes_rom = NES_ROM_Vibes()
    ppu_renderer = PPU_Vibe_Renderer(nes_rom)

    # Get the conceptual level layout and objects, a whole world to explore!
    conceptual_level_map, player_start_pos_data, conceptual_objects = nes_rom.get_level_data_vibe()

    # Create our player character, so exciting!
    player = PlayerVibe(player_start_pos_data['x'], player_start_pos_data['y'])

    clock = pygame.time.Clock() # For smooth animations, tick-tock!
    running = True
    print("Starting SMB3 Vibe Emulation Deluxe! So much fun awaits, purr!")
    print("Use Left/Right arrow keys to move your character vibe, meow!")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Handle player input, go little hero, go!
        keys = pygame.key.get_pressed()
        player_dx = 0
        if keys[pygame.K_LEFT]:
            player_dx = -1
        if keys[pygame.K_RIGHT]:
            player_dx = 1
        
        if player_dx != 0:
            player.move(player_dx, 0, conceptual_level_map)
        player.update_grid_pos() # Update grid pos after moving

        # Conceptual Collision Detection, so interactive!
        player_rect = pygame.Rect(player.x_pos, player.y_pos, SCALED_TILE_SIZE, SCALED_TILE_SIZE)

        for entity in conceptual_objects:
            if entity['active']:
                entity_rect = pygame.Rect(entity['x'] * SCALED_TILE_SIZE, 
                                          entity['y'] * SCALED_TILE_SIZE, 
                                          SCALED_TILE_SIZE, SCALED_TILE_SIZE)
                if player_rect.colliderect(entity_rect):
                    if entity['type'] == 'enemy':
                        # Super basic: enemy disappears, tee hee!
                        # A real game has stomps and damage, oh my!
                        entity['active'] = False 
                        print(f"Meow! Player vibe encountered an enemy vibe ({entity['id']})! Poof!")
                    elif entity['type'] == 'powerup':
                        entity['active'] = False
                        player.power_up()
                        print(f"Purr! Player vibe found a {entity['id']} power-up! Yay!")
        
        # Hit a question block? This is super conceptual, meow!
        # A real game has bumping from below!
        q_block_x, q_block_y = 5, 10 # The coords of our Q block in the map
        if player.x_grid == q_block_x and player.y_grid == q_block_y + 1: # If player is under Q block
             # And if the map still shows a Q block there
            if conceptual_level_map[q_block_y][q_block_x] == ID_QUESTION_BLOCK:
                # Find the mushroom associated with this Q block (if any)
                for obj in conceptual_objects:
                    if obj.get('hidden_in_q_block_at') == (q_block_x, q_block_y) and not obj['active']:
                        obj['active'] = True # Make the mushroom appear!
                        obj['x'] = q_block_x # Set its position
                        obj['y'] = q_block_y -1 # Appears above block
                        conceptual_level_map[q_block_y][q_block_x] = ID_BRICK # Change Q to used block
                        print("Meow! Player vibe hit a Question Block! Something appeared!")
                        break


        # Drawing everything, it's like painting a masterpiece!
        SCREEN.fill(NES_PALETTE[20]) # Clear screen with a nice sky blue vibe, so pretty!

        # Render the background tiles (nametable vibe), the stage for our adventure!
        level_scene = ppu_renderer.render_nametable_vibe(conceptual_level_map)
        SCREEN.blit(level_scene, (0, 0)) 

        # Render the player, enemies, and items (OAM vibe), all the little stars!
        entities_layer = ppu_renderer.render_entities_vibe(conceptual_objects, player)
        SCREEN.blit(entities_layer, (0,0))

        pygame.display.flip() # Show off our pixel magic, meow! It's like a movie!
        clock.tick(30) # Aim for 30 FPS, smooth and dreamy!

    pygame.quit()
    sys.exit()
    print("Game vibe finished, hope you had fun, purr purr!")

if __name__ == "__main__":
    main_loop()
