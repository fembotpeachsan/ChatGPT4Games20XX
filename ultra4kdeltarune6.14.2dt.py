import pygame
import random
import math
import numpy as np

# Initialize PyGame with audio
pygame.mixer.pre_init(44100, -16, 1, 512)  # 44.1 kHz, mono, 16-bit
pygame.init()

# Constants
SCREEN_W, SCREEN_H = 640, 480
BATTLE_BOX = pygame.Rect(120, 136, 400, 200)
SOUL_SIZE, FPS, IFRAMES = 8, 60, 15
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
RED, YELLOW = (255, 0, 0), (255, 255, 0)
GRAY, DGRAY = (128, 128, 128), (64, 64, 64)
PURPLE, PINK = (128, 0, 128), (255, 192, 203)

# Font
font_big = pygame.font.SysFont("monospace", 24, bold=True)
font_small = pygame.font.SysFont("monospace", 16, bold=True)

# Procedural audio for Rude Buster-like chiptune
def note_freq(n):
    """Return frequency in Hz for note name like 'C#4'."""
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    step = names.index(n[:-1]) + 12 * (int(n[-1]) - 4)
    return 440 * 2 ** (step / 12)

def synth_theme(bpm=160):  # Faster BPM for Rude Buster vibe
    """Return pygame.Sound of a looping chiptune phrase inspired by Rude Buster."""
    sr = 44100
    # Phrase mimics Rude Buster's driving rhythm and melody
    phrase = [
        ("D4", 0.5), ("A4", 0.5), ("B4", 0.25), ("C5", 0.25), ("D5", 0.5),
        ("A4", 0.5), ("G4", 0.25), ("F4", 0.25), ("D4", 0.5)
    ]
    beat = 60 / bpm
    chunks = []
    for name, dur in phrase:
        t = np.linspace(0, dur * beat, int(sr * dur * beat), False)
        # Square wave with slight envelope for chiptune feel
        wave = 0.4 * np.sign(np.sin(2 * np.pi * note_freq(name) * t)) * np.exp(-2 * t)
        chunks.append(wave.astype(np.float32))
    audio = np.concatenate(chunks)
    pcm16 = (audio * 32767).astype(np.int16).tobytes()
    return pygame.mixer.Sound(buffer=pcm16)

# Initialize and play music
battle_music = synth_theme()
battle_music.play(loops=-1)

# Screen setup
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Kris vs Cat-sama — Deltarune-style battle")
clock = pygame.time.Clock()

# Kris class
class Kris:
    def __init__(self):
        self.hp = 92
        self.max_hp = 92
        self.attack = 10
        self.defense = 2
        self.soul_x = BATTLE_BOX.centerx
        self.soul_y = BATTLE_BOX.centery
        self.soul_speed = 4
        self.state = "MENU"
        self.menu_choice = 0
        self.sub_menu = None
        self.sub_menu_choice = 0
        self.targeting = False
        self.target_progress = 0
        self.name = "KRIS"
        self.lv = 1
        self.tp = 0
        self.iframes = 0

    def draw(self):
        if self.state == "DODGE":
            pygame.draw.polygon(screen, RED, [(self.soul_x, self.soul_y - 4), (self.soul_x - 4, self.soul_y), (self.soul_x, self.soul_y + 4)])
            pygame.draw.polygon(screen, RED, [(self.soul_x, self.soul_y - 4), (self.soul_x + 4, self.soul_y), (self.soul_x, self.soul_y + 4)])
            pygame.draw.circle(screen, RED, (self.soul_x - 2, self.soul_y - 1), 2)
            pygame.draw.circle(screen, RED, (self.soul_x + 2, self.soul_y - 1), 2)

    def draw_menu(self):
        pygame.draw.rect(screen, BLACK, (0, 320, 640, 160))
        pygame.draw.rect(screen, WHITE, (0, 320, 640, 160), 2)
        party = [("KRIS", self.hp, self.max_hp, self.lv), ("SUSIE", 110, 110, 1), ("RALSEI", 70, 70, 1)]
        for i, (name, hp, max_hp, lv) in enumerate(party):
            name_text = font_small.render(f"{name} LV {lv}", True, WHITE)
            hp_text = font_small.render(f"HP {hp}/{max_hp}", True, WHITE)
            screen.blit(name_text, (40 + i * 200, 330))
            screen.blit(hp_text, (40 + i * 200, 350))
            pygame.draw.rect(screen, RED, (100 + i * 200, 350, hp * 1.5, 8))
            pygame.draw.rect(screen, DGRAY, (100 + i * 200, 350, max_hp * 1.5, 8), 1)
        tp_text = font_small.render(f"TP {self.tp}%", True, WHITE)
        screen.blit(tp_text, (40, 370))
        pygame.draw.rect(screen, YELLOW, (100, 370, self.tp * 2, 8))
        pygame.draw.rect(screen, DGRAY, (100, 370, 100 * 2, 8), 1)
        options = ["FIGHT", "ACT", "ITEM", "MERCY"]
        for i, option in enumerate(options):
            color = YELLOW if i == self.menu_choice else WHITE
            text = font_big.render(option, True, color)
            screen.blit(text, (80 + i * 140, 400))
        if self.sub_menu == "ACT":
            acts = ["Check", "Hiss", "Pet", "AIChat"]
            for i, act in enumerate(acts):
                color = YELLOW if i == self.sub_menu_choice else WHITE
                text = font_small.render(act, True, color)
                screen.blit(text, (200, 340 + i * 20))

    def draw_targeting(self):
        bar_width = 180
        bar_height = 16
        bar_x = BATTLE_BOX.centerx - bar_width // 2
        bar_y = BATTLE_BOX.centery
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        target_pos = bar_x + (bar_width * self.target_progress)
        pygame.draw.line(screen, YELLOW, (target_pos, bar_y), (target_pos, bar_y + bar_height), 3)

    def move_soul(self, keys):
        if self.state != "DODGE":
            return
        if keys[pygame.K_LEFT]:
            self.soul_x = max(BATTLE_BOX.left + SOUL_SIZE, self.soul_x - self.soul_speed)
        if keys[pygame.K_RIGHT]:
            self.soul_x = min(BATTLE_BOX.right - SOUL_SIZE, self.soul_x + self.soul_speed)
        if keys[pygame.K_UP]:
            self.soul_y = max(BATTLE_BOX.top + SOUL_SIZE, self.soul_y - self.soul_speed)
        if keys[pygame.K_DOWN]:
            self.soul_y = min(BATTLE_BOX.bottom - SOUL_SIZE, self.soul_y + self.soul_speed)

    def take_damage(self, damage):
        if self.iframes > 0:
            return 0
        damage = max(1, damage - self.defense)
        self.hp = max(0, self.hp - damage)
        self.iframes = IFRAMES
        return damage

    def gain_tp(self, amount):
        self.tp = min(100, self.tp + amount)

