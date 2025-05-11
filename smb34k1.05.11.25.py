import asyncio
import platform
import pygame
import random

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SKY_BLUE = (135, 206, 235)
WHITE = (255, 255, 255)
FPS = 60

# Game States
class GameState:
    TITLE = 0
    OVERWORLD = 1
    LEVEL = 2
    LEVEL_COMPLETE = 3
    GAME_OVER = 4

# Entity Types
class EntityType:
    PLAYER = 0
    COIN = 1
    MUSHROOM = 2
    BLOCK = 3

# Player States
class PlayerState:
    ALIVE = 0
    DEAD = 1

class Entity:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.entity_type = None

    # MODIFIED LINE: Added keys=None and level=None to the signature
    def update(self, dt, keys=None, level=None):
        pass

    def draw(self, surface, camera_x):
        pass

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.entity_type = EntityType.PLAYER
        self.score = 0
        self.coins = 0
        self.state = PlayerState.ALIVE
        self.width = 32
        self.height = 32
        self.vel = pygame.Vector2(0, 0)
        self.speed = 200

    def update(self, dt, keys, level): # Player's update already expects these
        if self.state == PlayerState.DEAD:
            return
        self.vel.x = 0
        if keys[pygame.K_LEFT]:
            self.vel.x = -self.speed
        if keys[pygame.K_RIGHT]:
            self.vel.x = self.speed
        self.pos += self.vel * dt
        if self.pos.x < 0:
            self.pos.x = 0
        for entity in level.entities:
            if entity != self and self.collides_with(entity):
                self.on_collision(entity)

    def collides_with(self, other):
        rect1 = pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)
        # Assuming other entities also have a standard size or need individual handling
        # For now, using a common 32x32, but you might want 'other.width', 'other.height'
        other_width = getattr(other, 'width', 32)
        other_height = getattr(other, 'height', 32)
        rect2 = pygame.Rect(other.pos.x, other.pos.y, other_width, other_height)
        return rect1.colliderect(rect2)

    def on_collision(self, other):
        if other.entity_type == EntityType.COIN and other.active:
            other.collect()
            self.coins += 1
            self.score += 100
            if self.coins >= 100:
                self.coins -= 100
                # Assuming 'level.game.player_lives' is accessible
                # It would be better to pass 'game' to player or have a more robust way to access it
                if hasattr(self, 'level') and hasattr(self.level, 'game'):
                    self.level.game.player_lives += 1
        elif other.entity_type == EntityType.MUSHROOM and other.active:
            other.collect()
            if hasattr(self, 'level') and hasattr(self.level, 'game'):
                self.level.game.player_lives += 1

    def draw(self, surface, camera_x):
        if self.state == PlayerState.ALIVE:
            pygame.draw.rect(surface, (255, 0, 0), (self.pos.x - camera_x, self.pos.y, self.width, self.height))

