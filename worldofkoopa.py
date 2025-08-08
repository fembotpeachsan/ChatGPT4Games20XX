# Koopa of the Stars — World of Light (files-off, Pygame)
# Everything is A-Koopa. Stats are Deltarune-ish. Deterministic via vibe-code.
# No external assets; all art & SFX are procedural or omitted.
# Controls:
#   Map:   WASD/Arrows to move, Enter to battle
#   Battle: A/D or Left/Right to move, W/Up/Space to jump (double), J attack, K special (TP), LShift dash
#           Esc to return to map after battle end
#   Global: V = toggle vibes, R (title) = new vibe code
# Env: KOOPA_VIBE="your-code"   # optional seed

import os
import sys
import math
import random
import pygame
from pygame import Rect
from pygame.math import Vector2

# ------------------------------------------------------------
# Config
# ------------------------------------------------------------
WIDTH, HEIGHT = 960, 540
FIXED_DT = 1.0 / 60.0
GRAVITY = 1900.0
TITLE = "KOOPA OF THE STARS — files=off"
STARTING_LV = 1

# Colors (RGB)
def hsv(h, s, v):
    import colorsys
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, max(0, min(1, s)), max(0, min(1, v)))
    return (int(r * 255), int(g * 255), int(b * 255))

WHITE = (240, 240, 240)
BLACK = (12, 12, 16)
GREY  = (70, 70, 80)
GOLD  = (250, 210, 80)
RED   = (240, 70, 70)
GREEN = (80, 220, 140)
CYAN  = (100, 230, 230)

def clamp(x, a, b): return a if x < a else (b if x > b else x)

