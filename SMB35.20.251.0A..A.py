import pygame
import sys
import random

# Initialize Pygame, so cute and ready for fun!
pygame.init()

# Screen dimensions, just like a little window into the NES world, purr!
SCREEN_WIDTH = 512  # NES Resolution (256x240) scaled up, so lovely!
SCREEN_HEIGHT = 480
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SMB3 ROM Vibe Emulation Deluxe - CHR Viewer Magic, Meow!")

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
ID_EMPTY = 0x00
ID_GROUND = 0x01
ID_BRICK = 0x02
ID_QUESTION_BLOCK = 0x03
ID_GOOMBA = 0x04
ID_KOOPA = 0x05
ID_PLAYER_SMALL = 0x06
ID_PLAYER_SUPER = 0x07
ID_MUSHROOM = 0x08

class NES_ROM_Vibes:
    def __init__(self, prg_rom_size_kb=256, chr_rom_size_kb=128):
        self.prg_rom_size = prg_rom_size_kb * 1024
        self.chr_rom_size = chr_rom_size_kb * 1024 
        self.prg_rom = self._generate_prg_rom_vibes()
        self.chr_rom = self._generate_chr_rom_vibes()
        print(f"Meow! Ripped/Generated PRG-ROM vibes with [HQRIPPER 7.1]: {len(self.prg_rom)} bytes! It's like a treasure chest of data!")
        print(f"Purr! Ripped/Generated CHR-ROM vibes with [DELTA-BUSTER]: {len(self.chr_rom)} bytes! Full of sparkly pixels!")

    def _generate_prg_rom_vibes(self):
        level_map_data = []
        for y in range(15):
            row = []
            for x in range(16):
                if y == 13: row.append(ID_GROUND) 
                elif y == 10 and (x == 4 or x == 6): row.append(ID_BRICK)
                elif y == 10 and x == 5: row.append(ID_QUESTION_BLOCK)
                elif y == 8 and x == 7: row.append(ID_BRICK)
                else: row.append(ID_EMPTY)
            level_map_data.extend(row)
        object_data_conceptual = [
            {'x': 3, 'y': 12, 'id': ID_PLAYER_SMALL, 'type': 'player_start'},
            {'x': 8, 'y': 12, 'id': ID_GOOMBA, 'type': 'enemy'},
            {'x': 11, 'y': 12, 'id': ID_KOOPA, 'type': 'enemy'},
            {'x': 5, 'y': 9, 'id': ID_MUSHROOM, 'type': 'powerup', 'hidden_in_q_block_at': (5,10)},
        ]
        prg_bytes = bytearray(level_map_data)
        prg_bytes.extend(bytearray([0xFF, 0xFF]))
        for obj in object_data_conceptual:
            prg_bytes.extend(bytearray([obj['x'], obj['y'], obj['id']]))
        remaining_space = self.prg_rom_size - len(prg_bytes)
        if remaining_space > 0:
            # [FAKERFAKE 1.0] filling with mysterious data!
            prg_bytes.extend(bytearray(random.getrandbits(8) for _ in range(remaining_space)))
        elif remaining_space < 0:
            prg_bytes = prg_bytes[:self.prg_rom_size]
        return prg_bytes

    def _generate_chr_rom_vibes(self):
        # [DELTA-BUSTER] is dreaming up these lovely pixel patterns!
        chr_bytes = bytearray()
        chr_bytes.extend(bytearray([0x00] * 16)) # ID_EMPTY
        chr_bytes.extend(bytearray([0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF, 0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])) # ID_GROUND
        chr_bytes.extend(bytearray([0x55,0xAA,0x55,0xAA,0x55,0xAA,0x55,0xAA, 0xAA,0x55,0xAA,0x55,0xAA,0x55,0xAA,0x55])) # ID_BRICK
        chr_bytes.extend(bytearray([0x00,0x3C,0x66,0x60,0x38,0x00,0x20,0x20, 0x00,0x3C,0x7E,0x7E,0x7E,0x3C,0x00,0x00])) # ID_QUESTION_BLOCK
        chr_bytes.extend(bytearray([0x00,0x3C,0x7E,0xFF,0xFF,0x7E,0x3C,0x00, 0x00,0x00,0x18,0x3C,0x3C,0x18,0x00,0x00])) # ID_GOOMBA
        chr_bytes.extend(bytearray([0x00,0x18,0x3C,0x7E,0x7E,0x3C,0x18,0x00, 0x00,0x24,0x24,0x7E,0x7E,0x24,0x24,0x00])) # ID_KOOPA
        chr_bytes.extend(bytearray([0x0C,0x1E,0x3F,0x0E,0x0E,0x3E,0x63,0x00, 0x0C,0x1E,0x0E,0x1E,0x3E,0x0E,0x00,0x00])) # ID_PLAYER_SMALL
        chr_bytes.extend(bytearray([0x18,0x3C,0x7E,0x18,0x18,0x7E,0xC3,0x00, 0x18,0x3C,0x18,0x3C,0x7E,0x18,0x00,0x00])) # ID_PLAYER_SUPER
        chr_bytes.extend(bytearray([0x00,0x3C,0x7E,0x7E,0xFF,0xFF,0x00,0x00, 0x00,0x00,0x24,0x24,0x24,0x3C,0x00,0x00])) # ID_MUSHROOM
        current_len = len(chr_bytes)
        remaining_space = self.chr_rom_size - current_len
        if remaining_space > 0:
            # [COPYRIGHT NOVA] ensuring our random pixel art is unique!
            chr_bytes.extend(bytearray(random.getrandbits(8) for _ in range(remaining_space)))
        elif remaining_space < 0:
            chr_bytes = chr_bytes[:self.chr_rom_size]
        return chr_bytes

    def get_tile_pattern(self, tile_id):
        offset = tile_id * 16
        if offset + 16 > len(self.chr_rom):
            print(f"Whoops! Tile ID {tile_id} is out of CHR-ROM bounds! Generating placeholder, meow!")
            return bytearray([0x00] * 16) 
        return self.chr_rom[offset : offset + 16]

    def get_level_data_vibe(self):
        try:
            delimiter_idx = -1
            for i in range(len(self.prg_rom) -1):
                if self.prg_rom[i] == 0xFF and self.prg_rom[i+1] == 0xFF:
                    delimiter_idx = i; break
            if delimiter_idx == -1:
                return [[ID_EMPTY for _ in range(16)] for _ in range(15)], {'x':2,'y':12}, []
            map_data_bytes = self.prg_rom[:delimiter_idx]
            object_bytes_conceptual = self.prg_rom[delimiter_idx + 2 :]
            objects = []; player_start_pos = {'x': 2, 'y': 12}
            if len(object_bytes_conceptual) >= 3:
                player_start_pos['x'] = object_bytes_conceptual[0] 
                player_start_pos['y'] = object_bytes_conceptual[1]
            current_byte_idx = 3 
            while current_byte_idx + 2 < len(object_bytes_conceptual):
                obj_x, obj_y, obj_id = object_bytes_conceptual[current_byte_idx:current_byte_idx+3]
                obj_type = 'enemy' if obj_id in [ID_GOOMBA, ID_KOOPA] else 'powerup' if obj_id == ID_MUSHROOM else 'unknown'
                objects.append({'x': obj_x, 'y': obj_y, 'id': obj_id, 'type': obj_type, 'active': True})
                current_byte_idx += 3
            conceptual_map = []; map_byte_idx = 0
            for y in range(15):
                row = []
                for x in range(16):
                    row.append(map_data_bytes[map_byte_idx] if map_byte_idx < len(map_data_bytes) else ID_EMPTY)
                    map_byte_idx +=1
                conceptual_map.append(row)
            return conceptual_map, player_start_pos, objects
        except Exception as e:
            print(f"Purr! A little hiccup in getting level data: {e}. Using defaults, it's okay!")
            return [[ID_EMPTY for _ in range(16)] for _ in range(15)], {'x': 2, 'y': 12}, []

