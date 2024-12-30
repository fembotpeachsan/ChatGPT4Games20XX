import pygame as pg
import sys
import math
import random
from enum import Enum, auto
from typing import Tuple

# Define game states
class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    GAME_OVER = auto()

# Define color palette
colors = {
    'WHITE': (255, 255, 255),
    'NEON_PINK': (255, 20, 147),
    'NEON_BLUE': (0, 191, 255),
    'BG_TOP': (15, 0, 30),
    'BG_BOTTOM': (30, 0, 60),
    'GRID': (50, 50, 50),
    'GAME_OVER': (255, 0, 0)  # Red color for Game Over text
}

# Define configuration settings
class Config:
    WIDTH = 800
    HEIGHT = 600
    FPS = 60
    PADDLE_WIDTH = 10
    PADDLE_HEIGHT = 100
    BALL_SIZE = 20
    PADDLE_SPEED = 7
    BALL_SPEED = 8
    WIN_SCORE = 5
    FONT_SIZE = 64

# Background class with animation
class Background:
    def __init__(self, config: Config):
        self.config = config
        self.surface = self._create_background()
        self.scroll_offset = 0
        self.scroll_speed = 1

    def _create_background(self) -> pg.Surface:
        """
        Create a gradient background that transitions from BG_TOP to BG_BOTTOM.
        """
        surface = pg.Surface((self.config.WIDTH, self.config.HEIGHT))
        for y in range(self.config.HEIGHT):
            ratio = y / self.config.HEIGHT
            color = tuple(
                int(colors['BG_TOP'][i] * (1 - ratio) + colors['BG_BOTTOM'][i] * ratio)
                for i in range(3)
            )
            pg.draw.line(surface, color, (0, y), (self.config.WIDTH, y))
        return surface

    def update(self):
        """
        Update the scrolling effect for the background grid lines.
        """
        self.scroll_offset = (self.scroll_offset + self.scroll_speed) % self.config.HEIGHT

    def draw(self, screen: pg.Surface):
        """
        Draw the gradient background and overlay scrolling grid lines.
        """
        screen.blit(self.surface, (0, 0))
        for y in range(0, self.config.HEIGHT, 40):
            grid_y = (y + self.scroll_offset) % self.config.HEIGHT
            pg.draw.line(screen, colors['GRID'], (0, grid_y), (self.config.WIDTH, grid_y))