class Coin(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.entity_type = EntityType.COIN
        self.active = True
        self.width = 32 # Assuming a size for collision
        self.height = 32

    def collect(self):
        self.active = False

    def draw(self, surface, camera_x):
        if self.active:
            # Draw circle centered
            pygame.draw.circle(surface, (255, 215, 0), (int(self.pos.x - camera_x + self.width/2), int(self.pos.y + self.height/2)), 16)

class OneUpMushroom(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.entity_type = EntityType.MUSHROOM
        self.active = True
        self.width = 32
        self.height = 32

    def collect(self):
        self.active = False

    def draw(self, surface, camera_x):
        if self.active:
            pygame.draw.rect(surface, (0, 255, 0), (self.pos.x - camera_x, self.pos.y, self.width, self.height))

class Block(Entity):
    def __init__(self, x, y, block_type, content):
        super().__init__(x, y)
        self.entity_type = EntityType.BLOCK
        self.block_type = block_type
        self.content = content
        self.width = 32
        self.height = 32

    def draw(self, surface, camera_x):
        pygame.draw.rect(surface, (139, 69, 19), (self.pos.x - camera_x, self.pos.y, self.width, self.height))

class Level:
    def __init__(self, game, level_type, world_index, level_index):
        self.game = game
        self.level_type = level_type
        self.world_index = world_index
        self.level_index = level_index
        self.entities = []
        self.player = None
        self.bg_color = SKY_BLUE
        self.time_left = 300
        self.timer = 0
        self.complete = False
        self.camera_x = 0
        self.level_width = SCREEN_WIDTH * 3
        self.generate_regular_level()

    def generate_regular_level(self):
        ground_y = SCREEN_HEIGHT - 64
        self.player = Player(100, ground_y - 32) # Player height is 32
        self.player.level = self # Assign level to player for context
        self.entities.append(self.player)
        
        # Add a coin, ensuring its y-position accounts for its height if needed for collision
        self.entities.append(Coin(200, ground_y - 32)) # Coin is 32x32, place on ground

        blocks_data = [
            # x, y_of_block_top, type, content
            (1920, ground_y - 280, "question", "1up"),
            (2000, ground_y - 280, "question", "coin"),
        ]
        for block_x, block_y, block_type, content in blocks_data:
            self.entities.append(Block(block_x, block_y, block_type, content))
            if content == "1up":
                # Spawn mushroom above the block, assuming mushroom is 32 high
                self.entities.append(OneUpMushroom(block_x, block_y - 32))
            # You might want to handle 'coin' content similarly if it spawns a coin item

    def update(self, dt, keys):
        self.timer += dt
        if self.timer >= 1:
            self.time_left -= 1
            self.timer = 0
        
        # Update all entities
        # Pass 'keys' and 'self' (for level context) to each entity's update method
        for entity in list(self.entities): # Iterate over a copy if entities can be removed during update
            entity.update(dt, keys, self)

        if self.player.pos.x > self.level_width - 150: # Check for level completion
            self.complete = True
        
        # Camera logic
        # Ensure camera doesn't go left of level start or right of level end
        # Player's drawn position is self.player.pos.x, camera should center player
        target_camera_x = self.player.pos.x - SCREEN_WIDTH // 2
        self.camera_x = max(0, min(target_camera_x, self.level_width - SCREEN_WIDTH))


    def draw(self, surface):
        surface.fill(self.bg_color)
        for entity in self.entities:
            entity.draw(surface, self.camera_x)
        self.draw_hud(surface)

    def draw_hud(self, surface):
        font = pygame.font.Font(None, 36) # Use default font
        score_text = font.render(f"Score: {self.player.score}", True, WHITE)
        surface.blit(score_text, (10, 10))
        coins_text = font.render(f"Coins: {self.player.coins}", True, WHITE)
        surface.blit(coins_text, (10, 50))
        lives_text = font.render(f"Lives: {self.game.player_lives}", True, WHITE)
        surface.blit(lives_text, (10, 90))
        time_text = font.render(f"Time: {self.time_left}", True, WHITE)
        surface.blit(time_text, (SCREEN_WIDTH - 150, 10))

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Delta4k Game") # Added a caption
        self.clock = pygame.time.Clock()
        self.state = GameState.LEVEL # Start directly in a level for now
        self.player_lives = 3
        # Initialize current_level
        self.current_level = Level(self, "regular", 0, 0)

    def handle_level(self, dt, keys):
        self.current_level.update(dt, keys)
        self.current_level.draw(self.screen)

        if self.current_level.complete:
            self.state = GameState.LEVEL_COMPLETE
            print("Level Complete!") # Placeholder for next state
            # Potentially load next level or go to a complete screen
            # For now, let's just re-create the level to restart
            self.current_level = Level(self, "regular", 0, 0) # Restart/Next level placeholder


        elif self.current_level.player.state == PlayerState.DEAD:
            self.player_lives -= 1
            if self.player_lives <= 0:
                self.state = GameState.GAME_OVER
                print("Game Over!") # Placeholder
                # For now, reset lives and level
                self.player_lives = 3
                self.current_level = Level(self, "regular", 0, 0)

            else:
                # Player died but has lives left, reset current level
                print(f"Player died. Lives remaining: {self.player_lives}")
                world_index = self.current_level.world_index
                level_index = self.current_level.level_index
                level_type = self.current_level.level_type
                self.current_level = Level(self, level_type, world_index, level_index)


    def run(self, dt, keys):
        if self.state == GameState.LEVEL:
            self.handle_level(dt, keys)
        elif self.state == GameState.LEVEL_COMPLETE:
            # Simple "Level Complete" screen or logic
            font = pygame.font.Font(None, 74)
            text = font.render("Level Complete!", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            self.screen.blit(text, text_rect)
            # Add logic to proceed or restart (e.g., press key to continue)
            # For now, it will just show this screen then potentially restart via handle_level if state changes back
        elif self.state == GameState.GAME_OVER:
            # Simple "Game Over" screen
            font = pygame.font.Font(None, 74)
            text = font.render("Game Over", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            self.screen.blit(text, text_rect)
            # Add logic to restart (e.g., press key to play again)

        pygame.display.flip()

# Global game instance
game = None

def setup():
    global game
    game = Game()

async def main():
    setup()
    running = True
    while running:
        dt = game.clock.tick(FPS) / 1000.0
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        if not running: # Exit loop if running is false
            break

        game.run(dt, keys)
        await asyncio.sleep(0) # Yield control to the event loop

    pygame.quit()

if __name__ == "__main__":
    if platform.system() == "Emscripten":
        asyncio.ensure_future(main())
    else:
        asyncio.run(main())