class PPU_Vibe_Renderer:
    def __init__(self, rom):
        self.rom = rom
        self.chr_sheet_surface = None # Cache for our lovely CHR sheet, meow!

    def render_tile_to_surface(self, tile_id, palette_group_idx=0):
        tile_data = self.rom.get_tile_pattern(tile_id)
        tile_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        tile_surface.fill((0,0,0,0))
        plane0, plane1 = tile_data[0:8], tile_data[8:16]
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                bit0 = (plane0[y] >> (7 - x)) & 0x01
                bit1 = (plane1[y] >> (7 - x)) & 0x01
                color_sub_index = (bit1 << 1) | bit0 
                if color_sub_index == 0: continue
                actual_color_idx = (palette_group_idx * 4) + color_sub_index
                if actual_color_idx >= len(NES_PALETTE): actual_color_idx = 15
                color = NES_PALETTE[actual_color_idx]
                tile_surface.set_at((x, y), color)
        return pygame.transform.scale(tile_surface, (SCALED_TILE_SIZE, SCALED_TILE_SIZE))

    def render_nametable_vibe(self, conceptual_map):
        map_width_tiles = len(conceptual_map[0]) if conceptual_map else 0
        map_height_tiles = len(conceptual_map) if conceptual_map else 0
        rendered_scene = pygame.Surface((map_width_tiles*SCALED_TILE_SIZE, map_height_tiles*SCALED_TILE_SIZE), pygame.SRCALPHA)
        rendered_scene.fill((0,0,0,0))
        for y, row in enumerate(conceptual_map):
            for x, tile_id in enumerate(row):
                palette_for_tile = 1 if tile_id == ID_BRICK or tile_id == ID_QUESTION_BLOCK else 0
                if tile_id != ID_EMPTY:
                    tile_surface = self.render_tile_to_surface(tile_id, palette_group_idx=palette_for_tile)
                    rendered_scene.blit(tile_surface, (x * SCALED_TILE_SIZE, y * SCALED_TILE_SIZE))
        return rendered_scene
    
    def render_entities_vibe(self, entities_list, player_obj):
        entities_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        entities_surface.fill((0,0,0,0))
        if player_obj and player_obj.active:
            entity_surface = self.render_tile_to_surface(player_obj.current_tile_id, palette_group_idx=4)
            entities_surface.blit(entity_surface, (player_obj.x_pos, player_obj.y_pos))
        for entity in entities_list:
            if entity['active']:
                palette_for_entity = 6 if entity['id'] == ID_KOOPA else 7 if entity['id'] == ID_MUSHROOM else 5
                entity_surface = self.render_tile_to_surface(entity['id'], palette_group_idx=palette_for_entity)
                entities_surface.blit(entity_surface, (entity['x']*SCALED_TILE_SIZE, entity['y']*SCALED_TILE_SIZE))
        return entities_surface

    # New function to render the CHR ROM sheet, purr! It's like a gallery of pixels!
    def render_chr_rom_sheet(self, default_palette_group=0):
        if self.chr_sheet_surface: # Use cached surface if available, so speedy!
            return self.chr_sheet_surface

        print("Purr! Generating CHR ROM sheet for the first time, so exciting!")
        tiles_per_row = SCREEN_WIDTH // SCALED_TILE_SIZE
        num_rows = SCREEN_HEIGHT // SCALED_TILE_SIZE
        max_tiles_in_rom = len(self.rom.chr_rom) // 16 # Each tile is 16 bytes, meow!
        
        # Surface to draw all our pretty tiles on!
        sheet_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        sheet_surface.fill((30,30,60,200)) # A nice dark blue translucent background, so stylish!

        for i in range(min(tiles_per_row * num_rows, max_tiles_in_rom)):
            tile_id = i
            row = i // tiles_per_row
            col = i % tiles_per_row
            
            # Render each tile using the default palette group, like a little artist!
            # This shows the raw patterns from the "hex values" (bytes)
            tile_surface = self.render_tile_to_surface(tile_id, palette_group_idx=default_palette_group)
            
            # Draw the tile onto our big sheet, purrfectly aligned!
            sheet_surface.blit(tile_surface, (col * SCALED_TILE_SIZE, row * SCALED_TILE_SIZE))
        
        self.chr_sheet_surface = sheet_surface # Cache for next time, clever kitty!
        return sheet_surface


