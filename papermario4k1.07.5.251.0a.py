#!/usr/bin/env python3
# test.py - Paper Mario: TTYD Battle Engine with Mario and Chain Chomp
# (c) 2025 Team SpecialEmu AGI Division
# TTYD battle system with procedural music and Sticker Star vibes

import pygame, math, array, random, sys, time
pygame.init(); pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# ─────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────
WW, WH = 800, 600
FPS = 60
WHITE = (255, 255, 255); BLACK = (0, 0, 0)
PURPLE = (138, 43, 226); GOLD = (255, 215, 0)
RED = (255, 0, 0); GREEN = (0, 255, 0); BLUE = (0, 0, 255)
STAGE_BROWN = (101, 67, 33); CURTAIN_RED = (139, 0, 0)
GRAY = (100, 100, 100); SKIN = (255, 200, 150)

# TTYD Stats
MARIO_MAX_HP, MARIO_MAX_FP = 30, 30
PARTNER_HP = {"Goomba": 20}
ENEMY_HP = {"Chain Chomp": 20}

# Star Power levels
MAX_STAR_POWER = 800  # 8 full stars
STAR_POWER_PER_BAR = 100

# ─────────────────────────────────────────────────────────────────
# INIT
# ─────────────────────────────────────────────────────────────────
screen = pygame.display.set_mode((WW, WH))
pygame.display.set_caption("Paper Mario: TTYD - Chain Chomp Battle")
clock = pygame.time.Clock()
font_damage = pygame.font.Font(None, 48)
font_ui = pygame.font.Font(None, 24)
font_small = pygame.font.Font(None, 18)

# ─────────────────────────────────────────────────────────────────
# TTYD BATTLE THEME GENERATOR
# ─────────────────────────────────────────────────────────────────
def generate_waveform(freq, duration_ms, sample_rate=44100, wave_type="square", volume=0.5):
    """Generate basic waveforms for synthesis"""
    n_samples = int(sample_rate * duration_ms / 1000)
    samples = array.array('h')
    
    for i in range(n_samples):
        t = i / sample_rate
        if wave_type == "square":
            val = volume if math.sin(2 * math.pi * freq * t) > 0 else -volume
        elif wave_type == "triangle":
            val = 2 * abs(2 * (t * freq % 1) - 1) - 1
            val *= volume
        elif wave_type == "sawtooth":
            val = 2 * (t * freq % 1) - 1
            val *= volume
        else:  # sine
            val = volume * math.sin(2 * math.pi * freq * t)
        
        samples.append(int(val * 32767))
    
    return samples