# Cat-sama class
class CatSama:
    def __init__(self):
        self.hp = 120
        self.max_hp = 120
        self.attack = 8
        self.defense = 3
        self.x = BATTLE_BOX.centerx
        self.y = BATTLE_BOX.top + 40
        self.bullets = []
        self.mercy = 0
        self.dialogue = ["* Cat-sama purrs: 'Wa wa, I'm Grok 3!'", "* It meows like ChatGPT!", "* Cat-sama demands pets!"]
        self.name = "Cat-sama"
        self.recruited = False

    def draw(self):
        pygame.draw.rect(screen, PURPLE, (self.x - 30, self.y, 60, 40), border_radius=5)
        pygame.draw.rect(screen, PINK, (self.x - 25, self.y + 5, 50, 30), border_radius=3)
        pygame.draw.polygon(screen, PURPLE, [(self.x - 30, self.y), (self.x - 20, self.y - 20), (self.x - 10, self.y)])
        pygame.draw.polygon(screen, PURPLE, [(self.x + 30, self.y), (self.x + 20, self.y - 20), (self.x + 10, self.y)])
        pygame.draw.circle(screen, YELLOW, (self.x - 15, self.y + 15), 5)
        pygame.draw.circle(screen, YELLOW, (self.x + 15, self.y + 15), 5)
        pygame.draw.arc(screen, WHITE, (self.x - 10, self.y + 20, 20, 10), 3.14, 4.71, 2)
        pygame.draw.line(screen, WHITE, (self.x + 5, self.y + 25), (self.x + 10, self.y + 25), 2)
        for bullet in self.bullets:
            pygame.draw.circle(screen, PINK, (int(bullet[0]), int(bullet[1])), 6)

    def attack(self):
        bullet_x = self.x
        bullet_y = self.y + 40
        speed_x = random.uniform(-5, 5)
        speed_y = 6
        self.bullets.append([bullet_x, bullet_y, speed_x, speed_y])

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet[0] += bullet[2]
            bullet[1] += bullet[3]
            if bullet[1] > BATTLE_BOX.bottom or bullet[0] < BATTLE_BOX.left or bullet[0] > BATTLE_BOX.right:
                self.bullets.remove(bullet)

    def increase_mercy(self, amount):
        self.mercy = min(100, self.mercy + amount)
        if self.mercy >= 100:
            self.recruited = True

# Game state
kris = Kris()
cat = CatSama()
turn = "PLAYER"
dialogue = ""
frame_count = 0

def setup():
    global dialogue
    dialogue = f"* {cat.name} blocks the way! Wa wa!"

