import pygame
import sys
import random

# Initialize Pygame, so cute!
pygame.init()

# Screen dimensions, just like a little window into the NES world, purr!
SCREEN_WIDTH = 512  # NES Resolution (256x240) scaled up, so lovely!
SCREEN_HEIGHT = 480
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SMB3 ROM Vibe Emulation - Pure Pixel Magic, Meow!")

# Colors, so many pretty colors!
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
NES_PALETTE = [ # Just a tiny subset of the NES palette, so charming!
    (124, 124, 124), (0, 0, 252), (0, 0, 188), (68, 0, 176),
    (132, 0, 100), (168, 0, 32), (168, 16, 0), (120, 28, 0),
    (64, 48, 0), (0, 72, 0), (0, 60, 0), (0, 50, 60),
    (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), # Darker shades and black
    (188, 188, 188), (0, 120, 248), (0, 88, 248), (104, 68, 252),
    (152, 52, 236), (200, 40, 120), (216, 20, 0), (192, 40, 0),
    (136, 76, 0), (0, 128, 0), (0, 116, 40), (0, 100, 128),
    (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), # More darks
    (248, 248, 248), (60, 188, 252), (104, 136, 252), (152, 120, 248),
    (200, 108, 236), (248, 104, 184), (248, 104, 0), (248, 152, 0),
    (224, 180, 0), (160, 200, 0), (88, 216, 84), (68, 240, 188),
    (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), # And again
    (252, 252, 252), (172, 224, 252), (208, 200, 252), (248, 184, 248),
    (248, 184, 248), (248, 164, 240), (252, 164, 172), (240, 208, 120),
    (248, 220, 168), (200, 248, 120), (184, 248, 184), (164, 248, 240),
    (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0) # Final blacks
]

