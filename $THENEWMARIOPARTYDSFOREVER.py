import platform
import pygame
import sys
import random
import base64
from io import BytesIO
import asyncio

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)

# Generate simple image surfaces and convert to base64
def create_surface_to_base64(color, shape=None):
    surface = pygame.Surface((40, 40), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))  # Transparent background
    if shape == "star":
        pygame.draw.polygon(surface, color, [(20, 5), (25, 15), (35, 15), (27, 22), (30, 30), (20, 25), (10, 30), (13, 22), (5, 15), (15, 15)])
    elif shape == "mario":
        pygame.draw.rect(surface, RED, (15, 10, 10, 10))  # Hat
        pygame.draw.rect(surface, (255, 204, 153), (10, 20, 20, 10))  # Face
        pygame.draw.rect(surface, BLUE, (10, 30, 20, 10))  # Body
    else:
        pygame.draw.rect(surface, color, (5, 5, 30, 30))
    buf = BytesIO()
    pygame.image.save(surface, buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# Embedded Assets (Base64-encoded programmatically generated images)
BLUE_SPACE_DATA = create_surface_to_base64(BLUE)
RED_SPACE_DATA = create_surface_to_base64(RED)
HAPPENING_SPACE_DATA = create_surface_to_base64(GREEN)
STAR_SPACE_DATA = create_surface_to_base64(YELLOW, "star")
CHANCE_SPACE_DATA = create_surface_to_base64(PURPLE)
MARIO_SPRITE_DATA = create_surface_to_base64(RED, "mario")

# Load Surfaces
blue_space_surface = pygame.image.load(BytesIO(base64.b64decode(BLUE_SPACE_DATA)))
red_space_surface = pygame.image.load(BytesIO(base64.b64decode(RED_SPACE_DATA)))
happening_space_surface = pygame.image.load(BytesIO(base64.b64decode(HAPPENING_SPACE_DATA)))
star_space_surface = pygame.image.load(BytesIO(base64.b64decode(STAR_SPACE_DATA)))
chance_space_surface = pygame.image.load(BytesIO(base64.b64decode(CHANCE_SPACE_DATA)))
mario_sprite = pygame.image.load(BytesIO(base64.b64decode(MARIO_SPRITE_DATA)))

# Fonts
FONT = pygame.font.SysFont("comicsansms", 24)

def draw_text(text, color, x, y):
    label = FONT.render(text, True, color)
    SCREEN.blit(label, (x, y))

class Button:
    def __init__(self, text, x, y, width=150, height=40, visible=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = RED
        self.visible = visible
    
    def draw(self):
        if self.visible:
            pygame.draw.rect(SCREEN, self.color, self.rect)
            draw_text(self.text, WHITE, self.rect.x + 10, self.rect.y + 10)
    
    def is_clicked(self, pos):
        return self.visible and self.rect.collidepoint(pos)

class Player:
    def __init__(self, name, sprite):
        self.name = name
        self.sprite = sprite
        self.position = 0
        self.coins = 10
        self.stars = 0

    def draw(self):
        tile = self.tiles[self.position]
        x = tile.rect.centerx - self.sprite.get_width() // 2
        y = tile.rect.centery - self.sprite.get_height() // 2
        SCREEN.blit(self.sprite, (x, y))

class BoardTile:
    def __init__(self, tile_type, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.type = tile_type
        self.surface = {
            "blue": blue_space_surface,
            "red": red_space_surface,
            "happening": happening_space_surface,
            "star": star_space_surface,
            "chance": chance_space_surface
        }[tile_type]

    def draw(self):
        SCREEN.blit(self.surface, self.rect)

    def trigger_effect(self, player):
        if self.type == "blue":
            player.coins += 3
            return "+3 coins!"
        elif self.type == "red":
            player.coins = max(0, player.coins - 3)
            return "-3 coins!"
        elif self.type == "star":
            if player.coins >= 20:
                player.coins -= 20
                player.stars += 1
                return "Bought a star for 20 coins!"
            return "Need 20 coins for a star!"
        elif self.type == "happening":
            return "Happening event triggered!"
        elif self.type == "chance":
            event = random.choice(["gain", "lose"])
            if event == "gain":
                player.coins += 5
                return "+5 coins from chance!"
            else:
                player.coins = max(0, player.coins - 5)
                return "-5 coins from chance!"
        return ""

class MarioPartyGame:
    def __init__(self):
        self.players = [Player("Mario", mario_sprite)]
        self.tiles = []
        self.current_player = 0
        self.dice_roll = 0
        self.phase = "roll"
        self.log_message = ""
        self.command_input = ""
        self.entering_command = False
        self.generate_board()
        self.buttons = [
            Button("Roll Dice", WIDTH - 200, HEIGHT - 100),
            Button("Next Turn", WIDTH - 200, HEIGHT - 50, visible=False)
        ]

    def generate_board(self):
        tile_sequence = ["blue", "blue", "red", "happening", "star", "blue", "chance", "red", "blue"]
        x, y = 50, HEIGHT - 50
        for tile_type in tile_sequence:
            self.tiles.append(BoardTile(tile_type, x, y))
            x += 50
            if x > WIDTH - 50:
                x = 50
                y -= 50
        for player in self.players:
            player.tiles = self.tiles

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and not self.entering_command:
                pos = pygame.mouse.get_pos()
                for btn in self.buttons:
                    if btn.is_clicked(pos):
                        if btn.text == "Roll Dice" and self.phase == "roll":
                            self.roll_dice()
                        elif btn.text == "Next Turn" and self.phase == "effect":
                            self.next_turn()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SLASH and self.phase == "roll":
                    self.entering_command = True
                    self.command_input = "/"
                elif self.entering_command:
                    if event.key == pygame.K_RETURN:
                        self.process_command(self.command_input)
                        self.entering_command = False
                        self.command_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.command_input = self.command_input[:-1]
                    else:
                        self.command_input += event.unicode

    def roll_dice(self):
        self.dice_roll = random.randint(1, 6)
        self.phase = "move"
        self.log_message = f"{self.players[self.current_player].name} rolled {self.dice_roll}!"

    def move_player(self):
        player = self.players[self.current_player]
        for _ in range(self.dice_roll):
            player.position = (player.position + 1) % len(self.tiles)
        effect_tile = self.tiles[player.position]
        self.log_message = effect_tile.trigger_effect(player)
        self.phase = "effect"
        self.buttons[0].visible = False
        self.buttons[1].visible = True

    def next_turn(self):
        self.phase = "roll"
        self.dice_roll = 0
        self.log_message = ""
        self.buttons[0].visible = True
        self.buttons[1].visible = False

    def process_command(self, command):
        player = self.players[self.current_player]
        if command == "/imagine":
            player.coins += 5
            self.log_message = "Imagined +5 coins!"
        elif command == "/testp":
            self.log_message = f"{player.name}: {player.coins} coins, {player.stars} stars"
        elif command == "/zeroshot":
            for i, tile in enumerate(self.tiles):
                if tile.type == "star":
                    player.position = i
                    self.log_message = "Moved to star space!"
                    break
        else:
            self.log_message = "Unknown command!"

    def draw(self):
        SCREEN.fill(WHITE)
        for tile in self.tiles:
            tile.draw()
        for player in self.players:
            player.draw()
        for btn in self.buttons:
            btn.draw()
        draw_text(self.log_message, BLACK, 50, HEIGHT - 50)
        p = self.players[self.current_player]
        draw_text(f"{p.name} | Coins: {p.coins} | Stars: {p.stars}", BLACK, 50, 20)
        if self.phase == "roll":
            draw_text("ROLL THE DICE!", RED, WIDTH // 2 - 50, 20)
        if self.entering_command:
            draw_text(self.command_input, BLACK, 50, HEIGHT - 80)
        pygame.display.update()

    async def run(self):
        while True:
            self.handle_events()
            self.draw()
            if self.phase == "move":
                self.move_player()
            await asyncio.sleep(1.0 / FPS)

async def main():
    game = MarioPartyGame()
    await game.run()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