# Deterministic, portable string->seed
def stable_seed_from(text: str) -> int:
    # 64-bit FNV-1a
    h = 0xcbf29ce484222325
    for ch in text.encode("utf-8"):
        h ^= ch
        h = (h * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return h & 0x7FFFFFFFFFFFFFFF

# ------------------------------------------------------------
# Stats (Deltarune-ish)
# ------------------------------------------------------------
class Stats:
    def __init__(self, lv=1):
        # LV scales baseline HP/ATK/DEF a touch
        self.lv = lv
        base = 60 + 6 * (lv - 1)
        self.hp_max = base
        self.hp = self.hp_max
        self.atk = 10 + 2 * (lv - 1)
        self.df  = 6 + 1 * (lv - 1)
        self.mag = 10
        self.spd = 10
        self.tp = 0
        self.tp_max = 100

    def heal_full(self):
        self.hp = self.hp_max
        self.tp = min(self.tp, self.tp_max)

    def add_tp(self, amount):
        self.tp = clamp(self.tp + amount, 0, self.tp_max)

    def take_damage(self, dmg):
        self.hp = max(0, self.hp - int(max(1, dmg)))

    def is_dead(self):
        return self.hp <= 0

# ------------------------------------------------------------
# Difficulty Agent (gentle auto-tuning)
# ------------------------------------------------------------
class DifficultyAgent:
    def __init__(self):
        self.target_time = 35.0   # seconds per battle
        self.smoothed_ratio = 1.0

    def suggest_scale(self, clear_time_s: float, player_lost: bool):
        # If you crushed it quickly, scale up a bit; if struggled, scale down a tad.
        ratio = self.target_time / max(10.0, clear_time_s)
        if player_lost:
            ratio *= 0.6
        # smooth
        self.smoothed_ratio = 0.85 * self.smoothed_ratio + 0.15 * ratio
        return clamp(self.smoothed_ratio, 0.6, 1.6)

# ------------------------------------------------------------
# Rendering helpers — Everything is A-Koopa
# ------------------------------------------------------------
def draw_shell(surface, pos, radius, hue=0.28, spin=0.0, outline=2):
    # Koopa-y shell: colored disk + hex spokes
    x, y = int(pos.x), int(pos.y)
    main = hsv(hue, 0.65, 0.9)
    rim  = hsv(hue - 0.06, 0.25, 0.98)
    pygame.draw.circle(surface, rim, (x, y), int(radius + outline))
    pygame.draw.circle(surface, main, (x, y), int(radius))
    # Hex spokes
    spokes = 6
    for i in range(spokes):
        ang = spin + i * (2 * math.pi / spokes)
        x2 = x + int(math.cos(ang) * radius * 0.82)
        y2 = y + int(math.sin(ang) * radius * 0.82)
        pygame.draw.line(surface, WHITE, (x, y), (x2, y2), 2)

def draw_face(surface, pos, radius):
    x, y = int(pos.x), int(pos.y)
    eye_off = radius * 0.35
    eye_r = max(2, int(radius * 0.12))
    pygame.draw.circle(surface, BLACK, (x - int(eye_off), y - int(eye_off)), eye_r)
    pygame.draw.circle(surface, BLACK, (x + int(eye_off), y - int(eye_off)), eye_r)

def draw_akoopa(surface, pos, radius, hue=0.28, spin=0.0):
    draw_shell(surface, pos, radius, hue, spin)
    draw_face(surface, pos, radius)

# ------------------------------------------------------------
# Physics helpers
# ------------------------------------------------------------
def circle_rect_collision_response(pos: Vector2, vel: Vector2, r: float, rect: Rect):
    # Push circle out of rect if overlapping; naive but robust
    nearest_x = clamp(pos.x, rect.left, rect.right)
    nearest_y = clamp(pos.y, rect.top, rect.bottom)
    dx = pos.x - nearest_x
    dy = pos.y - nearest_y
    d2 = dx * dx + dy * dy
    if d2 >= r * r:
        return pos, vel, False, Vector2()
    d = math.sqrt(max(1e-6, d2))
    if d == 0:
        # In a corner; push up
        n = Vector2(0, -1)
    else:
        n = Vector2(dx / d, dy / d)
    penetration = r - d
    pos += n * (penetration + 0.5)
    # Reflect velocity on normal if moving into surface, with friction
    vn = vel.dot(n)
    if vn < 0:
        vel -= n * (1.4 * vn)  # lose energy
        # apply friction on tangent
        t = Vector2(-n.y, n.x)
        vt = vel.dot(t)
        vel -= t * (0.15 * vt)
    grounded = n.y < -0.7  # standing on top
    return pos, vel, grounded, n

# ------------------------------------------------------------
# Entities
# ------------------------------------------------------------
class Entity:
    def __init__(self, pos, radius, hue, stats: Stats, mass=1.0):
        self.pos = Vector2(pos)
        self.vel = Vector2(0, 0)
        self.radius = radius
        self.hue = hue
        self.stats = stats
        self.mass = mass
        self.grounded = False
        self.alive = True
        self.spin = 0.0
        self.iframes = 0.0

    def update(self, dt):
        self.spin += dt * 8.0
        if self.iframes > 0:
            self.iframes -= dt

    def draw(self, surf):
        draw_akoopa(surf, self.pos, self.radius, self.hue, self.spin)

    def hit(self, dmg, knockback: Vector2):
        if self.iframes > 0:
            return
        # Simple Deltarune-ish: damage reduced by DEF
        actual = max(1, int(dmg + 0.5 - 0.5 * self.stats.df))
        self.stats.take_damage(actual)
        self.vel += knockback / max(0.3, self.mass)
        self.iframes = 0.3
        if self.stats.is_dead():
            self.alive = False

class Projectile:
    def __init__(self, pos, vel, radius, hue, dmg, ttl=3.5, owner=None, friendly=False):
        self.pos = Vector2(pos)
        self.vel = Vector2(vel)
        self.radius = radius
        self.hue = hue
        self.dmg = dmg
        self.ttl = ttl
        self.owner = owner
        self.friendly = friendly
        self.alive = True
        self.spin = 0.0

    def update(self, dt, gravity=0.0):
        self.spin += dt * 5.0
        self.ttl -= dt
        if self.ttl <= 0:
            self.alive = False
            return
        self.vel.y += gravity * dt
        self.pos += self.vel * dt

    def draw(self, surf):
        draw_shell(surf, self.pos, self.radius, self.hue, self.spin)

# ------------------------------------------------------------
# Player & Enemy
# ------------------------------------------------------------
class Player(Entity):
    def __init__(self, pos, rng: random.Random):
        super().__init__(pos, radius=18, hue=0.28, stats=Stats(STARTING_LV), mass=1.0)
        self.base_speed = 320
        self.jump_speed = 820
        self.double_jump = True
        self.dash_timer = 0.0
        self.dash_cool = 0.0
        self.rng = rng

    def control(self, keys, projectiles):
        # Horizontal
        move = 0.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  move -= 1.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move += 1.0
        target_vx = move * self.base_speed
        accel = 4000.0 if self.grounded else 2200.0
        self.vel.x += clamp(target_vx - self.vel.x, -accel, accel) * FIXED_DT

        # Jump (W/UP/Space)
        jump_pressed = keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]
        if jump_pressed and self.grounded:
            self.vel.y = -self.jump_speed
            self.grounded = False
            self.double_jump = True
        elif jump_pressed and self.double_jump:
            self.vel.y = -0.9 * self.jump_speed
            self.double_jump = False

        # Dash (LShift)
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.dash_cool <= 0 and self.dash_timer <= 0:
            self.dash_timer = 0.12
            self.dash_cool = 0.5
            facing = 1 if self.vel.x >= 0 else -1
            self.vel.x = 650 * facing

        # Attack (J) — star shell
        return  # attack specials are handled by input polling in scene

    def primary_attack(self):
        # One forward shell
        speed = 520 + 15 * self.stats.mag * 0.3
        direction = 1 if self.vel.x >= 0 else -1
        vel = Vector2(direction * speed, -80)
        dmg = 6 + 0.5 * self.stats.atk
        hue = 0.28
        return Projectile(self.pos + Vector2(direction * (self.radius + 6), -4),
                          vel, radius=8, hue=hue, dmg=dmg, ttl=2.0, owner=self, friendly=True)

    def special_attack(self):
        # Star burst — ring of shells (cost TP)
        if self.stats.tp < 40:
            return []
        self.stats.tp -= 40
        n = 8
        shells = []
        for i in range(n):
            ang = (2 * math.pi * i) / n
            vel = Vector2(math.cos(ang), math.sin(ang)) * (420 + 6 * self.stats.mag)
            shells.append(Projectile(self.pos + Vector2(0, -4), vel, radius=7, hue=0.12, dmg=5 + 0.4 * self.stats.atk, ttl=1.8, owner=self, friendly=True))
        return shells

    def update(self, dt):
        super().update(dt)
        if self.dash_timer > 0:
            self.dash_timer -= dt
        if self.dash_cool > 0:
            self.dash_cool -= dt

