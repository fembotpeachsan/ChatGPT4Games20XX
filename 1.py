from ursina import *
from dataclasses import dataclass
from random import random, randint, choice, uniform
import math

# Constants
W, H = 1280, 720
WINDOW_TITLE = "PAPER ADVENTURE"
TILE = 1.0
PLAYER_SPEED = 4.2
ENEMY_SPEED_MIN, ENEMY_SPEED_MAX = 1.2, 2.0

# Color helper function
def RGB(r, g, b): return color.rgb(r, g, b)

# Color palette
BLACK = RGB(10, 12, 14)
WHITE = RGB(240, 240, 245)
GRAY = RGB(60, 64, 70)
SILVER = RGB(160, 168, 180)
RED = RGB(220, 60, 60)
GREEN = RGB(60, 220, 130)
CYAN = RGB(64, 200, 240)
YELLOW = RGB(240, 220, 80)
ORANGE = RGB(252, 150, 80)
PINK = RGB(255, 120, 170)
VIOLET = RGB(170, 120, 255)
PURPLE = RGB(150, 80, 200)
BROWN = RGB(150, 100, 60)

# Paper texture for the papery feel
paper_texture = load_texture('white_cube')

@dataclass
class Stats:
    name: str = "Shellby"
    max_hp: int = 10
    hp: int = 10
    max_fp: int = 5
    fp: int = 5
    atk: int = 1
    defense: int = 0
    level: int = 1
    xp: int = 0
    coins: int = 0

@dataclass
class Move:
    name: str
    fp_cost: int
    type: str
    base: int
    desc: str = ""
    press_window: float = 0.12
    mash_time: float = 1.4

JUMP = Move("Jump", fp_cost=0, type="timed", base=2, desc="Press Z when the marker hits center.")
SHELL_DASH = Move("Shell Dash", fp_cost=1, type="mash", base=1, desc="Mash Z to power up.")
HAMMER_SMASH = Move("Hammer Smash", fp_cost=2, type="timed", base=3, desc="Press Z when the marker hits center.")
FIRE_FLOWER = Move("Fire Flower", fp_cost=3, type="mash", base=4, desc="Mash Z to build power.")

ENEMIES = [
    dict(kind="Goombean", max_hp=8, atk=2, defense=0, xp=3, coins=2, hue=ORANGE),
    dict(kind="Spikeling", max_hp=10, atk=3, defense=1, xp=5, coins=3, hue=YELLOW),
    dict(kind="Shybyte", max_hp=6, atk=1, defense=0, xp=2, coins=1, hue=PINK),
    dict(kind="Bob-Omb", max_hp=12, atk=4, defense=2, xp=8, coins=5, hue=BLACK),
]

# Create paper-like models
def create_paper_character(color, scale=Vec3(1, 1, 0.1)):
    """Create a paper-like character model"""
    body = Entity(
        model='quad',
        color=color,
        texture=paper_texture,
        scale=scale,
        double_sided=True
    )
    return body

def create_paper_enemy(color, scale=Vec3(1, 1, 0.1)):
    """Create a paper-like enemy model"""
    body = Entity(
        model='quad',
        color=color,
        texture=paper_texture,
        scale=scale,
        double_sided=True
    )
    return body

def create_paper_obstacle(color, scale=Vec3(1, 1, 0.1)):
    """Create a paper-like obstacle"""
    return Entity(
        model='quad',
        color=color,
        texture=paper_texture,
        scale=scale,
        double_sided=True
    )

def create_tree(position):
    """Create a paper-style tree"""
    trunk = Entity(
        model='quad',
        color=BROWN,
        texture=paper_texture,
        scale=(0.5, 2, 0.1),
        position=position,
        double_sided=True
    )
    leaves = Entity(
        model='quad',
        color=GREEN,
        texture=paper_texture,
        scale=(2, 2, 0.1),
        position=position + (0, 1.5, 0),
        double_sided=True
    )
    return (trunk, leaves)

class Scene:
    def __init__(self, game): 
        self.game = game
        self.root = Entity(enabled=False)
        self.ui_root = Entity(parent=camera.ui, enabled=False)
        
    def enter(self, **kwargs):
        self.root.enable()
        self.ui_root.enable()
        
    def exit(self):
        destroy(self.root)
        destroy(self.ui_root)
        
    def input(self, key): pass
    def update(self): pass