def create_ttyd_battle_theme():
    """Generate TTYD battle theme using pure synthesis"""
    notes = {
        'C3': 130.81, 'D3': 146.83, 'E3': 164.81, 'F3': 174.61, 'G3': 196.00, 'A3': 220.00, 'B3': 246.94,
        'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23, 'G4': 392.00, 'A4': 440.00, 'B4': 493.88,
        'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46, 'G5': 783.99, 'A5': 880.00, 'B5': 987.77,
    }
    
    bpm = 140
    beat_ms = 60000 / bpm
    
    melody_pattern = [
        (None, 0.25), (None, 0.25), (None, 0.25), (None, 0.25),
        ('E4', 0.25), ('E4', 0.25), ('F4', 0.25), ('G4', 0.25),
        ('C5', 0.5), ('B4', 0.25), ('A4', 0.25),
        ('G4', 0.5), ('F4', 0.25), ('E4', 0.25),
        ('D4', 0.5), ('C4', 0.5),
        ('G4', 0.25), ('G4', 0.25), ('A4', 0.25), ('B4', 0.25),
        ('C5', 0.5), ('D5', 0.5),
        ('E5', 0.5), ('D5', 0.25), ('C5', 0.25),
        ('B4', 0.5), ('A4', 0.5),
        ('E4', 0.125), ('E4', 0.125), ('E4', 0.25), ('F4', 0.25), ('G4', 0.25),
        ('A4', 0.5), ('G4', 0.25), ('F4', 0.25),
        ('E4', 0.5), ('D4', 0.25), ('C4', 0.25),
        ('D4', 0.25), ('E4', 0.25), ('F4', 0.25), ('G4', 0.25),
    ]
    
    bass_pattern = [
        ('C3', 1.0), ('G3', 1.0), ('A3', 1.0), ('F3', 1.0),
        ('C3', 1.0), ('G3', 1.0), ('A3', 0.5), ('B3', 0.5), ('C4', 1.0),
    ]
    
    melody_samples = array.array('h')
    for note, duration in melody_pattern:
        if note:
            freq = notes.get(note, 440)
            wave = generate_waveform(freq, int(beat_ms * duration), wave_type="square", volume=0.3)
            melody_samples.extend(wave)
        else:
            silence = array.array('h', [0] * int(44100 * beat_ms * duration / 1000))
            melody_samples.extend(silence)
    
    bass_samples = array.array('h')
    for _ in range(len(melody_samples) // (len(bass_pattern) * int(beat_ms * 44.1))):
        for note, duration in bass_pattern:
            freq = notes.get(note, 130)
            wave = generate_waveform(freq, int(beat_ms * duration), wave_type="sawtooth", volume=0.2)
            bass_samples.extend(wave)
    
    while len(bass_samples) < len(melody_samples):
        bass_samples.append(0)
    
    drum_samples = array.array('h')
    kick_freq, snare_freq = 60, 200
    for i in range(0, len(melody_samples), int(beat_ms * 44.1 / 2)):
        if i % (int(beat_ms * 44.1)) == 0:
            kick = generate_waveform(kick_freq, 50, wave_type="sine", volume=0.5)
            for j, sample in enumerate(kick):
                if i + j < len(melody_samples):
                    drum_samples.append(sample)
        elif i % (int(beat_ms * 44.1)) == int(beat_ms * 44.1 / 2):
            for j in range(int(44.1 * 30)):
                if i + j < len(melody_samples):
                    drum_samples.append(int(random.uniform(-0.3, 0.3) * 32767))
        else:
            drum_samples.append(0)
    
    final_samples = array.array('h')
    for i in range(len(melody_samples)):
        melody = melody_samples[i] if i < len(melody_samples) else 0
        bass = bass_samples[i] if i < len(bass_samples) else 0
        drum = drum_samples[i] if i < len(drum_samples) else 0
        
        mixed = int((melody * 0.5 + bass * 0.3 + drum * 0.2) * 0.7)
        mixed = max(-32767, min(32767, mixed))
        final_samples.append(mixed)
    
    stereo_samples = array.array('h')
    for sample in final_samples:
        stereo_samples.append(sample)
        stereo_samples.append(sample)
    
    return pygame.mixer.Sound(buffer=stereo_samples)

battle_theme = create_ttyd_battle_theme()
battle_theme.play(loops=-1)

# ─────────────────────────────────────────────────────────────────
# SOUND EFFECTS
# ─────────────────────────────────────────────────────────────────
def create_sfx(name):
    """Create TTYD-style sound effects"""
    if name == "menu_move":
        return pygame.mixer.Sound(buffer=generate_waveform(880, 30, wave_type="square", volume=0.3))
    elif name == "menu_select":
        return pygame.mixer.Sound(buffer=generate_waveform(1320, 50, wave_type="square", volume=0.4))
    elif name == "jump":
        samples = generate_waveform(440, 50, wave_type="sine", volume=0.5)
        samples.extend(generate_waveform(880, 100, wave_type="sine", volume=0.4))
        return pygame.mixer.Sound(buffer=samples)
    elif name == "hammer":
        return pygame.mixer.Sound(buffer=generate_waveform(220, 150, wave_type="sawtooth", volume=0.6))
    elif name == "excellent":
        samples = generate_waveform(523, 100, wave_type="sine", volume=0.5)
        samples.extend(generate_waveform(659, 100, wave_type="sine", volume=0.5))
        samples.extend(generate_waveform(784, 150, wave_type="sine", volume=0.5))
        return pygame.mixer.Sound(buffer=samples)
    elif name == "damage":
        return pygame.mixer.Sound(buffer=generate_waveform(150, 200, wave_type="sawtooth", volume=0.5))
    elif name == "star_power":
        samples = array.array('h')
        for i in range(10):
            freq = 440 + i * 100
            samples.extend(generate_waveform(freq, 50, wave_type="sine", volume=0.3))
        return pygame.mixer.Sound(buffer=samples)
    elif name == "audience_cheer":
        noise = array.array('h')
        for _ in range(int(44100 * 0.5)):
            noise.append(int(random.uniform(-0.1, 0.1) * 32767))
        return pygame.mixer.Sound(buffer=noise)

sfx = {
    'menu_move': create_sfx('menu_move'),
    'menu_select': create_sfx('menu_select'),
    'jump': create_sfx('jump'),
    'hammer': create_sfx('hammer'),
    'excellent': create_sfx('excellent'),
    'damage': create_sfx('damage'),
    'star_power': create_sfx('star_power'),
    'audience_cheer': create_sfx('audience_cheer')
}

# ─────────────────────────────────────────────────────────────────
# CLASSES
# ─────────────────────────────────────────────────────────────────
class ActionCommand:
    """TTYD-style action commands"""
    def __init__(self, cmd_type):
        self.type = cmd_type
        self.active = False
        self.timer = 0
        self.success = False
        self.perfect = False
        self.window_start = 0
        self.window_end = 0
        if self.type == "jump":
            self.window_start = 30
            self.window_end = 45
        elif self.type == "hammer":
            self.window_start = 40
            self.window_end = 55
        elif self.type == "superguard":
            self.window_start = 0
            self.window_end = 5
        elif self.type == "defense":
            self.guard_start = 20
            self.guard_end = 30
            self.superguard_start = 25
            self.superguard_end = 27
            
    def start(self):
        self.active = True
        self.timer = 0
        self.success = False
        self.perfect = False
        
    def update(self):
        if self.active:
            self.timer += 1
            
    def check_input(self, perfect_only=False):
        if not self.active:
            return False
        if perfect_only:
            if 0 <= self.timer <= 3:
                self.perfect = True
                self.success = True
                self.active = False
                return True
        else:
            if self.window_start <= self.timer <= self.window_end:
                if self.timer <= self.window_start + 5:
                    self.perfect = True
                self.success = True
                self.active = False
                return True
        return False
    
    def check_guard(self):
        if self.active and self.type == "defense" and self.guard_start <= self.timer <= self.guard_end:
            return True
        return False
    
    def check_superguard(self):
        if self.active and self.type == "defense" and self.superguard_start <= self.timer <= self.superguard_end:
            return True
        return False

class Audience:
    """TTYD audience system"""
    def __init__(self):
        self.members = []
        self.max_size = 200
        self.excitement = 50
        self.spawn_audience()
        
    def spawn_audience(self):
        audience_types = ['toad', 'koopa', 'goomba', 'boo', 'shy_guy']
        for i in range(self.max_size):
            row = i // 50
            col = i % 50
            x = 50 + col * 14
            y = 450 + row * 20
            member = {
                'type': random.choice(audience_types),
                'x': x + random.randint(-3, 3),
                'y': y + random.randint(-3, 3),
                'animation': random.uniform(0, 2*math.pi)
            }
            self.members.append(member)
            
    def update(self, dt):
        for member in self.members:
            member['animation'] += dt * 3
            
    def react(self, event_type):
        if event_type == "excellent":
            self.excitement = min(100, self.excitement + 10)
            sfx['audience_cheer'].play()
        elif event_type == "miss":
            self.excitement = max(0, self.excitement - 5)
            
    def throw_items(self):
        if random.random() < self.excitement / 100 * 0.1:
            return random.choice(['mushroom', 'flower', 'star_piece'])
        return None

class StageHazard:
    """TTYD stage hazards"""
    def __init__(self):
        self.active_hazards = []
        self.hazard_timer = 0
        
    def update(self, dt):
        self.hazard_timer += dt
        if self.hazard_timer > 10 and random.random() < 0.01:
            self.spawn_hazard()
            self.hazard_timer = 0
        for hazard in self.active_hazards[:]:
            hazard['timer'] -= dt
            if hazard['timer'] <= 0:
                self.active_hazards.remove(hazard)
                
    def spawn_hazard(self):
        hazard_types = ['fog', 'spotlight', 'falling_object', 'stage_tilt']
        hazard_type = random.choice(hazard_types)
        if hazard_type == 'falling_object':
            self.active_hazards.append({
                'type': 'falling_object',
                'x': random.randint(100, 700),
                'y': 0,
                'timer': 3.0
            })

class BattleMenu:
    """TTYD battle menu system"""
    def __init__(self):
        self.state = "main"
        self.selected = 0
        self.main_options = ["Attack", "Tactics", "Items", "Special", "Run"]
        self.attack_options = ["Jump", "Hammer"]
        self.special_moves = ["Sweet Treat", "Earth Tremor", "Clock Out", "Power Lift"]
        
    def move_cursor(self, direction):
        sfx['menu_move'].play()
        if self.state == "main":
            self.selected = (self.selected + direction) % len(self.main_options)
        elif self.state == "attack":
            self.selected = (self.selected + direction) % len(self.attack_options)
        elif self.state == "special":
            self.selected = (self.selected + direction) % len(self.special_moves)
            
    def select(self):
        sfx['menu_select'].play()
        if self.state == "main":
            if self.main_options[self.selected] == "Attack":
                self.state = "attack"
                self.selected = 0
            elif self.main_options[self.selected] == "Special":
                self.state = "special"
                self.selected = 0
        return self.selected
        
    def back(self):
        if self.state != "main":
            self.state = "main"
            self.selected = 0

# ─────────────────────────────────────────────────────────────────
# GAME OBJECTS
# ─────────────────────────────────────────────────────────────────
class Mario:
    def __init__(self):
        self.hp = MARIO_MAX_HP
        self.fp = MARIO_MAX_FP
        self.x = 200
        self.y = 350
        self.animation_state = "idle"
        self.animation_timer = 0
        
class Partner:
    def __init__(self, name):
        self.name = name
        self.hp = PARTNER_HP.get(name, 20)
        self.x = 150
        self.y = 350
        
class Enemy:
    def __init__(self, enemy_type):
        self.type = enemy_type
        self.hp = ENEMY_HP.get(enemy_type, 5)
        self.x = 600
        self.y = 350
        self.animation_state = "idle"
        self.animation_timer = 0

# ─────────────────────────────────────────────────────────────────
# RENDERING
# ─────────────────────────────────────────────────────────────────
def draw_mario(surface, mario):
    """Draw Mario in Sticker Star paper style"""
    x, y = int(mario.x), int(mario.y)
    # Body (trapezoid for paper-like torso)
    body_points = [(x-20, y+20), (x+20, y+20), (x+15, y-20), (x-15, y-20)]
    pygame.draw.polygon(surface, BLUE, body_points)
    pygame.draw.polygon(surface, BLACK, body_points, 2)  # Outline
    
    # Head (rounded rectangle)
    pygame.draw.rect(surface, SKIN, (x-15, y-35, 30, 20))
    pygame.draw.rect(surface, BLACK, (x-15, y-35, 30, 20), 2)
    
    # Hat (red cap with 'M')
    hat_points = [(x-20, y-35), (x+20, y-35), (x+15, y-50), (x-15, y-50)]
    pygame.draw.polygon(surface, RED, hat_points)
    pygame.draw.polygon(surface, BLACK, hat_points, 2)
    m_text = font_small.render('M', True, WHITE)
    surface.blit(m_text, (x-5, y-45))
    
    # Animation: Arm swing for jump/hammer
    if mario.animation_state == "jump":
        arm_angle = math.sin(mario.animation_timer * 5) * 30
        arm_start = (x-10, y)
        arm_end = (x-30, y + math.sin(math.radians(arm_angle)) * 20)
        pygame.draw.line(surface, BLUE, arm_start, arm_end, 5)
        pygame.draw.line(surface, BLACK, arm_start, arm_end, 1)
    elif mario.animation_state == "hammer":
        arm_angle = math.sin(mario.animation_timer * 5) * 45
        arm_start = (x+10, y)
        arm_end = (x+30, y - math.cos(math.radians(arm_angle)) * 20)
        pygame.draw.line(surface, BLUE, arm_start, arm_end, 5)
        pygame.draw.line(surface, BLACK, arm_start, arm_end, 1)
        # Hammer head
        hammer_x = arm_end[0]
        hammer_y = arm_end[1]
        pygame.draw.rect(surface, GRAY, (hammer_x-10, hammer_y-5, 15, 10))
        pygame.draw.rect(surface, BLACK, (hammer_x-10, hammer_y-5, 15, 10), 2)

def draw_chain_chomp(surface, enemy):
    """Draw Chain Chomp in Sticker Star paper style"""
    x, y = int(enemy.x), int(enemy.y)
    # Body (large hexagon for chomp head)
    chomp_points = []
    for i in range(6):
        angle = i * math.pi / 3
        chomp_points.append((x + 40 * math.cos(angle), y + 40 * math.sin(angle)))
    pygame.draw.polygon(surface, GRAY, chomp_points)
    pygame.draw.polygon(surface, BLACK, chomp_points, 2)
    
    # Eyes (white ovals with black pupils)
    pygame.draw.ellipse(surface, WHITE, (x-20, y-20, 15, 10))
    pygame.draw.ellipse(surface, WHITE, (x+5, y-20, 15, 10))
    pygame.draw.ellipse(surface, BLACK, (x-15, y-18, 5, 5))
    pygame.draw.ellipse(surface, BLACK, (x+10, y-18, 5, 5))
    
    # Chain (three links)
    for i in range(3):
        chain_x = x + 50 + i * 20
        chain_y = y + 10
        pygame.draw.circle(surface, GRAY, (chain_x, chain_y), 8)
        pygame.draw.circle(surface, BLACK, (chain_x, chain_y), 8, 2)
    
    # Animation: Jaw snap for attack
    if enemy.animation_state == "attack":
        jaw_offset = math.sin(enemy.animation_timer * 10) * 10
        jaw_points = [(x-20, y+20), (x+20, y+20), (x+15, y+20+jaw_offset), (x-15, y+20+jaw_offset)]
        pygame.draw.polygon(surface, GRAY, jaw_points)
        pygame.draw.polygon(surface, BLACK, jaw_points, 2)

def draw_stage(surface):
    """Draw TTYD-style battle stage"""
    pygame.draw.rect(surface, STAGE_BROWN, (50, 400, 700, 150))
    for i in range(0, 700, 50):
        pygame.draw.line(surface, BLACK, (50 + i, 400), (50 + i, 550), 2)
    pygame.draw.rect(surface, CURTAIN_RED, (0, 0, 800, 100))
    pygame.draw.rect(surface, CURTAIN_RED, (0, 0, 50, 600))
    pygame.draw.rect(surface, CURTAIN_RED, (750, 0, 50, 600))
    for i in range(3):
        x = 200 + i * 200
        pygame.draw.circle(surface, GOLD, (x, 80), 20)
        pygame.draw.polygon(surface, (255, 255, 200, 50), [(x-30, 80), (x+30, 80), (x+50, 400), (x-50, 400)])

def draw_audience(surface, audience):
    """Draw TTYD audience"""
    colors = {
        'toad': (255, 200, 200),
        'koopa': (100, 200, 100),
        'goomba': (150, 100, 50),
        'boo': (240, 240, 240),
        'shy_guy': (200, 50, 50)
    }
    for member in audience.members:
        color = colors.get(member['type'], WHITE)
        y_offset = math.sin(member['animation']) * 2
        pygame.draw.ellipse(surface, color, (int(member['x'])-5, int(member['y'] + y_offset)-5, 10, 10))

def draw_star_power(surface, star_power):
    """Draw TTYD star power meter"""
    x, y = 20, 100
    stars_filled = star_power // STAR_POWER_PER_BAR
    partial_fill = (star_power % STAR_POWER_PER_BAR) / STAR_POWER_PER_BAR
    for i in range(8):
        star_x = x + i * 25
        if i < stars_filled:
            color = GOLD
        elif i == stars_filled:
            color = (int(255 * partial_fill), int(215 * partial_fill), 0)
        else:
            color = (50, 50, 50)
        points = []
        for j in range(10):
            angle = j * math.pi / 5
            if j % 2 == 0:
                r = 10
            else:
                r = 5
            px = star_x + r * math.cos(angle - math.pi / 2)
            py = y + r * math.sin(angle - math.pi / 2)
            points.append((px, py))
        pygame.draw.polygon(surface, color, points)

def draw_hp_fp_bars(surface, mario):
    """Draw TTYD-style HP/FP bars"""
    x, y = 20, 20
    pygame.draw.rect(surface, BLACK, (x-2, y-2, 204, 24))
    pygame.draw.rect(surface, RED, (x, y, 200, 20))
    hp_width = int(200 * mario.hp / MARIO_MAX_HP)
    pygame.draw.rect(surface, GREEN, (x, y, hp_width, 20))
    hp_text = font_ui.render(f"HP: {mario.hp}/{MARIO_MAX_HP}", True, WHITE)
    surface.blit(hp_text, (x + 5, y + 2))
    y += 30
    pygame.draw.rect(surface, BLACK, (x-2, y-2, 204, 24))
    pygame.draw.rect(surface, (100, 100, 200), (x, y, 200, 20))
    fp_width = int(200 * mario.fp / MARIO_MAX_FP)
    pygame.draw.rect(surface, (100, 100, 255), (x, y, fp_width, 20))
    fp_text = font_ui.render(f"FP: {mario.fp}/{MARIO_MAX_FP}", True, WHITE)
    surface.blit(fp_text, (x + 5, y + 2))

def draw_battle_menu(surface, menu):
    """Draw TTYD-style battle menu"""
    menu_x, menu_y = 250, 450
    menu_width, menu_height = 300, 120
    pygame.draw.rect(surface, BLACK, (menu_x-2, menu_y-2, menu_width+4, menu_height+4))
    pygame.draw.rect(surface, (200, 200, 255), (menu_x, menu_y, menu_width, menu_height))
    if menu.state == "main":
        options = menu.main_options
    elif menu.state == "attack":
        options = menu.attack_options
    elif menu.state == "special":
        options = menu.special_moves
    else:
        options = []
    for i, option in enumerate(options):
        y = menu_y + 10 + i * 20
        if i == menu.selected:
            pygame.draw.polygon(surface, GOLD, [(menu_x + 10, y + 8), (menu_x + 20, y + 3), (menu_x + 20, y + 13)])
            color = GOLD
        else:
            color = BLACK
        text = font_ui.render(option, True, color)
        surface.blit(text, (menu_x + 30, y))

def draw_damage_number(surface, x, y, damage, color=RED, style="normal"):
    """Draw TTYD-style damage numbers"""
    if style == "excellent":
        text = font_damage.render(str(damage), True, GOLD)
        outline = font_damage.render(str(damage), True, BLACK)
    else:
        text = font_damage.render(str(damage), True, color)
        outline = font_damage.render(str(damage), True, BLACK)
    for dx, dy in [(-2,-2), (2,-2), (-2,2), (2,2)]:
        surface.blit(outline, (x+dx, y+dy))
    surface.blit(text, (x, y))

def draw_action_command_hint(surface, action_cmd):
    """Draw action command timing hint"""
    if action_cmd.active:
        x, y = 400, 300
        bar_width = 200
        pygame.draw.rect(surface, BLACK, (x-bar_width//2-2, y-12, bar_width+4, 24))
        pygame.draw.rect(surface, WHITE, (x-bar_width//2, y-10, bar_width, 20))
        if action_cmd.type == "defense":
            guard_start_x = x - bar_width//2 + int(bar_width * action_cmd.guard_start / 60)
            guard_end_x = x - bar_width//2 + int(bar_width * action_cmd.guard_end / 60)
            guard_width = guard_end_x - guard_start_x
            pygame.draw.rect(surface, GREEN, (guard_start_x, y-10, guard_width, 20))
            superguard_start_x = x - bar_width//2 + int(bar_width * action_cmd.superguard_start / 60)
            superguard_end_x = x - bar_width//2 + int(bar_width * action_cmd.superguard_end / 60)
            superguard_width = superguard_end_x - superguard_start_x
            pygame.draw.rect(surface, GOLD, (superguard_start_x, y-10, superguard_width, 20))
        else:
            window_start_x = x - bar_width//2 + int(bar_width * action_cmd.window_start / 60)
            window_end_x = x - bar_width//2 + int(bar_width * action_cmd.window_end / 60)
            window_width = window_end_x - window_start_x
            pygame.draw.rect(surface, GREEN, (window_start_x, y-10, window_width, 20))
        current_x = x - bar_width//2 + int(bar_width * action_cmd.timer / 60)
        pygame.draw.rect(surface, RED, (current_x-2, y-15, 4, 30))
        if action_cmd.type == "defense":
            text = font_ui.render("Press A to Guard, B to Superguard!", True, WHITE)
        elif action_cmd.type == "superguard":
            text = font_ui.render("Press B to Superguard!", True, WHITE)
        else:
            text = font_ui.render("Press A!", True, WHITE)
        surface.blit(text, (x - text.get_width()//2, y-40))

# ─────────────────────────────────────────────────────────────────
# GAME STATE
# ─────────────────────────────────────────────────────────────────
class BattleState:
    def __init__(self):
        self.mario = Mario()
        self.partner = Partner("Goomba")
        self.enemies = [Enemy("Chain Chomp")]
        self.menu = BattleMenu()
        self.audience = Audience()
        self.stage_hazards = StageHazard()
        self.action_command = ActionCommand("jump")
        self.star_power = 200
        self.turn = "player"
        self.battle_phase = "menu"
        self.damage_numbers = []
        self.defense_success = False
        self.defense_perfect = False
        self.attack_timer = 0
        self.current_enemy_attacking = None
        
    def update(self, dt):
        self.audience.update(dt)
        self.stage_hazards.update(dt)
        self.action_command.update()
        self.mario.animation_timer += dt
        for enemy in self.enemies:
            enemy.animation_timer += dt
        for i in range(len(self.damage_numbers)-1, -1, -1):
            x, y, damage, timer, style = self.damage_numbers[i]
            timer -= dt
            y -= 50 * dt
            if timer <= 0:
                self.damage_numbers.pop(i)
            else:
                self.damage_numbers[i] = (x, y, damage, timer, style)
        if self.battle_phase == "enemy_turn":
            if self.current_enemy_attacking is None:
                if self.enemies:
                    self.current_enemy_attacking = self.enemies[0]
                    self.current_enemy_attacking.animation_state = "attack"
                    self.action_command = ActionCommand("defense")
                    self.action_command.start()
                    self.attack_timer = 60
                else:
                    self.battle_phase = "menu"
                    self.turn = "player"
            else:
                self.attack_timer -= 1
                if self.attack_timer <= 0:
                    enemy = self.current_enemy_attacking
                    base_damage = 4
                    if self.defense_perfect:
                        damage = 0
                        enemy.hp -= 1
                        sfx['excellent'].play()
                        self.damage_numbers.append((enemy.x, enemy.y - 30, 1, 1.0, "excellent"))
                    elif self.defense_success:
                        damage = max(0, base_damage - 1)
                    else:
                        damage = base_damage
                    if damage > 0:
                        self.mario.hp -= damage
                        self.damage_numbers.append((self.mario.x, self.mario.y - 30, damage, 1.0, "normal"))
                        sfx['damage'].play()
                    enemy.animation_state = "idle"
                    self.current_enemy_attacking = None
                    self.battle_phase = "menu"
                    self.turn = "player"
                    self.defense_success = False
                    self.defense_perfect = False
                    if self.mario.hp <= 0:
                        self.battle_phase = "game_over"
                
    def handle_attack(self, attack_type):
        self.mario.animation_state = attack_type
        self.mario.animation_timer = 0
        if attack_type == "jump":
            self.action_command = ActionCommand("jump")
            self.action_command.start()
            sfx['jump'].play()
        elif attack_type == "hammer":
            self.action_command = ActionCommand("hammer")
            self.action_command.start()
            sfx['hammer'].play()
            
    def check_action_command(self):
        if self.action_command.check_input():
            if self.action_command.perfect:
                sfx['excellent'].play()
                damage = 3
                style = "excellent"
                self.star_power = min(MAX_STAR_POWER, self.star_power + 50)
                self.audience.react("excellent")
            else:
                damage = 2
                style = "normal"
                self.star_power = min(MAX_STAR_POWER, self.star_power + 25)
            if self.enemies:
                enemy = self.enemies[0]
                enemy.hp -= damage
                self.damage_numbers.append((enemy.x, enemy.y - 30, damage, 1.0, style))
                sfx['damage'].play()
                if enemy.hp <= 0:
                    self.enemies.remove(enemy)
                    self.star_power = min(MAX_STAR_POWER, self.star_power + 100)
            self.mario.animation_state = "idle"
            return True
        return False
    
    def use_special_move(self, move_index):
        move = self.menu.special_moves[move_index]
        star_cost = (move_index + 1) * 100
        if self.star_power >= star_cost:
            self.star_power -= star_cost
            sfx['star_power'].play()
            if move == "Sweet Treat":
                self.mario.hp = min(MARIO_MAX_HP, self.mario.hp + 10)
                self.mario.fp = min(MARIO_MAX_FP, self.mario.fp + 10)

# ─────────────────────────────────────────────────────────────────
# MAIN GAME LOOP
# ─────────────────────────────────────────────────────────────────
def main():
    battle = BattleState()
    running = True
    dt = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif battle.battle_phase == "menu":
                    if event.key in (pygame.K_UP, pygame.K_w):
                        battle.menu.move_cursor(-1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        battle.menu.move_cursor(1)
                    elif event.key in (pygame.K_RETURN, pygame.K_a, pygame.K_SPACE):
                        selected = battle.menu.select()
                        if battle.menu.state == "attack":
                            if battle.menu.attack_options[selected] == "Jump":
                                battle.handle_attack("jump")
                                battle.battle_phase = "action"
                            elif battle.menu.attack_options[selected] == "Hammer":
                                battle.handle_attack("hammer")
                                battle.battle_phase = "action"
                    elif event.key in (pygame.K_BACKSPACE, pygame.K_b):
                        battle.menu.back()
                elif battle.battle_phase == "action":
                    if event.key in (pygame.K_a, pygame.K_SPACE):
                        if battle.check_action_command():
                            battle.battle_phase = "enemy_turn"
                            battle.turn = "enemy"
                    elif event.key == pygame.K_b:
                        superguard = ActionCommand("superguard")
                        superguard.start()
                        if superguard.check_input(perfect_only=True):
                            sfx['excellent'].play()
                elif battle.battle_phase == "enemy_turn":
                    if event.key in (pygame.K_a, pygame.K_SPACE):
                        if battle.action_command.check_guard():
                            battle.defense_success = True
                    elif event.key == pygame.K_b:
                        if battle.action_command.check_superguard():
                            battle.defense_perfect = True
                            battle.defense_success = True
        
        battle.update(dt)
        
        screen.fill((50, 50, 100))
        draw_stage(screen)
        draw_audience(screen, battle.audience)
        draw_mario(screen, battle.mario)
        for enemy in battle.enemies:
            draw_chain_chomp(screen, enemy)
        draw_hp_fp_bars(screen, battle.mario)
        draw_star_power(screen, battle.star_power)
        if battle.battle_phase == "menu":
            draw_battle_menu(screen, battle.menu)
        elif battle.battle_phase in ("action", "enemy_turn"):
            draw_action_command_hint(screen, battle.action_command)
        for x, y, damage, timer, style in battle.damage_numbers:
            draw_damage_number(screen, int(x), int(y), damage, RED, style)
        for hazard in battle.stage_hazards.active_hazards:
            if hazard['type'] == 'falling_object':
                pygame.draw.ellipse(pygame.Surface, BLACK, (int(hazard['x'])-15, int(hazard['y'])-15, 30, 30))
                hazard['y'] += 200 * dt
        if battle.battle_phase == "game_over":
            text = font_damage.render("Game Over", True, RED)
            screen.blit(text, (WW//2 - text.get_width()//2, WH//2 - 24))
        
        pygame.display.flip()
        dt = clock.tick(FPS) / 1000.0
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    screen.fill(BLACK)
    splash_text = pygame.font.Font(None, 48).render("TEAM SPECIALEMU AGI Division Presents", True, WHITE)
    screen.blit(splash_text, (WW//2 - splash_text.get_width()//2, WH//2 - 24))
    pygame.display.flip()
    pygame.time.wait(2000)
    main()