class SpiritKoopa(Entity):
    def __init__(self, pos, rng: random.Random, scale=1.0, hue=0.46):
        lv = max(1, int(STARTING_LV + scale * 2))
        stats = Stats(lv)
        stats.hp_max = int(40 + 28 * scale)
        stats.hp = stats.hp_max
        stats.atk = int(8 + 4 * scale)
        stats.df  = int(5 + 2 * scale)
        super().__init__(pos, radius=16 + 3 * scale, hue=hue, stats=stats, mass=1.2 + 0.2 * scale)
        self.rng = rng
        self.jump_cd = 0.4 + 0.3 * self.rng.random()
        self.shoot_cd = 0.8
        self.think_cd = 0.2
        self.air_time = 0.0

    def ai(self, player: Player, projectiles, modifiers):
        # Horizontal chase
        dir = math.copysign(1.0, (player.pos.x - self.pos.x) or 1.0)
        target = 260.0 * dir
        accel = 1900.0 if self.grounded else 1200.0
        self.vel.x += clamp(target - self.vel.x, -accel, accel) * FIXED_DT

        # Occasional jump over bullets / towards platforms
        self.air_time = 0.0 if self.grounded else (self.air_time + FIXED_DT)
        self.jump_cd -= FIXED_DT
        if self.grounded and self.jump_cd <= 0:
            self.jump_cd = 0.7 + 0.6 * self.rng.random()
            if abs(player.pos.x - self.pos.x) < 130 or self.rng.random() < 0.35:
                self.vel.y = -760

        # Shoot patterns
        self.shoot_cd -= FIXED_DT
        if self.shoot_cd <= 0:
            self.shoot_cd = 0.9 + 0.5 * self.rng.random()
            # Pattern: small spiral or burst
            if self.rng.random() < 0.5:
                for k in range(3):
                    ang = math.atan2(player.pos.y - self.pos.y, player.pos.x - self.pos.x) + 0.25 * (k - 1)
                    spd = 360 + 120 * self.rng.random()
                    vel = Vector2(math.cos(ang), math.sin(ang)) * spd
                    projectiles.append(Projectile(self.pos, vel, radius=6, hue=0.55, dmg=4 + 0.6 * self.stats.atk, ttl=3.0, owner=self, friendly=False))
            else:
                # ring
                n = 10
                base = self.rng.random() * math.pi * 2
                for i in range(n):
                    ang = base + i * (2 * math.pi / n)
                    vel = Vector2(math.cos(ang), math.sin(ang)) * 280
                    projectiles.append(Projectile(self.pos, vel, radius=5, hue=0.58, dmg=3 + 0.5 * self.stats.atk, ttl=2.5, owner=self, friendly=False))

    def update(self, dt):
        super().update(dt)

