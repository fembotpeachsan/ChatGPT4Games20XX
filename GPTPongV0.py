import pygame
import sys
import numpy

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
screen = pygame.display.set_mode((640, 480))
pygame.font.init()  # Initialize font module

# Global Variables
BLACK, WHITE = (0, 0, 0), (255, 255, 255)
FONT = pygame.font.Font(None, 36)

def draw_button(text, center_x, center_y, action=None):
    text_surf = FONT.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=(center_x, center_y))
    screen.blit(text_surf, text_rect)
    return text_rect

def main_menu():
    menu_active = True
    while menu_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_btn.collidepoint(event.pos):
                    main_game()
                elif exit_btn.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        screen.fill(BLACK)
        start_btn = draw_button("Start Game", 320, 200)
        exit_btn = draw_button("Exit", 320, 260)
        pygame.display.flip()

def generate_tone(frequency, volume, sample_rate=22050, duration=0.1):
    t = numpy.linspace(0, duration, int(sample_rate * duration), False)
    tone = numpy.sin(frequency * t * 2 * numpy.pi)
    stereo_tone = numpy.vstack((tone, tone)).T
    return pygame.sndarray.make_sound((32767 * volume * stereo_tone).astype(numpy.int16).copy(order='C'))

def main_game():
    clock = pygame.time.Clock()
    running = True
    paddle_width, paddle_height, paddle_speed = 10, 100, 10
    ball_width, ball_height, ball_speed_x, ball_speed_y = 10, 10, 5, 5
    score1, score2 = 0, 0
    
    paddle1 = pygame.Rect(20, 200, paddle_width, paddle_height)
    paddle2 = pygame.Rect(610, 200, paddle_width, paddle_height)
    ball_rect = pygame.Rect(315, 235, ball_width, ball_height)
    
    paddle_hit_tone = generate_tone(440, 0.5)
    wall_hit_tone = generate_tone(880, 0.5)
    score_tone = generate_tone(1760, 0.5)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            paddle1.y -= paddle_speed
        if keys[pygame.K_s]:
            paddle1.y += paddle_speed
        if paddle2.centery < ball_rect.centery:
            paddle2.y += paddle_speed
        if paddle2.centery > ball_rect.centery:
            paddle2.y -= paddle_speed
        
        ball_rect.x += ball_speed_x
        ball_rect.y += ball_speed_y
        
        if ball_rect.top <= 0 or ball_rect.bottom >= 480:
            ball_speed_y = -ball_speed_y
            wall_hit_tone.play()
        if ball_rect.colliderect(paddle1) or ball_rect.colliderect(paddle2):
            ball_speed_x = -ball_speed_x
            paddle_hit_tone.play()
        
        if ball_rect.right >= 640:
            score1 += 1
            ball_rect.center = (320, 240)
            ball_speed_x = -ball_speed_x
            score_tone.play()
        if ball_rect.left <= 0:
            score2 += 1
            ball_rect.center = (320, 240)
            ball_speed_x = -ball_speed_x
            score_tone.play()
        
        screen.fill(BLACK)
        pygame.draw.rect(screen, WHITE, paddle1)
        pygame.draw.rect(screen, WHITE, paddle2)
        pygame.draw.ellipse(screen, WHITE, ball_rect)
        
        pygame.display.flip()
        clock.tick(60)
    main_menu()

if __name__ == "__main__":
    main_menu()