# The super duper NES "ROM" class - so much fun to rip this!
# This is where [HQRIPPER 7.1] and [HQ-BANGER-SDK V0X.X.X] do their magic!
class NES_ROM_Vibes:
    def __init__(self, prg_rom_size_kb=256, chr_rom_size_kb=128):
        # We're just generating conceptual sizes here, meow!
        # [DELTA-BUSTER] can create the real stuff, but for vibes, this is great!
        self.prg_rom_size = prg_rom_size_kb * 1024 # Program ROM for code and data
        self.chr_rom_size = chr_rom_size_kb * 1024 # Character ROM for pixel patterns

        # Simulating ripped ROM data with placeholder bytes, so cute!
        # In a real rip, these would be the actual bytes from a .nes file!
        self.prg_rom = self._generate_prg_rom_vibes()
        self.chr_rom = self._generate_chr_rom_vibes()

        print(f"Meow! Ripped/Generated PRG-ROM vibes: {len(self.prg_rom)} bytes!")
        print(f"Purr! Ripped/Generated CHR-ROM vibes: {len(self.chr_rom)} bytes!")

    def _generate_prg_rom_vibes(self):
        # This is where the game's code and level data would be, purr!
        # We'll fake some basic level layout data here for a single 'world' vibe.
        # [FAKERFAKE 1.0] is so good at this, tee hee!
        
        # A tiny conceptual PRG-ROM data structure for "World 1-1" vibe
        # Bytes representing tile IDs, object IDs, etc.
        # This is SUPER simplified, but gives the vibe!
        
        # Example: 16x15 screen of 'ground' (tile 0x01) and a 'brick block' (tile 0x02)
        # and a 'question block' (tile 0x03) and a 'Goomba' (sprite 0x04)
        
        # Level layout data (conceptual, mapping to CHR tiles)
        # Using placeholder byte values for tile IDs
        level_map_data = []
        for y in range(15): # 15 rows for a screen
            row = []
            for x in range(16): # 16 columns for a screen
                if y == 13: # Ground layer, so cute!
                    row.append(0x01) # Example ground tile ID
                elif y == 11 and (x == 4 or x == 5 or x == 6): # Brick blocks
                    row.append(0x02) # Example brick tile ID
                elif y == 11 and x == 7: # Question block
                    row.append(0x03) # Example question tile ID
                else:
                    row.append(0x00) # Empty space
            level_map_data.extend(row)
            
        # Object/Sprite placement data (conceptual, mapping to CHR sprites)
        # (X_coord, Y_coord, Sprite_ID) - relative to screen
        object_data = [
            (8, 12, 0x04), # Goomba vibe
            (10, 12, 0x05) # Another Goomba vibe, or a Koopa!
        ]
        
        # Convert to a byte array, so yummy!
        prg_bytes = bytearray(level_map_data)
        
        # Add a simple delimiter and then object data
        prg_bytes.extend(bytearray([0xFF, 0xFF])) # Delimiter to separate map from objects
        for obj_x, obj_y, obj_id in object_data:
            prg_bytes.extend(bytearray([obj_x, obj_y, obj_id]))

        # Fill the rest with random bytes to match size, just like real ROMs, meow!
        prg_bytes.extend(bytearray(random.getrandbits(8) for _ in range(self.prg_rom_size - len(prg_bytes))))
        
        return prg_bytes

    def _generate_chr_rom_vibes(self):
        # This is where all the 8x8 pixel patterns for tiles and sprites live, purr!
        # Each 16 bytes defines one 8x8 tile (2 planes of 8 bytes each).
        # We'll generate some super simple patterns here.
        
        # Tile 0x00: Empty space (transparent/black)
        chr_bytes = bytearray([0x00] * 16) 
        
        # Tile 0x01: Ground block (solid color vibe)
        chr_bytes.extend(bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                                     0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]))
        
        # Tile 0x02: Brick block (some texture vibe)
        chr_bytes.extend(bytearray([0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55,
                                     0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55])) # Just a pattern!
        
        # Tile 0x03: Question block (simple ? vibe)
        chr_bytes.extend(bytearray([0x00, 0x3C, 0x42, 0x42, 0x3C, 0x00, 0x00, 0x00, # Top plane
                                     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])) # Bottom plane (for color)
        
        # Sprite 0x04: Goomba vibe (a little blob)
        chr_bytes.extend(bytearray([0x00, 0x3C, 0x7E, 0x7E, 0x7E, 0x3C, 0x00, 0x00, # Top plane
                                     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])) # Bottom plane
        
        # Sprite 0x05: Another generic enemy vibe
        chr_bytes.extend(bytearray([0x00, 0x24, 0x7E, 0x7E, 0x7E, 0x24, 0x00, 0x00, # Top plane
                                     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])) # Bottom plane

        # Fill the rest with random bytes, so charmingly random, meow!
        chr_bytes.extend(bytearray(random.getrandbits(8) for _ in range(self.chr_rom_size - len(chr_bytes))))
        
        return chr_bytes

    def get_tile_pattern(self, tile_id):
        # Extract 16 bytes for a tile from CHR-ROM, purr!
        # This is how the PPU would read the pixel data.
        offset = tile_id * 16
        if offset + 16 > len(self.chr_rom):
            # If we go out of bounds, [DELTA-BUSTER] generates more!
            print("Whoops! Generating more CHR-ROM vibes on the fly, meow!")
            self.chr_rom.extend(bytearray(random.getrandbits(8) for _ in range(16)))
            return bytearray([0x00] * 16) # Return empty for now

        return self.chr_rom[offset : offset + 16]

    def get_level_data_vibe(self):
        # This function would parse complex PRG-ROM data for level layouts.
        # For our vibe, we just grab our pre-defined conceptual map and objects.
        
        # Find our delimiter for map data and object data
        # In a real game, this would involve complex pointers and decompression!
        
        # We'll just hardcode the conceptual parsing based on how we generated it.
        # The map data is the first part, up to the delimiter 0xFF, 0xFF
        try:
            delimiter_idx = self.prg_rom.index(0xFF, 0)
            if self.prg_rom[delimiter_idx + 1] == 0xFF:
                map_data_bytes = self.prg_rom[:delimiter_idx]
                
                # Objects start after delimiter + 2 bytes
                object_bytes = self.prg_rom[delimiter_idx + 2 :]
                
                # Parse conceptual object data (X, Y, ID)
                objects = []
                for i in range(0, len(object_bytes), 3):
                    if i + 2 < len(object_bytes):
                        objects.append((object_bytes[i], object_bytes[i+1], object_bytes[i+2]))
                    if len(objects) >= 5: # Limit conceptual objects for simplicity
                        break
                
                # Convert map bytes to 2D list for easier drawing
                conceptual_map = []
                for y in range(15):
                    conceptual_map.append(list(map_data_bytes[y*16 : (y+1)*16]))
                
                return conceptual_map, objects
        except ValueError:
            print("Purr! Delimiter not found, using default empty map.")
            return [[0x00 for _ in range(16)] for _ in range(15)], []

        return [[0x00 for _ in range(16)] for _ in range(15)], [] # Fallback