# ------------------------------------------------------------
# Stage / Arena
# ------------------------------------------------------------
class Stage:
    def __init__(self, w, h):
        self.rects = []
        floor_h = 60
        self.rects.append(Rect(0, h - floor_h, w, floor_h))
        # Platforms
        plat_w, plat_h = int(w * 0.24), 18
        y = int(h * 0.64)
        self.rects.append(Rect(int(w * 0.5) - plat_w // 2, y, plat_w, plat_h))
        self.rects.append(Rect(int(w * 0.22) - plat_w // 2, int(y - 110), plat_w, plat_h))
        self.rects.append(Rect(int(w * 0.78) - plat_w // 2, int(y - 110), plat_w, plat_h))
        self.blast = Rect(-240, -240, w + 480, h + 480)  # outside = KO zone

    def draw(self, surf, vibes=False, t=0.0):
        if vibes:
            # Subtle gradient sweep
            for i in range(8):
                c = hsv((0.58 + 0.1 * math.sin(t * 0.2 + i)) % 1.0, 0.25, 0.10 + 0.04 * i)
                pygame.draw.rect(surf, c, Rect(0, int(HEIGHT * i / 8), WIDTH, int(HEIGHT / 8) + 1))
        # Platforms and floor
        for r in self.rects:
            pygame.draw.rect(surf, (40, 50, 60), r.inflate(4, 4), border_radius=6)
            pygame.draw.rect(surf, (120, 150, 170), r, border_radius=6)

# ------------------------------------------------------------
# Battle Scene
# ------------------------------------------------------------
class BattleScene:
    def __init__(self, rng: random.Random, difficulty_scale=1.0, modifiers=None, vibes=False):
        self.rng = rng
        self.stage = Stage(WIDTH, HEIGHT)
        self.player = Player(Vector2(WIDTH * 0.25, HEIGHT * 0.3), rng)
        self.player.stats.lv = STARTING_LV
        self.player.stats.heal_full()
        self.projectiles = []
        self.enemies = []
        self.vibes = vibes
        self.t = 0.0
        self.done = False
        self.win = False
        self.clear_time = None
        self.modifiers = modifiers or {}
        # Spawn enemies
        count = int(1 + difficulty_scale * 1.2)
        for i in range(count):
            x = WIDTH * (0.55 + 0.25 * self.rng.random())
            y = HEIGHT * (0.3 + 0.4 * self.rng.random())
            hue = 0.46 + 0.08 * self.rng.random()
            self.enemies.append(SpiritKoopa(Vector2(x, y), rng, scale=0.8 + 0.8 * difficulty_scale, hue=hue))

    def apply_modifiers(self, ent: Entity):
        # Simple gravity & wind modifiers
        g = GRAVITY
        if self.modifiers.get("low_g"): g *= 0.6
        if self.modifiers.get("high_g"): g *= 1.4
        wind = 0.0
        if self.modifiers.get("windy"):
            wind = 100.0 * math.sin(self.t * 0.7)
        ent.vel.y += g * FIXED_DT
        ent.vel.x += wind * FIXED_DT

    def handle_entity_vs_stage(self, ent: Entity):
        ent.grounded = False
        for r in self.stage.rects:
            ent.pos, ent.vel, grounded, _ = circle_rect_collision_response(ent.pos, ent.vel, ent.radius, r)
            ent.grounded = ent.grounded or grounded

    def update(self, keys, just_pressed):
        self.t += FIXED_DT

        # Player control + skill keys
        self.player.control(keys, self.projectiles)
        if just_pressed(pygame.K_j):
            self.projectiles.append(self.player.primary_attack())
            self.player.stats.add_tp(6)
        if just_pressed(pygame.K_k):
            self.projectiles.extend(self.player.special_attack())

        # AI
        for e in self.enemies:
            e.ai(self.player, self.projectiles, self.modifiers)

        # Physics
        # Entities
        for ent in [self.player] + self.enemies:
            self.apply_modifiers(ent)
            ent.pos += ent.vel * FIXED_DT
            self.handle_entity_vs_stage(ent)
            ent.update(FIXED_DT)

        # Projectiles
        grav_p = 600.0 if self.modifiers.get("low_g") else (800.0 if self.modifiers.get("high_g") else 700.0)
        for p in self.projectiles:
            p.update(FIXED_DT, grav_p * 0.1)
            # stage bounce on platforms a bit
            for r in self.stage.rects:
                # only bounce off tops
                if r.collidepoint(p.pos.x, p.pos.y + p.radius):
                    p.vel.y = -abs(p.vel.y) * 0.55
            # KO if outside blast
            if not self.stage.blast.collidepoint(p.pos.x, p.pos.y):
                p.alive = False

        # Collisions: projectiles vs entities
        for p in self.projectiles:
            if not p.alive: continue
            targets = [self.player] if not p.friendly else self.enemies
            for t in targets:
                if not t.alive: continue
                if (t.pos - p.pos).length_squared() <= (t.radius + p.radius) ** 2:
                    # Damage & knockback
                    dir = (t.pos - p.pos)
                    if dir.length_squared() == 0: dir = Vector2(1, -0.2)
                    kvec = dir.normalize() * (150 + 2.2 * p.dmg)
                    t.hit(p.dmg, kvec)
                    if p.friendly:
                        self.player.stats.add_tp(3)
                    p.alive = False
                    break

        # Clean up
        self.projectiles = [p for p in self.projectiles if p.alive]
        self.enemies = [e for e in self.enemies if e.alive]

        # Fail if player KO: respawn with HP penalty
        if not self.player.alive:
            self.done = True
            self.win = False
            self.clear_time = self.t

        # Win if all enemies defeated
        if not self.enemies and not self.done:
            self.done = True
            self.win = True
            self.clear_time = self.t

    def draw(self, surf):
        self.stage.draw(surf, vibes=self.vibes, t=self.t)
        # projectiles
        for p in self.projectiles:
            p.draw(surf)
        # entities
        for e in self.enemies:
            e.draw(surf)
        self.player.draw(surf)
        self.draw_hud(surf)

    def draw_hud(self, surf):
        # HP bar & TP
        x, y = 24, 20
        # Nameplate
        label = f"AKOOPA  LV{self.player.stats.lv}"
        self._text(surf, label, x, y, WHITE, 24, bold=True)
        # HP
        hp = self.player.stats.hp
        hpmax = self.player.stats.hp_max
        self._text(surf, f"HP {hp}/{hpmax}", x, y + 22, GREEN, 22)
        pygame.draw.rect(surf, WHITE, Rect(x, y + 44, 220, 12), 2)
        w = int(216 * hp / max(1, hpmax))
        pygame.draw.rect(surf, GREEN, Rect(x + 2, y + 46, w, 8))
        # TP
        tp = self.player.stats.tp
        self._text(surf, f"TP {tp:3.0f}/100  [K]", x, y + 64, CYAN, 22)
        pygame.draw.rect(surf, WHITE, Rect(x, y + 86, 220, 10), 2)
        wtp = int(216 * tp / 100)
        pygame.draw.rect(surf, CYAN, Rect(x + 2, y + 88, wtp, 6))

    @staticmethod
    def _text(surf, text, x, y, color, size=24, bold=False, center=False):
        f = pygame.font.SysFont(None, size, bold=bold)
        s = f.render(text, True, color)
        r = s.get_rect()
        if center:
            r.center = (x, y)
        else:
            r.topleft = (x, y)
        surf.blit(s, r)

# ------------------------------------------------------------
# World Map (star graph)
# ------------------------------------------------------------
class Node:
    def __init__(self, idx, pos, difficulty, seed, prereqs=None):
        self.idx = idx
        self.pos = Vector2(pos)
        self.difficulty = difficulty
        self.seed = seed
        self.edges = []
        self.cleared = False
        self.prereqs = set(prereqs or [])

class StarMap:
    def __init__(self, rng: random.Random, count=18):
        self.rng = rng
        self.nodes = []
        self._generate(count)

    def _generate(self, count):
        # Star with 5 rays; nodes spread along rays
        cx, cy = WIDTH * 0.5, HEIGHT * 0.5
        rays = 5
        per = max(2, count // rays)
        idx = 0
        center = Node(idx, (cx, cy), 1, self.rng.randrange(1 << 30))
        self.nodes.append(center)
        idx += 1
        for r in range(rays):
            ang = (2 * math.pi * r) / rays - math.pi / 2
            for i in range(1, per + 1):
                t = i / per
                rad = 80 + 280 * t
                jitter = Vector2(self.rng.uniform(-20, 20), self.rng.uniform(-16, 16))
                pos = Vector2(cx + math.cos(ang) * rad, cy + math.sin(ang) * rad) + jitter
                diff = 1 + i + (1 if self.rng.random() < 0.3 else 0)
                node = Node(idx, pos, diff, self.rng.randrange(1 << 30), prereqs=[idx - 1] if i > 1 else [0])
                self.nodes.append(node)
                idx += 1
        # Connect: center to first of each ray, then chains
        # Build edges by proximity along rays (since we created in sequence)
        for i, n in enumerate(self.nodes):
            for j, m in enumerate(self.nodes):
                if i >= j: continue
                if (n.pos - m.pos).length() < 150 and (len(n.edges) < 3 and len(m.edges) < 3):
                    n.edges.append(j)
                    m.edges.append(i)

    def neighbors(self, idx): return self.nodes[idx].edges

# ------------------------------------------------------------
# App / Scenes
# ------------------------------------------------------------
class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.vibes = False

        # Seed
        vibe = os.environ.get("KOOPA_VIBE", "").strip()
        if not vibe:
            vibe = f"koopa-{random.randrange(10_000)}"
        self.vibe_code = vibe
        self.master_seed = stable_seed_from(vibe)
        self.rng = random.Random(self.master_seed)

        self.agent = DifficultyAgent()

        self.state = "TITLE"
        self.just = set()

        # Map
        self.map = StarMap(self.rng, count=20)
        self.cursor = 0  # node index at center
        self.cleared_count = 0
        self.last_battle_time = None

    def run(self):
        acc = 0.0
        prev = pygame.time.get_ticks() / 1000.0
        running = True
        while running:
            # Real-time -> fixed-step accumulator
            now = pygame.time.get_ticks() / 1000.0
            acc += min(0.25, now - prev)
            prev = now

            # Events
            self.just.clear()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYDOWN:
                    self.just.add(e.key)

            def just_pressed(k): return k in self.just
            keys = pygame.key.get_pressed()

            # Global toggles
            if just_pressed(pygame.K_v):
                self.vibes = not self.vibes

            # Fixed updates
            while acc >= FIXED_DT:
                acc -= FIXED_DT
                if self.state == "TITLE":
                    self.update_title(keys, just_pressed)
                elif self.state == "MAP":
                    self.update_map(keys, just_pressed)
                elif self.state == "BATTLE":
                    self.update_battle(keys, just_pressed)
                elif self.state == "WIN" or self.state == "GAMEOVER":
                    if just_pressed(pygame.K_RETURN) or just_pressed(pygame.K_ESCAPE):
                        self.state = "MAP"

            # Draw
            self.draw()

            # Cap to display refresh (we still simulate at fixed 60)
            self.clock.tick(60)
        pygame.quit()

    # ---------------- TITLE ----------------
    def update_title(self, keys, just):
        if pygame.K_r in self.just:
            # re-roll vibe
            self.vibe_code = f"koopa-{random.randrange(10_000)}"
            self.master_seed = stable_seed_from(self.vibe_code)
            self.rng = random.Random(self.master_seed)
            self.map = StarMap(self.rng, count=20)
            self.cursor = 0
            self.cleared_count = 0
        if pygame.K_RETURN in self.just:
            self.state = "MAP"

    def draw_title(self):
        t = pygame.time.get_ticks() / 1000.0
        self.screen.fill(BLACK)
        # Star ripple background
        for i in range(10):
            rr = (i + 1) * 32 + 12 * math.sin(t * 0.7 + i)
            c = hsv((0.12 * i + 0.6 * math.sin(t * 0.3)) % 1.0, 0.4, 0.08 + 0.06 * i)
            pygame.draw.circle(self.screen, c, (WIDTH // 2, HEIGHT // 2), int(rr), 2)
        title = "KOOPA OF THE STARS"
        self.text(title, WIDTH // 2, HEIGHT // 2 - 40, GOLD, 46, bold=True, center=True)
        self.text("World of Light • Deltarune stats • files=off", WIDTH // 2, HEIGHT // 2 + 2, WHITE, 24, center=True)
        self.text(f"VIBE: {self.vibe_code}", WIDTH // 2, HEIGHT // 2 + 36, CYAN, 22, center=True)
        self.text("[Enter] start   [R] re-roll vibe   [V] vibes mode", WIDTH // 2, HEIGHT // 2 + 72, GREY, 20, center=True)

    # ---------------- MAP ----------------
    def update_map(self, keys, just):
        cur = self.cursor
        node = self.map.nodes[cur]
        # Move cursor along edges
        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])

        if dx or dy:
            # choose neighbor closest to input dir
            desired = Vector2(dx, dy)
            best, bestdot = cur, -1.0
            for nidx in node.edges:
                v = (self.map.nodes[nidx].pos - node.pos)
                if v.length_squared() == 0: continue
                dot = desired.normalize().dot(v.normalize())
                if dot > bestdot:
                    bestdot = dot
                    best = nidx
            self.cursor = best

        # Enter to battle if unlocked
        if pygame.K_RETURN in self.just:
            if self.is_unlocked(self.cursor):
                self.start_battle(self.map.nodes[self.cursor])

    def is_unlocked(self, idx):
        node = self.map.nodes[idx]
        if node.idx == 0:
            return True
        # unlocked if all prerequisites cleared
        for p in node.prereqs:
            if not self.map.nodes[p].cleared:
                return False
        return True

    def start_battle(self, node: Node):
        # Difficulty scaling via agent & node difficulty
        scale = 0.75 + 0.35 * node.difficulty
        if self.last_battle_time is not None:
            scale *= self.agent.suggest_scale(self.last_battle_time, player_lost=False)
        # Random simple modifiers per node
        rng = random.Random(node.seed ^ self.master_seed)
        modifiers = {"low_g": False, "high_g": False, "windy": False}
        pick = rng.random()
        if pick < 0.25: modifiers["low_g"] = True
        elif pick < 0.50: modifiers["high_g"] = True
        elif pick < 0.70: modifiers["windy"] = True
        self.battle = BattleScene(rng, difficulty_scale=scale, modifiers=modifiers, vibes=self.vibes)
        self.state = "BATTLE"

    def draw_map(self):
        self.screen.fill((16, 20, 26))
        # Edges
        for n in self.map.nodes:
            for eid in n.edges:
                m = self.map.nodes[eid]
                pygame.draw.line(self.screen, (40, 60, 80), n.pos, m.pos, 2)

        # Nodes
        for n in self.map.nodes:
            col = (60, 70, 80)
            r = 11
            if n.cleared:
                col = GREEN; r = 12
            elif self.is_unlocked(n.idx):
                col = GOLD; r = 12
            pygame.draw.circle(self.screen, col, n.pos, r)
            pygame.draw.circle(self.screen, (255, 255, 255), n.pos, r, 2)

        # Cursor
        cnode = self.map.nodes[self.cursor]
        pygame.draw.circle(self.screen, CYAN, cnode.pos, 16, 2)

        # HUD
        cleared = sum(1 for n in self.map.nodes if n.cleared)
        self.text(f"Nodes cleared: {cleared}/{len(self.map.nodes)}", 16, 10, WHITE, 22)
        self.text(f"Selected DIFF: {cnode.difficulty}", 16, 36, GREY, 20)
        self.text(f"Unlocked: {'YES' if self.is_unlocked(self.cursor) else 'NO'}", 16, 58, GREY, 20)
        self.text(f"VIBE: {self.vibe_code}", WIDTH - 12, 10, CYAN, 20, center=False, right=True)

        self.text("[Enter] Battle  [V] vibes", WIDTH // 2, HEIGHT - 24, GREY, 20, center=True)

    # ---------------- BATTLE ----------------
    def update_battle(self, keys, just):
        if pygame.K_ESCAPE in self.just and self.battle.done:
            self.state = "MAP"
            return

        self.battle.update(keys, just_pressed=lambda k: (k in self.just))

        if self.battle.done:
            # End screen: mark cleared if win
            if self.battle.win:
                node = self.map.nodes[self.cursor]
                if not node.cleared:
                    node.cleared = True
            self.last_battle_time = self.battle.clear_time
            self.state = "WIN" if self.battle.win else "GAMEOVER"

    def draw_battle(self):
        self.battle.draw(self.screen)
        if self.battle.done:
            msg = "VICTORY!" if self.battle.win else "DEFEAT!"
            col = GREEN if self.battle.win else RED
            self.text(msg, WIDTH // 2, HEIGHT // 2 - 30, col, 42, bold=True, center=True)
            self.text(f"Clear time: {self.battle.clear_time:.1f}s   [Enter/Esc] map",
                      WIDTH // 2, HEIGHT // 2 + 8, WHITE, 22, center=True)

    # ---------------- DRAW WRAPPER ----------------
    def draw(self):
        if self.state == "TITLE":
            self.draw_title()
        elif self.state == "MAP":
            self.draw_map()
        elif self.state == "BATTLE":
            self.draw_battle()
        elif self.state == "WIN" or self.state == "GAMEOVER":
            # reuse battle screen under banner
            self.draw_battle()
        pygame.display.flip()

    # ---------------- TEXT ----------------
    def text(self, s, x, y, color, size=24, bold=False, center=False, right=False):
        f = pygame.font.SysFont(None, size, bold=bold)
        m = f.render(s, True, color)
        r = m.get_rect()
        if center:
            r.center = (x, y)
        elif right:
            r.topright = (x, y)
        else:
            r.topleft = (x, y)
        self.screen.blit(m, r)

# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
if __name__ == "__main__":
    try:
        App().run()
    except Exception as e:
        print("Koopa crashed:", e)
        pygame.quit()
        sys.exit(1)