class Game:
    def __init__(self):
        self.vibes = True
        self.player = Stats()
        self.scene_stack = []
        self.push(TitleScene(self))

    def push(self, scene, **kwargs):
        self.scene_stack.append(scene)
        scene.enter(**kwargs)

    def pop(self):
        if self.scene_stack:
            s = self.scene_stack.pop()
            s.exit()

    def switch(self, scene, **kwargs):
        self.pop()
        self.push(scene, **kwargs)

    @property
    def cur(self):
        return self.scene_stack[-1] if self.scene_stack else None

    def route_input(self, key):
        if key == 'f1 down':
            self.vibes = not self.vibes
        if key == 'escape':
            application.quit()
        if self.cur:
            self.cur.input(key)

    def route_update(self):
        if self.cur:
            self.cur.update()

class TitleScene(Scene):
    def enter(self, **kwargs):
        super().enter(**kwargs)
        self.t = 0
        
        # Paper-style background
        self.bg = Entity(
            parent=self.ui_root, 
            model='quad', 
            scale=(2, 2), 
            color=color.rgb(16, 18, 24),
            texture=paper_texture
        )
        
        # Paper-style title
        self.logo = Text(
            parent=self.ui_root, 
            text="PAPER ADVENTURE", 
            origin=(0, 0), 
            position=(0, .15), 
            scale=2, 
            color=CYAN,
            background=True,
            background_color=color.rgb(30, 30, 40, 200)
        )
        
        self.blurb = Text(
            parent=self.ui_root, 
            text="Ursina • Paper Mario-style • Action Commands",
            position=(0, .06), 
            origin=(0, 0), 
            color=SILVER
        )
        
        self.prompt = Text(
            parent=self.ui_root, 
            text="Press ENTER or Z",
            position=(0, -.02), 
            origin=(0, 0), 
            color=WHITE
        )
        
        self.footer = Text(
            parent=self.ui_root, 
            text="F1: Vibes Mode | ESC: Quit",
            position=(0, -.45), 
            origin=(0, 0), 
            color=GRAY, 
            scale=.9
        )
        
        # Create paper-style characters in the background
        self.paper_chars = []
        positions = [(-0.6, 0.2), (0.6, 0.2), (0, -0.2)]
        colors = [CYAN, YELLOW, PINK]
        
        for i, (x, y) in enumerate(positions):
            char = Entity(
                parent=self.ui_root,
                model='quad',
                color=colors[i],
                texture=paper_texture,
                position=(x, y),
                scale=(0.3, 0.5),
                rotation_z=randint(-10, 10),
                double_sided=True
            )
            self.paper_chars.append(char)

    def input(self, key):
        if key in ('enter', 'z'):
            self.game.switch(MapScene(self.game))

    def update(self):
        self.t += time.dt
        self.prompt.color = WHITE if int(self.t * 2) % 2 == 0 else SILVER
        
        # Animate paper characters
        if self.game.vibes:
            self.logo.y = .15 + math.sin(time.time() * 2) * .005
            for i, char in enumerate(self.paper_chars):
                char.rotation_z = math.sin(time.time() * 2 + i) * 10