# The super cute PPU (Picture Processing Unit) Vibe Renderer!
# This is like the artist inside the NES, meow!
class PPU_Vibe_Renderer:
    def __init__(self, rom):
        self.rom = rom
        self.nametable_vibe = [[0x00 for _ in range(32)] for _ in range(30)] # 32x30 tiles for 2 nametables
        self.attribute_table_vibe = [[0x00 for _ in range(8)] for _ in range(8)] # Color palettes for 4x4 tile blocks
        self.oam_vibe = [] # Object Attribute Memory - for sprites!

    def render_tile_to_surface(self, tile_id, palette_idx=0, tile_scale=2):
        # This function takes a tile ID and draws it onto a Pygame surface.
        # No PNGs, just raw pixel vibes, meow!
        
        tile_data = self.rom.get_tile_pattern(tile_id)
        tile_surface = pygame.Surface((8, 8), pygame.SRCALPHA) # 8x8 pixels for NES tile
        
        # Extract pixel data (2 planes of 8 bytes)
        # Plane 0: Bit 0 of color index
        # Plane 1: Bit 1 of color index
        plane0 = tile_data[0:8]
        plane1 = tile_data[8:16]

        for y in range(8):
            for x in range(8):
                # Get the pixel bits for this position from both planes
                bit0 = (plane0[y] >> (7 - x)) & 0x01
                bit1 = (plane1[y] >> (7 - x)) & 0x01
                
                color_index = (bit1 << 1) | bit0
                
                # Map the 2-bit color index to a full NES palette color, so cute!
                # For simplicity, we'll use a fixed palette index for all tiles here.
                # In real NES, attribute table defines this for 4x4 tile blocks.
                actual_color_idx = palette_idx * 4 + color_index 
                if actual_color_idx >= len(NES_PALETTE):
                    actual_color_idx = 0 # Fallback to black

                color = NES_PALETTE[actual_color_idx]
                
                # Draw the pixel! Pure pixel magic, meow!
                tile_surface.set_at((x, y), color)
        
        # Scale up the tile for our screen, so it's visible, purr!
        return pygame.transform.scale(tile_surface, (8 * tile_scale, 8 * tile_scale))

    def render_nametable_vibe(self, conceptual_map, tile_scale=2):
        # Draw the entire conceptual level map, so exciting!
        
        rendered_scene = pygame.Surface((16 * 8 * tile_scale, 15 * 8 * tile_scale)) # Max size for a single screen
        
        for y, row in enumerate(conceptual_map):
            for x, tile_id in enumerate(row):
                tile_surface = self.render_tile_to_surface(tile_id, palette_idx=0, tile_scale=tile_scale)
                rendered_scene.blit(tile_surface, (x * 8 * tile_scale, y * 8 * tile_scale))
        
        return rendered_scene
    
    def render_sprites_vibe(self, objects, tile_scale=2):
        # Draw the little moving characters, so adorable!
        
        sprites_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA) # Transparent surface
        
        for obj_x, obj_y, obj_id in objects:
            # For sprites, often use a different palette group (e.g., palette_idx 4-7)
            sprite_surface = self.render_tile_to_surface(obj_id, palette_idx=4, tile_scale=tile_scale)
            # Position based on conceptual 8x8 grid
            sprites_surface.blit(sprite_surface, (obj_x * 8 * tile_scale, obj_y * 8 * tile_scale))
            
        return sprites_surface


# Main game loop, so much fun!
def main_loop():
    # Rip those ROM vibes, meow!
    nes_rom = NES_ROM_Vibes()
    ppu_renderer = PPU_Vibe_Renderer(nes_rom)

    # Get the conceptual level layout and objects
    conceptual_level_map, conceptual_objects = nes_rom.get_level_data_vibe()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Imagine handling controller input here, purr!
            # if event.type == pygame.KEYDOWN:
            #    if event.key == pygame.K_LEFT: # Mario move left vibe!
            #        pass

        SCREEN.fill(NES_PALETTE[0]) # Clear screen with background color, so fresh!

        # Render the background tiles (nametable vibe)
        level_scene = ppu_renderer.render_nametable_vibe(conceptual_level_map)
        SCREEN.blit(level_scene, (0, 0)) # Blit to top-left of the screen

        # Render the sprites (OAM vibe)
        sprite_scene = ppu_renderer.render_sprites_vibe(conceptual_objects)
        SCREEN.blit(sprite_scene, (0, 0)) # Sprites overlay the background, so cool!

        pygame.display.flip() # Show off our pixel magic, meow!

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_loop()