# Ball class
class Ball:
    def __init__(self, config: Config):
        self.config = config
        self.rect = pg.Rect(
            config.WIDTH // 2 - config.BALL_SIZE // 2,
            config.HEIGHT // 2 - config.BALL_SIZE // 2,
            config.BALL_SIZE,
            config.BALL_SIZE
        )
        self.reset()

    def reset(self):
        """
        Place the ball at the center and launch it in a random direction.
        """
        self.rect.center = (self.config.WIDTH // 2, self.config.HEIGHT // 2)
        angle = random.uniform(-45, 45)  # Randomize angle between -45° and 45°
        direction = random.choice([-1, 1])  # Randomize horizontal direction
        self.speed_x = direction * self.config.BALL_SPEED * math.cos(math.radians(angle))
        self.speed_y = self.config.BALL_SPEED * math.sin(math.radians(angle))

    def update(self, paddles):
        """
        Move the ball and handle collisions with walls and paddles.
        """
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Bounce off top or bottom
        if self.rect.top <= 0 or self.rect.bottom >= self.config.HEIGHT:
            self.speed_y *= -1

        # Paddle collisions
        for paddle in paddles:
            if self.rect.colliderect(paddle.rect):
                hit_pos = (self.rect.centery - paddle.rect.centery) / (self.config.PADDLE_HEIGHT / 2)
                # Increase speed slightly and reverse direction
                self.speed_x *= -1.1
                self.speed_y += hit_pos * 2
                # Prevent ball from "sticking" inside the paddle
                if self.speed_x > 0:
                    self.rect.left = paddle.rect.right
                else:
                    self.rect.right = paddle.rect.left

    def draw(self, screen: pg.Surface):
        pg.draw.ellipse(screen, colors['WHITE'], self.rect)

# Paddle class with optional glow effect
class Paddle:
    def __init__(self, x: int, config: Config, color: Tuple[int, ...]):
        self.config = config
        self.color = color
        self.speed = config.PADDLE_SPEED
        self.rect = pg.Rect(
            x,
            config.HEIGHT // 2 - config.PADDLE_HEIGHT // 2,
            config.PADDLE_WIDTH,
            config.PADDLE_HEIGHT
        )
        self.glow_timer = 0

    def move(self, up: bool):
        """
        Move the paddle up or down, ensuring it stays in the screen.
        """
        self.rect.y += -self.speed if up else self.speed
        self.rect.y = max(0, min(self.config.HEIGHT - self.config.PADDLE_HEIGHT, self.rect.y))

    def trigger_glow(self):
        """
        Trigger a temporary glow effect on the paddle.
        """
        self.glow_timer = 10

    def update(self):
        if self.glow_timer > 0:
            self.glow_timer -= 1

    def draw(self, screen: pg.Surface):
        # Optional: Draw paddle glow
        if self.glow_timer > 0:
            glow_surface = pg.Surface((self.rect.width + 20, self.rect.height + 20), pg.SRCALPHA)
            pg.draw.ellipse(glow_surface, (*self.color, 100), glow_surface.get_rect())
            screen.blit(glow_surface, (self.rect.x - 10, self.rect.y - 10))
        # Draw the paddle rectangle
        pg.draw.rect(screen, self.color, self.rect)

# Main game class
class PongGame:
    def __init__(self):
        pg.init()
        self.config = Config()
        self.screen = pg.display.set_mode((self.config.WIDTH, self.config.HEIGHT))
        pg.display.set_caption("Synthwave Pong")
        self.clock = pg.time.Clock()
        self.font = pg.font.Font(None, self.config.FONT_SIZE)
        self.background = Background(self.config)
        self.reset_game()

    def reset_game(self):
        """
        Reset all variables to initial conditions.
        """
        self.state = GameState.MENU
        self.single_player = False
        self.score = [0, 0]
        self.ball = Ball(self.config)
        self.paddles = [
            Paddle(25, self.config, colors['NEON_PINK']),
            Paddle(self.config.WIDTH - 35, self.config, colors['NEON_BLUE'])
        ]

    def handle_events(self):
        """
        Handle all pygame events.
        Returns False if the window should close, True otherwise.
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            elif event.type == pg.KEYDOWN:
                # MENU state inputs
                if self.state == GameState.MENU:
                    if event.key == pg.K_1:
                        self.single_player = True
                        self.state = GameState.PLAYING
                    elif event.key == pg.K_2:
                        self.single_player = False
                        self.state = GameState.PLAYING

                # GAME_OVER state inputs
                elif self.state == GameState.GAME_OVER:
                    if event.key == pg.K_ESCAPE:
                        self.reset_game()

                # Other states
                else:
                    if event.key == pg.K_ESCAPE:
                        self.reset_game()
        return True

    def update(self):
        """
        Update game objects based on the current game state.
        """
        # MENU state: Display static or animate background
        if self.state == GameState.MENU:
            self.background.update()

        # PLAYING state
        elif self.state == GameState.PLAYING:
            self.background.update()
            self.ball.update(self.paddles)

            # Update paddles (including glow timers)
            for paddle in self.paddles:
                paddle.update()

            # Single-player AI
            if self.single_player:
                # Move AI paddle with a bit of buffer
                if self.ball.rect.centery > self.paddles[1].rect.centery + 20:
                    self.paddles[1].move(False)
                elif self.ball.rect.centery < self.paddles[1].rect.centery - 20:
                    self.paddles[1].move(True)

            # Multiplayer controls for right paddle if not single-player
            keys = pg.key.get_pressed()
            if keys[pg.K_w]:
                self.paddles[0].move(True)
            if keys[pg.K_s]:
                self.paddles[0].move(False)
            if not self.single_player:
                if keys[pg.K_UP]:
                    self.paddles[1].move(True)
                if keys[pg.K_DOWN]:
                    self.paddles[1].move(False)

            # Scoring logic
            if self.ball.rect.left <= 0:
                self.score[1] += 1
                self.ball.reset()
            elif self.ball.rect.right >= self.config.WIDTH:
                self.score[0] += 1
                self.ball.reset()

            # Check for Game Over
            if max(self.score) >= self.config.WIN_SCORE:
                self.state = GameState.GAME_OVER

        # GAME_OVER state: Wait for ESC to reset

    def draw_menu(self):
        """
        Draw the main menu screen.
        """
        self.background.draw(self.screen)
        title_text = self.font.render("Synthwave Pong", True, colors['WHITE'])
        single_text = self.font.render("Press 1 for Single-Player", True, colors['NEON_PINK'])
        multi_text = self.font.render("Press 2 for Multiplayer", True, colors['NEON_BLUE'])
        self.screen.blit(title_text, (self.config.WIDTH // 2 - title_text.get_width() // 2, 150))
        self.screen.blit(single_text, (self.config.WIDTH // 2 - single_text.get_width() // 2, 300))
        self.screen.blit(multi_text, (self.config.WIDTH // 2 - multi_text.get_width() // 2, 400))

    def draw_playing(self):
        """
        Draw the gameplay screen including background, ball, paddles, and score.
        """
        self.background.draw(self.screen)
        self.ball.draw(self.screen)
        for paddle in self.paddles:
            paddle.draw(self.screen)

        # Score display
        score_text = self.font.render(f"{self.score[0]} - {self.score[1]}", True, colors['WHITE'])
        self.screen.blit(score_text, (self.config.WIDTH // 2 - score_text.get_width() // 2, 20))

    def draw_game_over(self):
        """
        Display a Game Over screen with the winner and reset instructions.
        """
        self.background.draw(self.screen)
        winner = "Player 1" if self.score[0] > self.score[1] else ("Player 2" if not self.single_player else "AI")
        game_over_text = self.font.render(f"{winner} Wins!", True, colors['WHITE'])
        restart_text = self.font.render("Press ESC to Restart", True, colors['WHITE'])
        self.screen.blit(game_over_text, (self.config.WIDTH // 2 - game_over_text.get_width() // 2, 250))
        self.screen.blit(restart_text, (self.config.WIDTH // 2 - restart_text.get_width() // 2, 350))

    def draw(self):
        """
        Draw the correct screen depending on the game state.
        """
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_playing()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()

        pg.display.flip()

    def run(self):
        """
        Main game loop.
        """
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.config.FPS)
        pg.quit()
        sys.exit()

if __name__ == "__main__":
    PongGame().run()