class MapScene(Scene):
    def enter(self, **kwargs):
        super().enter(**kwargs)
        camera.orthographic = False
        camera.position = (0, 12, -0.01)
        camera.rotation_x = 75
        window.title = WINDOW_TITLE

        self.cols = 18
        self.rows = 12
        
        # Create paper-style terrain
        self.floor = Entity(
            parent=self.root, 
            model='plane', 
            collider=None,
            scale=(self.cols, 1, self.rows), 
            color=color.rgb(22, 24, 30), 
            texture=paper_texture
        )
        
        # Create paper-style obstacles and trees
        self.tiles = []
        self.trees = []
        
        for y in range(self.rows):
            for x in range(self.cols):
                if x == 0 or x == self.cols - 1 or y == 0 or y == self.rows - 1:
                    # Border walls
                    e = create_paper_obstacle(
                        color=color.rgb(30, 38, 44),
                        scale=(1, 1, 0.1)
                    )
                    e.position = (x - self.cols/2 + .5, .5, y - self.rows/2 + .5)
                    e.parent = self.root
                    self.tiles.append(e)
                elif random() < 0.1:  # Trees
                    tree_parts = create_tree((x - self.cols/2 + .5, 0, y - self.rows/2 + .5))
                    for part in tree_parts:
                        part.parent = self.root
                        self.trees.append(part)
                elif random() < 0.14:  # Random obstacles
                    e = create_paper_obstacle(
                        color=color.rgb(40, 50, 60),
                        scale=(1, 1, 0.1)
                    )
                    e.position = (x - self.cols/2 + .5, .5, y - self.rows/2 + .5)
                    e.parent = self.root
                    self.tiles.append(e)

        # Create player
        px, py = self._empty_cell()
        self.player_ent = create_paper_character(
            color=CYAN,
            scale=Vec3(0.8, 0.8, 0.1)
        )
        self.player_ent.collider = 'box'
        self.player_ent.position = self._cell_to_world(px, py, y=.5)
        self.player_ent.parent = self.root
        
        # Add a little hat to make it more paper-like
        self.player_hat = Entity(
            parent=self.player_ent,
            model='quad',
            color=RED,
            texture=paper_texture,
            scale=(0.8, 0.2, 0.1),
            position=(0, 0.5, -0.1),
            double_sided=True
        )
        
        self.player_vel = Vec3(0, 0, 0)
        
        self.msg = Text(
            parent=self.ui_root, 
            text="Bump an enemy to start a battle.",
            position=(-.5, -.47), 
            origin=(-.5, -.5), 
            color=GRAY, 
            scale=.9
        )
        
        # Create paper-style enemies
        self.enemies = []
        for _ in range(4):
            ex, ey = self._empty_cell()
            eproto = choice(ENEMIES).copy()
            
            enemy_ent = create_paper_enemy(
                color=eproto["hue"],
                scale=Vec3(0.8, 0.8, 0.1)
            )
            enemy_ent.collider = 'box'
            enemy_ent.position = self._cell_to_world(ex, ey, y=.5)
            enemy_ent.parent = self.root
            enemy_ent.rotation_y = uniform(0, 360)
            
            # Enemy features
            if eproto["kind"] == "Bob-Omb":
                fuse = Entity(
                    parent=enemy_ent,
                    model='quad',
                    color=YELLOW,
                    texture=paper_texture,
                    scale=(0.2, 0.4, 0.1),
                    position=(0, 0.6, -0.1),
                    rotation_z=20,
                    double_sided=True
                )
            
            e = {
                "ent": enemy_ent,
                "stats": eproto,
                "dir": uniform(0, math.tau),
                "spd": uniform(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX),
                "alive": True
            }
            self.enemies.append(e)

    def _empty_cell(self):
        while True:
            x = randint(1, self.cols - 2)
            y = randint(1, self.rows - 2)
            return x, y

    def _cell_to_world(self, cx, cy, y=0):
        return Vec3(cx - self.cols/2 + .5, y, cy - self.rows/2 + .5)

    def input(self, key):
        pass

    def _try_move(self, ent, dx, dz):
        ent.x += dx
        if ent.intersects().hit:
            ent.x -= dx
        ent.z += dz
        if ent.intersects().hit:
            ent.z -= dz

    def update(self):
        ax = (held_keys['d'] or held_keys['right arrow']) - (held_keys['a'] or held_keys['left arrow'])
        az = (held_keys['s'] or held_keys['down arrow']) - (held_keys['w'] or held_keys['up arrow'])
        v = Vec3(ax, 0, az)
        if v.length() > 0:
            v = v.normalized() * PLAYER_SPEED * time.dt
            self._try_move(self.player_ent, v.x, v.z)
            
            # Add paper-like bobbing animation
            if self.game.vibes:
                self.player_ent.y = .5 + math.sin(time.time() * 10) * 0.05
                self.player_ent.rotation_z = math.sin(time.time() * 5) * 5
            else:
                self.player_ent.y = .5

        for e in self.enemies:
            if not e["alive"] or not e["ent"].enabled:
                continue
                
            if random() < 0.02:
                e["dir"] += uniform(-0.8, 0.8)
                
            dx = math.cos(e["dir"]) * e["spd"] * time.dt
            dz = math.sin(e["dir"]) * e["spd"] * time.dt
            
            before = e["ent"].position
            self._try_move(e["ent"], dx, dz)
            
            if (e["ent"].position - before).length() < .001:
                e["dir"] += math.pi/2 + uniform(-.5, .5)
                
            # Add paper-like bobbing animation for enemies
            if self.game.vibes:
                e["ent"].y = .5 + math.sin(time.time() * 8 + e["dir"]) * 0.04
                e["ent"].rotation_z = math.sin(time.time() * 4 + e["dir"]) * 4

        for e in self.enemies:
            if not e["alive"]:
                continue
                
            if distance_xz(self.player_ent.position, e["ent"].position) < .6:
                e["alive"] = False
                e["ent"].disable()
                estats = dict(
                    name=e["stats"]["kind"], 
                    max_hp=e["stats"]["max_hp"], 
                    hp=e["stats"]["max_hp"],
                    atk=e["stats"]["atk"], 
                    defense=e["stats"]["defense"], 
                    xp=e["stats"]["xp"],
                    coins=e["stats"]["coins"], 
                    hue=e["stats"]["hue"]
                )
                self.game.push(BattleScene(self.game), enemy=estats, return_to=self)
                break

        if self.game.vibes:
            self.floor.y = math.sin(time.time() * 1.5) * .02
        else:
            self.floor.y = 0