class PlayerVibe:
    def __init__(self, start_x_grid, start_y_grid):
        self.x_grid, self.y_grid = start_x_grid, start_y_grid
        self.x_pos, self.y_pos = start_x_grid*SCALED_TILE_SIZE, start_y_grid*SCALED_TILE_SIZE
        self.current_tile_id = ID_PLAYER_SMALL
        self.is_super = False
        self.speed = SCALED_TILE_SIZE / 4
        self.active = True

    def move(self, dx, dy, conceptual_map):
        new_x_pos = self.x_pos + dx * self.speed
        if 0 <= new_x_pos <= SCREEN_WIDTH - SCALED_TILE_SIZE: self.x_pos = new_x_pos

    def update_grid_pos(self):
        self.x_grid = round(self.x_pos / SCALED_TILE_SIZE)
        self.y_grid = round(self.y_pos / SCALED_TILE_SIZE)

    def power_up(self):
        if not self.is_super:
            self.is_super = True; self.current_tile_id = ID_PLAYER_SUPER
            print("Meow! Player powered up to Super Vibe!")

def main_loop():
    nes_rom = NES_ROM_Vibes()
    ppu_renderer = PPU_Vibe_Renderer(nes_rom)
    conceptual_level_map, player_start_pos_data, conceptual_objects = nes_rom.get_level_data_vibe()
    player = PlayerVibe(player_start_pos_data['x'], player_start_pos_data['y'])
    clock = pygame.time.Clock(); running = True
    
    # New state for our CHR ROM viewer, meow!
    show_chr_rom_view = False 
    # Let's pre-generate the CHR sheet once if CHR ROM doesn't change
    # If CHR ROM could change, this would need to be regenerated or PPU notified.
    # For now, our CHR ROM is static after init, so this is fine!
    # Actually, let's make it generate on demand or toggle to avoid initial slowdown if not used.
    # The PPU class now caches it internally, which is even better, purr!

    print("Starting SMB3 Vibe Emulation Deluxe! So much fun awaits, purr!")
    print("Use Left/Right arrow keys to move your character vibe, meow!")
    print("Press 'C' to toggle the CHR ROM Tile Viewer, like magic glasses for pixels!")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN: # Key press events, so exciting!
                if event.key == pygame.K_c: # 'C' for CHR ROM viewer, clever kitty!
                    show_chr_rom_view = not show_chr_rom_view
                    if show_chr_rom_view:
                        print("Meow! Switched to CHR ROM Viewer mode! Look at all the pretty tiles!")
                        # Invalidate cache if we want to allow palette changes for CHR view later.
                        # ppu_renderer.chr_sheet_surface = None # Example if we wanted to force regen
                    else:
                        print("Purr! Switched back to Game Vibe mode! Adventure time!")
        
        if not show_chr_rom_view: # Only update game logic if not in CHR view, makes sense!
            keys = pygame.key.get_pressed()
            player_dx = 0
            if keys[pygame.K_LEFT]: player_dx = -1
            if keys[pygame.K_RIGHT]: player_dx = 1
            if player_dx != 0: player.move(player_dx, 0, conceptual_level_map)
            player.update_grid_pos()

            player_rect = pygame.Rect(player.x_pos, player.y_pos, SCALED_TILE_SIZE, SCALED_TILE_SIZE)
            for entity in conceptual_objects:
                if entity['active']:
                    entity_rect = pygame.Rect(entity['x']*SCALED_TILE_SIZE, entity['y']*SCALED_TILE_SIZE, SCALED_TILE_SIZE, SCALED_TILE_SIZE)
                    if player_rect.colliderect(entity_rect):
                        if entity['type'] == 'enemy':
                            entity['active'] = False 
                            print(f"Meow! Player vibe encountered an enemy vibe ({entity['id']})! Poof!")
                        elif entity['type'] == 'powerup':
                            entity['active'] = False; player.power_up()
                            print(f"Purr! Player vibe found a {entity['id']} power-up! Yay!")
            
            q_block_x, q_block_y = 5, 10
            if player.x_grid == q_block_x and player.y_grid == q_block_y + 1:
                if conceptual_level_map[q_block_y][q_block_x] == ID_QUESTION_BLOCK:
                    for obj in conceptual_objects:
                        if obj.get('hidden_in_q_block_at') == (q_block_x, q_block_y) and not obj['active']:
                            obj['active'] = True; obj['x'] = q_block_x; obj['y'] = q_block_y -1
                            conceptual_level_map[q_block_y][q_block_x] = ID_BRICK
                            print("Meow! Player vibe hit a Question Block! Something appeared!")
                            break

        # Drawing everything, it's like painting a masterpiece!
        if show_chr_rom_view:
            # Display the entire CHR ROM sheet, like a magical tapestry of pixels!
            # Using default_palette_group 0, which uses NES_PALETTE colors 0-3 for tile colors 0-3.
            # This is how we "display the code from the hex values"! So neat!
            chr_sheet = ppu_renderer.render_chr_rom_sheet(default_palette_group=0) 
            SCREEN.blit(chr_sheet, (0,0))
        else:
            # Normal game rendering, our little adventure world!
            SCREEN.fill(NES_PALETTE[20]) 
            level_scene = ppu_renderer.render_nametable_vibe(conceptual_level_map)
            SCREEN.blit(level_scene, (0, 0)) 
            entities_layer = ppu_renderer.render_entities_vibe(conceptual_objects, player)
            SCREEN.blit(entities_layer, (0,0))

        pygame.display.flip() 
        clock.tick(30) 

    pygame.quit()
    sys.exit()
    print("Game vibe finished, hope you had fun with the pixel magic, purr purr!")

if __name__ == "__main__":
    main_loop()
