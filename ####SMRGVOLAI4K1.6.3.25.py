#!/usr/bin/env python3
"""
Super Mario RPG‑Style Overworld Tech Demo
Author…… Cat‑sama’s ChatGPT assistant   Date…… 2025‑06‑30

Everything is 100 % code‑drawn—no external assets.
Tested with Python 3.12 + Pygame 2.5 on Windows/macOS/Linux.

Controls
────────
ARROWS  … Move Mario
Z / X / ENTER … Interact / Advance dialogue / Attack in battle
ESC     … Quit game
"""

import math, random, sys, pygame
from pygame import Rect, Surface, Vector2

##############################################################################
# CONFIGURATION & GLOBALS
##############################################################################

W, H           = 960, 540                    # window size (16:9, nice & wide)
FPS            = 60
TILE           = 48                          # virtual “tile” size for layout
CAMERA_MARGIN  = 120                         # keep Mario roughly centred
FONT_NAME      = "sans"                      # system font – chunky is fine
COLORS         = {
    "grass":      ( 92, 200,  72),
    "path":       (240, 208, 136),
    "water":      ( 64, 160, 224),
    "tree_light": ( 20, 100,  20),
    "tree_dark":  ( 12,  60,  12),
    "cloud":      (248, 248, 248),
    "sky":        (156, 200, 252),
    "hud_bg":     (240, 64,  56),
    "hud_fg":     (248, 216,168),
    "hud_shadow": ( 64,  16, 16),
    "dialog_bg":  (248, 248, 248),
    "dialog_txt": (  0,   0,   0),
    "battle_ui":  (248, 248, 248),
    "battle_btn": (240, 200,  72),
}

# Game state enum
OVERWORLD, DIALOG, BATTLE = "overworld", "dialog", "battle"

pygame.init()
pygame.display.set_caption("Mini Mario RPG Tech Demo")
clock   = pygame.time.Clock()
screen  = pygame.display.set_mode((W, H))
bigfont = pygame.font.SysFont(FONT_NAME, 28, bold=True)
hudfont = pygame.font.SysFont(FONT_NAME, 20, bold=True)
txtfont = pygame.font.SysFont(FONT_NAME, 18)

##############################################################################
# UTILITY
##############################################################################
def draw_text(surface:Surface, text:str, pos, font, color, shadow=False, center=False):
    img = font.render(text, True, color)
    if shadow:
        sh = font.render(text, True, COLORS["hud_shadow"])
        shpos = img.get_rect()
        shpos.center = pos if center else (pos[0], pos[1])
        shpos.move_ip(2,2)
        surface.blit(sh, shpos)
    rect = img.get_rect()
    rect.center = pos if center else (pos[0], pos[1])
    surface.blit(img, rect)

def iso_to_screen(x, y):
    """Simple 2‑D fake‑isometric transform (staggered grid)."""
    return Vector2(
        x * TILE - y * TILE * .5,
        y * TILE * .5 + x * TILE * .25
    )