def distance_xz(a, b):
    da = Vec2(a.x, a.z)
    db = Vec2(b.x, b.z)
    return (da - db).length()

class BattleScene(Scene):
    def enter(self, **kwargs):
        super().enter(**kwargs)
        self.enemy = kwargs.get("enemy")
        self.return_to = kwargs.get("return_to", None)

        self.state = "intro"
        self.t = 0
        self.menu_i = 0
        self.submenu_i = 0
        self.message = "A wild foe approaches!"
        self.guard_window = 0
        self.guard_success = False
        self.pending_damage = 0
        self.last_grade = None
        self.ac_pressed = False

        self.commands = ["Attack", "Skill", "Item", "Run"]
        self.skills = [SHELL_DASH, HAMMER_SMASH, FIRE_FLOWER]
        self.selected_move = None

        # Paper-style background
        self.bg = Entity(
            parent=self.ui_root, 
            model='quad', 
            color=color.rgb(22, 22, 28), 
            scale=(2, 2),
            texture=paper_texture
        )
        
        # Paper-style stage
        self.stage = Entity(
            parent=self.ui_root, 
            model='quad', 
            color=color.rgb(28, 32, 40),
            position=(0, -.15), 
            scale=(2, .7),
            texture=paper_texture
        )
        
        self.stage_border = Entity(
            parent=self.ui_root, 
            model='quad', 
            color=color.rgb(36, 40, 52),
            position=(0, -.15), 
            scale=(2, .7), 
            wireframe=True
        )

        # Enemy panel
        self.enemy_box = Entity(
            parent=self.ui_root, 
            model='quad', 
            scale=(.42, .26),
            color=color.rgb(34, 38, 46), 
            position=(.38, .15),
            texture=paper_texture
        )
        
        self.enemy_box_line = Entity(
            parent=self.enemy_box, 
            model='quad', 
            color=self.enemy["hue"], 
            scale=(1, 1), 
            wireframe=True
        )
        
        # Create 3D paper enemy model on the stage
        self.enemy_model = create_paper_enemy(
            color=self.enemy["hue"],
            scale=Vec3(1.5, 1.5, 0.1)
        )
        self.enemy_model.parent = self.root
        self.enemy_model.position = (2, 1.5, 0)
        self.enemy_model.rotation_y = 180
        
        # Enemy features
        if self.enemy["name"] == "Bob-Omb":
            fuse = Entity(
                parent=self.enemy_model,
                model='quad',
                color=YELLOW,
                texture=paper_texture,
                scale=(0.2, 0.4, 0.1),
                position=(0, 0.8, -0.1),
                rotation_z=20,
                double_sided=True
            )
        
        self.enemy_name = Text(
            parent=self.enemy_box, 
            text=self.enemy.get("name", "??"), 
            position=(0, .35), 
            origin=(0, 0), 
            color=WHITE, 
            scale=.9
        )
        
        self.enemy_hp_bar_bg = Entity(
            parent=self.enemy_box, 
            model='quad', 
            color=color.rgb(40, 48, 56), 
            position=(0, -.35), 
            scale=(.8, .06)
        )
        
        self.enemy_hp_fill = Entity(
            parent=self.enemy_box, 
            model='quad', 
            color=ORANGE, 
            position=(-.4, -.35), 
            origin=(-.5, 0), 
            scale=(.8, .06)
        )

        # Player panel
        self.player_box = Entity(
            parent=self.ui_root, 
            model='quad', 
            scale=(.42, .26),
            color=color.rgb(34, 38, 46), 
            position=(-.38, .15),
            texture=paper_texture
        )
        
        self.player_box_line = Entity(
            parent=self.player_box, 
            model='quad', 
            color=CYAN, 
            scale=(1, 1), 
            wireframe=True
        )
        
        # Create 3D paper player model on the stage
        self.player_model = create_paper_character(
            color=CYAN,
            scale=Vec3(1.5, 1.5, 0.1)
        )
        self.player_model.parent = self.root
        self.player_model.position = (-2, 1.5, 0)
        
        # Player hat
        self.player_hat = Entity(
            parent=self.player_model,
            model='quad',
            color=RED,
            texture=paper_texture,
            scale=(0.8, 0.2, 0.1),
            position=(0, 0.8, -0.1),
            double_sided=True
        )
        
        self.player_name = Text(
            parent=self.player_box, 
            text=self.game.player.name, 
            position=(0, .35), 
            origin=(0, 0), 
            color=WHITE, 
            scale=.9
        )
        
        self.player_hp_bar_bg = Entity(
            parent=self.player_box, 
            model='quad', 
            color=color.rgb(40, 48, 56), 
            position=(0, -.35), 
            scale=(.8, .06)
        )
        
        self.player_hp_fill = Entity(
            parent=self.player_box, 
            model='quad', 
            color=GREEN, 
            position=(-.4, -.35), 
            origin=(-.5, 0), 
            scale=(.8, .06)
        )

        # Menu panel
        self.menu_panel = Entity(
            parent=self.ui_root, 
            model='quad', 
            scale=(.9, .2), 
            position=(0, -.38), 
            color=color.rgb(26, 30, 38),
            texture=paper_texture
        )
        
        self.menu_border = Entity(
            parent=self.menu_panel, 
            model='quad', 
            scale=(1, 1), 
            wireframe=True, 
            color=SILVER
        )
        
        self.menu_texts = []
        for i, name in enumerate(self.commands):
            t = Text(
                parent=self.menu_panel, 
                text=name, 
                position=(-.42 + i * .3, .02), 
                origin=(-.5, 0), 
                color=WHITE, 
                scale=1
            )
            self.menu_texts.append(t)
            
        self.fp_text = Text(
            parent=self.menu_panel, 
            text="", 
            position=(.32, .02), 
            origin=(-.5, 0), 
            color=SILVER, 
            scale=.9
        )
        
        self.msg_text = Text(
            parent=self.menu_panel, 
            text=self.message, 
            position=(-.42, -.06), 
            origin=(-.5, 0), 
            color=WHITE, 
            scale=.9
        )

        self.ac_bar = None
        self.ac_marker = None
        self.ac_sweet = None
        self.mash_count = 0

        self._refresh_bars()

    def _refresh_bars(self):
        p = self.game.player
        e = self.enemy
        pw = .8 * max(0, min(1, p.hp / max(1, p.max_hp)))
        ew = .8 * max(0, min(1, e["hp"] / max(1, e["max_hp"])))
        self.player_hp_fill.scale_x = pw
        self.enemy_hp_fill.scale_x = ew
        self.fp_text.text = f"FP {p.fp}/{p.max_fp}"

    def input(self, key):
        if self.state in ("player_menu", "choose_skill"):
            if key in ('right arrow', 'd'):
                if self.state == "choose_skill": 
                    self.submenu_i = (self.submenu_i + 1) % max(1, len(self.skills))
                else: 
                    self.menu_i = (self.menu_i + 1) % len(self.commands)
            elif key in ('left arrow', 'a'):
                if self.state == "choose_skill": 
                    self.submenu_i = (self.submenu_i - 1) % max(1, len(self.skills))
                else: 
                    self.menu_i = (self.menu_i - 1) % len(self.commands)
            elif key in ('enter', 'z'):
                self.menu_confirm()
            elif key in ('x', 'backspace'):
                self.state = "player_menu"
                self.selected_move = None
        elif self.state and self.state.startswith("ac_"):
            if key == 'z':
                self.ac_pressed = True

    def menu_confirm(self):
        c = self.commands[self.menu_i]
        if c == "Attack":
            self.selected_move = JUMP
            self.start_action_command(self.selected_move)
        elif c == "Skill":
            if not self.skills:
                self._say("No skills yet.")
                return
            move = self.skills[self.submenu_i]
            if self.game.player.fp < move.fp_cost:
                self._say("Not enough FP!")
                return
            self.game.player.fp -= move.fp_cost
            self.selected_move = move
            self.start_action_command(move)
        elif c == "Item":
            if getattr(self.game.player, "_heart_leafs", 3) <= 0:
                self._say("Out of Heart Leafs!")
            else:
                self.game.player._heart_leafs = getattr(self.game.player, "_heart_leafs", 3) - 1
                heal = 7
                self.game.player.hp = min(self.game.player.max_hp, self.game.player.hp + heal)
                self._say(f"Used Heart Leaf! +{heal} HP")
                self.state = "enemy_turn"
                self.t = 0
                self._refresh_bars()
        elif c == "Run":
            if random() < 0.45:
                self._say("You got away!")
                self.finish_to_map(victory=False, fled=True)
            else:
                self._say("Couldn't run!")
                self.state = "enemy_turn"
                self.t = 0

    def start_action_command(self, move: Move):
        self.ac_pressed = False
        self.last_grade = None
        
        if self.ac_bar: 
            destroy(self.ac_bar)
            self.ac_bar = None
            
        if move.type == "timed":
            self.state = "ac_timed"
            self.t = 0
            self.ac_pos = 0.0
            self.ac_speed = 1.3
            
            self.ac_bar = Entity(
                parent=self.menu_panel, 
                model='quad', 
                color=color.rgb(30, 34, 44),
                position=(-.02, .02), 
                scale=(.36, .035)
            )
            
            self.ac_sweet = Entity(
                parent=self.ac_bar, 
                model='quad', 
                color=color.rgb(54, 58, 72),
                scale=(.36 * .4, .035 * 1.0)
            )
            
            self.ac_marker = Entity(
                parent=self.ac_bar, 
                model='quad', 
                color=YELLOW, 
                scale=(.01, .08)
            )
            
            self.note = Text(
                parent=self.menu_panel, 
                text=move.desc, 
                position=(-.02, .06), 
                origin=(0, 0), 
                color=SILVER, 
                scale=.9
            )
            
            # Animate player model
            self.player_model.animate_position(
                (-1.5, 1.5, 0), 
                duration=0.3, 
                curve=curve.out_quad
            )
            
        elif move.type == "mash":
            self.state = "ac_mash"
            self.t = 0
            self.mash_count = 0
            
            self.ac_bar = Entity(
                parent=self.menu_panel, 
                model='quad', 
                color=color.rgb(30, 34, 44),
                position=(-.02, .02), 
                scale=(.36, .035)
            )
            
            self.ac_fill = Entity(
                parent=self.ac_bar, 
                model='quad', 
                color=CYAN, 
                origin=(-.5, 0),
                position=(-.18, 0), 
                scale=(0, .03)
            )
            
            self.note = Text(
                parent=self.menu_panel, 
                text=move.desc, 
                position=(-.02, .06), 
                origin=(0, 0), 
                color=SILVER, 
                scale=.9
            )
            
            # Animate player model
            self.player_model.animate_position(
                (-1.5, 1.5, 0), 
                duration=0.3, 
                curve=curve.out_quad
            )

    def update(self):
        self.t += time.dt
        
        if self.state == "intro":
            if self.t > .8:
                self.state = "player_menu"
                self.t = 0
                self._say("Choose a command.")
                
        elif self.state == "player_menu":
            pass
            
        elif self.state == "ac_timed":
            self.ac_pos = (self.ac_pos + self.ac_speed * time.dt) % 1.0
            left = -self.ac_bar.scale_x / 2
            x = left + self.ac_bar.scale_x * self.ac_pos
            self.ac_marker.x = x
            
            if self.ac_pressed:
                self.ac_pressed = False
                diff = abs(self.ac_pos - 0.5)
                
                if diff < 0.035:  
                    grade, bonus = ("Great", 2)
                    self.player_model.color = GREEN
                elif diff < 0.11: 
                    grade, bonus = ("Good", 1)
                    self.player_model.color = YELLOW
                else:             
                    grade, bonus = ("OK", 0)
                    self.player_model.color = CYAN
                    
                self.resolve_player_attack(self.selected_move, bonus, grade)
                
                if self.ac_bar: 
                    destroy(self.ac_bar)
                    self.ac_bar = None
                    if hasattr(self, 'ac_marker'): 
                        destroy(self.ac_marker)
                    if hasattr(self, 'ac_sweet'): 
                        destroy(self.ac_sweet)
                    if hasattr(self, 'note'): 
                        destroy(self.note)
                        
                # Return player to position
                self.player_model.animate_position(
                    (-2, 1.5, 0), 
                    duration=0.3, 
                    curve=curve.in_out_quad
                )
                self.player_model.animate_color(
                    CYAN, 
                    duration=0.5
                )
                
        elif self.state == "ac_mash":
            if self.ac_pressed:
                self.ac_pressed = False
                self.mash_count += 1
                # Shake player model when mashing
                if self.game.vibes:
                    self.player_model.rotation_z = randint(-5, 5)
                
            t = min(1, self.t / self.selected_move.mash_time)
            self.ac_fill.scale_x = .36 * t
            
            if self.t >= self.selected_move.mash_time:
                rate = self.mash_count / self.selected_move.mash_time
                
                if rate >= 8:     
                    grade, bonus = ("Great", 3)
                    self.player_model.color = GREEN
                elif rate >= 4.5: 
                    grade, bonus = ("Good", 2)
                    self.player_model.color = YELLOW
                else:             
                    grade, bonus = ("OK", 1)
                    self.player_model.color = CYAN
                    
                self.resolve_player_attack(self.selected_move, bonus, grade)
                
                if self.ac_bar:
                    destroy(self.ac_bar)
                    self.ac_bar = None
                    if hasattr(self, 'ac_fill'): 
                        destroy(self.ac_fill)
                    if hasattr(self, 'note'): 
                        destroy(self.note)
                        
                # Return player to position
                self.player_model.animate_position(
                    (-2, 1.5, 0), 
                    duration=0.3, 
                    curve=curve.in_out_quad
                )
                self.player_model.animate_color(
                    CYAN, 
                    duration=0.5
                )
                
        elif self.state == "enemy_turn":
            if self.guard_window > 0:
                self.guard_window -= time.dt
                
            if self.t < 0.6:
                pass
            elif self.t < 0.85:
                if self.guard_window <= 0:
                    self.guard_window = 0.18
                    self.guard_success = False
                    
                if held_keys['z']:
                    self.guard_success = True
                    self.guard_window = 0
                    self.player_model.color = SILVER
            else:
                if self.pending_damage == 0:
                    dmg = max(0, self.enemy["atk"] - self.game.player.defense)
                    if self.guard_success: 
                        dmg = max(0, dmg - 1)
                        
                    self.game.player.hp = max(0, self.game.player.hp - dmg)
                    self._say(("BLOCK! " if self.guard_success else "") + f"Enemy hits for {dmg}.")
                    self.pending_damage = dmg
                    self._refresh_bars()
                    
                    # Enemy attack animation
                    self.enemy_model.animate_position(
                        (0, 1.5, 0), 
                        duration=0.2, 
                        curve=curve.out_quad
                    )
                    self.enemy_model.animate_position(
                        (2, 1.5, 0), 
                        duration=0.3, 
                        curve=curve.in_out_quad,
                        delay=0.2
                    )
                    
                    # Player hit animation
                    self.player_model.animate_color(
                        RED, 
                        duration=0.1
                    )
                    self.player_model.animate_color(
                        CYAN, 
                        duration=0.3,
                        delay=0.1
                    )
                    
                if self.t >= 1.2:
                    self.pending_damage = 0
                    if self.game.player.hp <= 0:
                        self.state = "defeat"
                        self.t = 0
                        self._say("You fainted...")
                    else:
                        self.state = "player_menu"
                        self.t = 0
                        
        elif self.state == "victory":
            if self.t > 1.2:
                self.finish_to_map(victory=True)
                
        elif self.state == "defeat":
            if self.t > 1.6:
                self.game.player = Stats()
                self.game.switch(TitleScene(self.game))

        blink_on = int(self.t * 4) % 2 == 0
        for i, t in enumerate(self.menu_texts):
            t.color = CYAN if (i == self.menu_i and blink_on) else WHITE

        if self.game.vibes:
            self.bg.scale_y = 2 + math.sin(time.time() * 2) * .02
            self.stage.scale_y = 0.7 + math.sin(time.time() * 3) * .01
        else:
            self.bg.scale_y = 2
            self.stage.scale_y = 0.7

    def _say(self, msg):
        self.message = msg
        self.msg_text.text = msg

    def resolve_player_attack(self, move, bonus, grade):
        self.last_grade = grade
        atk = self.game.player.atk + move.base + bonus
        dmg = max(0, atk - self.enemy["defense"])
        self.enemy["hp"] = max(0, self.enemy["hp"] - dmg)
        self._say(f"{move.name}! {grade}! {dmg} dmg.")
        self.t = 0
        self._refresh_bars()
        
        # Enemy hit animation
        self.enemy_model.animate_color(
            RED, 
            duration=0.1
        )
        self.enemy_model.animate_color(
            self.enemy["hue"], 
            duration=0.3,
            delay=0.1
        )
        
        # Shake enemy
        if self.game.vibes:
            self.enemy_model.animate_rotation_z(
                randint(-10, 10), 
                duration=0.05
            )
            self.enemy_model.animate_rotation_z(
                0, 
                duration=0.05,
                delay=0.05
            )
        
        if self.enemy["hp"] <= 0:
            self.state = "victory"
            self.t = 0
            self._say(f"Victory! +{self.enemy['xp']} XP, +{self.enemy['coins']} coins")
            self.game.player.xp += self.enemy["xp"]
            self.game.player.coins += self.enemy["coins"]
            
            # Victory animation
            self.enemy_model.animate_scale(
                (0.1, 0.1, 0.1), 
                duration=0.8, 
                curve=curve.out_quad
            )
            self.enemy_model.animate_rotation(
                (0, 0, 360), 
                duration=0.8, 
                curve=curve.linear
            )
            
            while self.game.player.xp >= 10:
                self.game.player.xp -= 10
                self.game.player.level += 1
                self.game.player.max_hp += 2
                self.game.player.hp = self.game.player.max_hp
                self.game.player.max_fp += 1
                self.game.player.fp = self.game.player.max_fp
                if self.game.player.level % 2 == 0:
                    self.game.player.atk += 1
                self._say(f"Level Up! Now LV {self.game.player.level}")
                
            self._refresh_bars()
        else:
            self.state = "enemy_turn"
            self.t = 0
            self.guard_window = 0
            self.guard_success = False
            self.pending_damage = 0

    def finish_to_map(self, victory=True, fled=False):
        if self.return_to:
            self.game.pop()
        else:
            self.game.switch(MapScene(self.game))

if __name__ == "__main__":
    app = Ursina(borderless=False)
    window.fullscreen = False
    window.vsync = True
    window.title = WINDOW_TITLE
    window.color = BLACK
    window.size = (W, H)
    window.fps_counter.enabled = True
    window.fps_counter.position = (0.47, 0.45)
    window.fps_counter.scale = 0.7

    game = Game()

    def input(key): 
        game.route_input(key)

    def update(): 
        game.route_update()

    app.run()