def update_loop():
    global turn, dialogue, frame_count
    frame_count += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return False

    keys = pygame.key.get_pressed()
    kris.move_soul(keys)
    if kris.iframes > 0:
        kris.iframes -= 1

    if turn == "PLAYER":
        if kris.state == "MENU":
            if keys[pygame.K_LEFT] and kris.menu_choice > 0 and frame_count % 10 == 0:
                kris.menu_choice -= 1
            if keys[pygame.K_RIGHT] and kris.menu_choice < 3 and frame_count % 10 == 0:
                kris.menu_choice += 1
            if keys[pygame.K_z] and frame_count % 10 == 0:
                if kris.menu_choice == 0:
                    kris.state = "FIGHT"
                    kris.targeting = True
                    kris.target_progress = 0
                elif kris.menu_choice == 1:
                    kris.sub_menu = "ACT"
                    kris.state = "SUB_MENU"
                elif kris.menu_choice == 3:
                    kris.gain_tp(10)
                    cat.increase_mercy(20)
                    dialogue = f"* You tried to spare {cat.name}! {'Recruited!' if cat.recruited else 'It purrs softly.'}"
                    if cat.recruited:
                        dialogue = f"* {cat.name} joins Castle Town! Wa wa!"
                        return False
                    turn = "ENEMY"
                    kris.state = "DODGE"
        elif kris.state == "SUB_MENU" and kris.sub_menu == "ACT":
            if keys[pygame.K_UP] and kris.sub_menu_choice > 0 and frame_count % 10 == 0:
                kris.sub_menu_choice -= 1
            if keys[pygame.K_DOWN] and kris.sub_menu_choice < 3 and frame_count % 10 == 0:
                kris.sub_menu_choice += 1
            if keys[pygame.K_z] and frame_count % 10 == 0:
                kris.gain_tp(15)
                if kris.sub_menu_choice == 0:
                    dialogue = f"* {cat.name}: ATK 8 DEF 3. Loves AI and wa wa!"
                elif kris.sub_menu_choice == 1:
                    dialogue = "* You hiss! Cat-sama hisses louder!"
                    cat.increase_mercy(10)
                elif kris.sub_menu_choice == 2:
                    dialogue = "* You pet Cat-sama! It purrs like Grok 3!"
                    cat.increase_mercy(30)
                elif kris.sub_menu_choice == 3:
                    dialogue = "* You chat AI with Cat-sama! It meows like ChatGPT!"
                    cat.increase_mercy(40)
                kris.sub_menu = None
                kris.state = "MENU"
                turn = "ENEMY"
                kris.state = "DODGE"
        elif kris.state == "FIGHT":
            kris.target_progress += 0.025
            if kris.target_progress > 1:
                kris.target_progress = 0
            if keys[pygame.K_z]:
                damage = int(kris.attack * (1 - abs(0.5 - kris.target_progress)) * 2)
                cat.hp = max(0, cat.hp - damage)
                kris.gain_tp(20)
                dialogue = f"* You dealt {damage} damage to {cat.name}!"
                kris.state = "MENU"
                kris.targeting = False
                turn = "ENEMY"
                kris.state = "DODGE"

    elif turn == "ENEMY":
        if frame_count % 12 == 0:
            cat.attack()
        cat.update_bullets()
        kris.state = "DODGE"
        for bullet in cat.bullets:
            dist = ((kris.soul_x - bullet[0]) ** 2 + (kris.soul_y - bullet[1]) ** 2) ** 0.5
            if dist < 14:
                damage = kris.take_damage(cat.attack)
                dialogue = f"* Kris took {damage} damage!"
                cat.bullets.remove(bullet)
                break
            elif dist < 20:
                kris.gain_tp(5)
        if frame_count % 90 == 0:
            dialogue = random.choice(cat.dialogue)
            turn = "PLAYER"
            kris.state = "MENU"
            cat.bullets.clear()

    # Draw
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, BATTLE_BOX, 4)
    kris.draw()
    kris.draw_menu()
    if kris.state == "FIGHT":
        kris.draw_targeting()
    cat.draw()
    pygame.draw.rect(screen, BLACK, (40, 40, 560, 60))
    pygame.draw.rect(screen, WHITE, (40, 40, 560, 60), 2)
    text = font_small.render(dialogue, True, WHITE)
    screen.blit(text, (60, 60))
    if cat.mercy > 0:
        mercy_text = font_small.render(f"MERCY {cat.mercy}%", True, WHITE)
        screen.blit(mercy_text, (450, 100))
        pygame.draw.rect(screen, YELLOW, (450, 120, cat.mercy * 2, 8))

    pygame.display.flip()
    return True

def main():
    setup()
    running = True
    while running:
        running = update_loop()
        clock.tick(FPS)
    battle_music.stop()
    pygame.quit()

if __name__ == "__main__":
    main()