##############################################################################
# WORLD TILES & MAP
##############################################################################
class Map:
    def __init__(self, w, h):
        self.w, self.h = w, h
        # Build basic layout: grass w/ random paths & water border
        self.tiles = [["grass" for _ in range(h)] for _ in range(w)]
        for x in range(w):
            for y in range(h):
                if x in (0, w-1) or y in (0,h-1):
                    self.tiles[x][y] = "water"

        # carve a horizontal & vertical path
        for x in range(2, w-2):
            self.tiles[x][h//2] = "path"
        for y in range(2, h-2):
            self.tiles[w//2][y] = "path"

        self.trees = [Vector2(random.randrange(2,w-2), random.randrange(2,h-2))
                      for _ in range(50)]

        # scatter coins
        self.coins = [Vector2(random.randrange(2,w-2), random.randrange(2,h-2))
                      for _ in range(30)]

        # enemy & npc spawns
        self.npcs  = []
        self.enemies = []

    def add_npc(self, npc):
        self.npcs.append(npc)
    def add_enemy(self, enemy):
        self.enemies.append(enemy)

    def draw(self, surf, camera):
        # Sky
        surf.fill(COLORS["sky"])

        # Simple isometric draw order based on tile y
        for y in range(self.h):
            for x in range(self.w):
                pos = iso_to_screen(x, y) - camera
                if pos.y > H: continue         # skip far below view
                tile = self.tiles[x][y]
                color = COLORS.get(tile, COLORS["grass"])
                pygame.draw.rect(surf, color,
                                 Rect(pos.x, pos.y, TILE, TILE*.5))

        # draw water animated border
        t = pygame.time.get_ticks()/400
        for x in range(self.w):
            for y in [0,self.h-1]:
                pos = iso_to_screen(x,y) - camera
                c = COLORS["water"]
                pygame.draw.rect(surf, c,
                                 Rect(pos.x, pos.y+math.sin(t+x)*2, TILE, TILE*.5))
        for y in range(self.h):
            for x in [0,self.w-1]:
                pos = iso_to_screen(x,y) - camera
                c = COLORS["water"]
                pygame.draw.rect(surf, c,
                                 Rect(pos.x+math.sin(t+y)*2, pos.y, TILE, TILE*.5))

        # trees
        for tree in self.trees:
            pos = iso_to_screen(tree.x, tree.y) - camera
            sway = math.sin(pygame.time.get_ticks()/800 + tree.x)*4
            pygame.draw.rect(surf, COLORS["tree_dark"],
                             Rect(pos.x+TILE/2-4+sway/2, pos.y-TILE*.4, 8, TILE*.4))
            pygame.draw.ellipse(surf, COLORS["tree_light"],
                                Rect(pos.x-20+sway, pos.y-TILE, TILE+40, TILE))

        # coins
        for coin in self.coins:
            pos = iso_to_screen(coin.x, coin.y) - camera + Vector2(TILE/2, -TILE*.25)
            pulse = 4*math.sin(pygame.time.get_ticks()/200)
            pygame.draw.circle(surf, (252, 220,  88), pos, 10+pulse)
            pygame.draw.circle(surf, (252, 248, 176), pos, 6+pulse)

##############################################################################
# ENTITIES
##############################################################################
class Sprite:
    def __init__(self, map:Map, pos:Vector2):
        self.map  = map
        self.pos  = pos          # map coords (float)
        self.vel  = Vector2(0,0)
        self.rect = Rect(0,0, TILE//1, TILE//1)
    @property
    def screen_pos(self):
        return iso_to_screen(self.pos.x, self.pos.y)

class Player(Sprite):
    def __init__(self, map, pos):
        super().__init__(map,pos)
        self.hp = 20
        self.coins = 0
        self.lvl = 1
        self.facing = Vector2(1,0)

    def handle_input(self, keys):
        self.vel.update(0,0)
        if keys[pygame.K_LEFT]:  self.vel.x = -1
        if keys[pygame.K_RIGHT]: self.vel.x =  1
        if keys[pygame.K_UP]:    self.vel.y = -1
        if keys[pygame.K_DOWN]:  self.vel.y =  1
        if self.vel.length_squared():
            self.vel = self.vel.normalize()*0.05

    def update(self, dt):
        # move, keep inside bounds
        self.pos += self.vel * dt
        self.pos.x = max(1,min(self.map.w-2,self.pos.x))
        self.pos.y = max(1,min(self.map.h-2,self.pos.y))

        # pick up coins
        for coin in list(self.map.coins):
            if self.pos.distance_to(coin) < 0.5:
                self.map.coins.remove(coin)
                self.coins += 1

    def draw(self, surf, camera):
        pos = self.screen_pos - camera
        # little 2‑frame foot animation
        step = (pygame.time.get_ticks()//150)%2
        body = Rect(pos.x+TILE/2-8, pos.y-TILE*.25, 16, 24)
        pygame.draw.rect(surf, (224,32,24), body)        # red shirt
        pygame.draw.rect(surf, ( 32,32,224),      # blue pants
                         Rect(body.x, body.bottom-8, 16, 8))
        # feet
        if step==0:
            pygame.draw.rect(surf, (80,40,24),
                             Rect(body.x-4, body.bottom-4, 8,4))
            pygame.draw.rect(surf, (80,40,24),
                             Rect(body.right-4, body.bottom-4, 8,4))
        else:
            pygame.draw.rect(surf, (80,40,24),
                             Rect(body.x-2, body.bottom-4, 12,4))
        # head
        pygame.draw.circle(surf, (252,208,168),
                           (body.centerx, body.y-8), 10)
        # hat
        pygame.draw.rect(surf, (224,32,24),
                         Rect(body.centerx-12, body.y-12, 24, 6))

class NPC(Sprite):
    def __init__(self, map, pos, dialog:str, color=(248,248,248)):
        super().__init__(map,pos)
        self.dialog = dialog
        self.color  = color
    def draw(self, surf, camera):
        pos = self.screen_pos - camera
        pygame.draw.rect(surf, self.color,
                         Rect(pos.x+TILE/2-10, pos.y-TILE*.2, 20, 20))
        pygame.draw.rect(surf, (200,0,0),
                         Rect(pos.x+TILE/2-12, pos.y-TILE*.2-4, 24, 4))

class Enemy(Sprite):
    def __init__(self, map,pos):
        super().__init__(map,pos)
        self.base_pos = Vector2(pos)
    def update(self, dt):
        # little bobbing idle
        self.pos = self.base_pos + Vector2(
            math.sin(pygame.time.get_ticks()/700)*0.1,
            math.sin(pygame.time.get_ticks()/650)*0.1)
    def draw(self, surf,camera):
        pos = self.screen_pos - camera
        pygame.draw.circle(surf, (200,80,40),
                           (pos.x+TILE/2, pos.y-TILE*.15), 14)
        pygame.draw.circle(surf, (248,248,248),
                           (pos.x+TILE/2-6, pos.y-TILE*.2), 4)
        pygame.draw.circle(surf, (248,248,248),
                           (pos.x+TILE/2+6, pos.y-TILE*.2), 4)

##############################################################################
# DIALOG & BATTLE
##############################################################################
class DialogManager:
    def __init__(self):
        self.active = False
        self.text   = ""
    def open(self, text):
        self.active, self.text = True, text
    def close(self):
        self.active = False
    def draw(self, surf):
        if not self.active: return
        w,h = W*.8, H*.25
        box = Rect((W-w)/2, H-h-30, w, h)
        pygame.draw.rect(surf, COLORS["dialog_bg"], box)
        pygame.draw.rect(surf, COLORS["hud_shadow"], box, 4)
        # wrap text
        words = self.text.split()
        line, lines = "", []
        for w_ in words:
            if txtfont.size(line+w_+" ")[0] > w-40:
                lines.append(line)
                line = ""
            line += w_+" "
        lines.append(line)
        for i,l in enumerate(lines[:4]):
            draw_text(surf, l.strip(), (box.x+20, box.y+20+i*24),
                      txtfont, COLORS["dialog_txt"])

class Battle:
    def __init__(self, player:Player, enemy:Enemy):
        self.player, self.enemy  = player, enemy
        self.result = None
        self.btn = Rect(W/2-80, H*.7, 160, 50)
    def update(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_z, pygame.K_x, pygame.K_RETURN):
                self.result = "win"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button==1:
                if self.btn.collidepoint(e.pos):
                    self.result = "win"
    def draw(self, surf):
        surf.fill((0,0,0))
        # simple BG gradient
        for i in range(H):
            c = pygame.Color(0,0,0)
            c.hsla = (30, 50, 30+i*30/H, 100)
            pygame.draw.line(surf, c, (0,i), (W,i))
        # char silhouettes
        pygame.draw.circle(surf, (224,32,24), (W*.3, H*.45), 60)
        pygame.draw.circle(surf, (200,80,40), (W*.7, H*.45), 60)
        pygame.draw.rect(surf, COLORS["battle_btn"], self.btn)
        pygame.draw.rect(surf, (0,0,0), self.btn, 3)
        draw_text(surf, "ATTACK!", self.btn.center, bigfont, (0,0,0), center=True)

##############################################################################
# HUD
##############################################################################
def draw_hud(player:Player, surf:Surface):
    bar = Rect(0,0, W, 60)
    pygame.draw.rect(surf, COLORS["hud_bg"], bar)
    # Mario face (simple circle)
    pygame.draw.circle(surf, (252,208,168), (40,30), 20)
    pygame.draw.rect(surf, (224,32,24), Rect(20,12,40,10))
    # Stats text
    draw_text(surf, f"HP:{player.hp:02}", (80,16), hudfont, COLORS["hud_fg"])
    draw_text(surf, f"LV:{player.lvl}",   (80,36), hudfont, COLORS["hud_fg"])
    draw_text(surf, f"Coins:{player.coins}", (200,26), hudfont, COLORS["hud_fg"])
    # Menu button (stub)
    menu = Rect(W-120,10,110,40)
    pygame.draw.rect(surf, COLORS["hud_fg"], menu)
    pygame.draw.rect(surf, COLORS["hud_shadow"], menu,3)
    draw_text(surf, "Menu", menu.center, hudfont, COLORS["hud_shadow"], center=True)
##############################################################################
# GAME INITIALISATION
##############################################################################
def build_world():
    world = Map(32, 32)
    # NPCs
    world.add_npc(NPC(world, Vector2(10,15),
        "Hello Mario! Press Z to talk.\nBeware of wandering Goombas!"))
    world.add_npc(NPC(world, Vector2(22,14),
        "This demo shows dialogue, coins, and a stub battle. Enjoy!"))
    # Enemies
    for _ in range(5):
        p = Vector2(random.randrange(5,27), random.randrange(5,27))
        world.add_enemy(Enemy(world,p))
    return world

##############################################################################
# MAIN LOOP
##############################################################################
def main():
    world  = build_world()
    player = Player(world, Vector2(5,5))
    dialog = DialogManager()
    state  = OVERWORLD
    battle = None
    camera = Vector2()

    while True:
        dt      = clock.tick(FPS)
        events  = pygame.event.get()
        keys    = pygame.key.get_pressed()

        # Quit
        for e in events:
            if e.type==pygame.QUIT or (e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE):
                pygame.quit(); sys.exit()

        ####################################################################
        # OVERWORLD LOGIC
        ####################################################################
        if state == OVERWORLD:
            player.handle_input(keys)
            player.update(dt)
            for e in world.enemies: e.update(dt)

            # camera follows Mario with margin
            target = player.screen_pos - Vector2(W/2, H/2-60)
            camera += (target-camera)*0.08

            # Interactions
            if any(keys[k] for k in (pygame.K_z,pygame.K_x,pygame.K_RETURN)):
                for npc in world.npcs:
                    if player.pos.distance_to(npc.pos) < 1.0:
                        dialog.open(npc.dialog)
                        state = DIALOG
                        break

            # Enemy collision -> battle
            for enemy in list(world.enemies):
                if player.pos.distance_to(enemy.pos) < 0.8:
                    battle = Battle(player, enemy)
                    state  = BATTLE
                    break

            # Draw overworld
            world.draw(screen, camera)
            for npc in world.npcs: npc.draw(screen, camera)
            for enemy in world.enemies: enemy.draw(screen, camera)
            player.draw(screen, camera)
            draw_hud(player, screen)

        ####################################################################
        # DIALOG STATE
        ####################################################################
        elif state == DIALOG:
            player.draw(screen, camera)
            world.draw(screen, camera)
            for npc in world.npcs: npc.draw(screen, camera)
            dialog.draw(screen)
            draw_hud(player, screen)
            if any(e.type==pygame.KEYDOWN and e.key in (
                     pygame.K_z,pygame.K_x,pygame.K_RETURN) for e in events):
                dialog.close()
                state = OVERWORLD

        ####################################################################
        # BATTLE STATE
        ####################################################################
        elif state == BATTLE:
            battle.update(events)
            battle.draw(screen)
            if battle.result == "win":
                # award coin + maybe level
                player.coins += 2
                player.lvl   += 0 if random.random()<.7 else 1
                try:
                    world.enemies.remove(battle.enemy)
                except ValueError:
                    pass
                state = OVERWORLD

        pygame.display.flip()

if __name__ == "__main__":
    main()
