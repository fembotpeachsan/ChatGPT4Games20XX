import pygame, sys, random, numpy as np

# --- Gameboy Chiptune Synth, PYTHON 3.13+ COMPATIBLE, STEREO-SAFE ---
def gb_synth(freq=440, ms=200, v=0.15, wave=0):
    sr = 22050
    t = np.linspace(0, ms/1000, int(sr*ms/1000), False)
    if wave == 0:  # Square
        s = (np.sign(np.sin(2*np.pi*freq*t)) * 32767 * v).astype(np.int16)
    elif wave == 1:  # Pulse 1/4
        s = (np.where((np.sin(2*np.pi*freq*t)>0), 1, -1) * 32767 * v * 0.6).astype(np.int16)
    elif wave == 2:  # Noise
        s = (np.random.uniform(-1,1,len(t)) * 32767 * v * 0.7).astype(np.int16)
    else:  # Triangle
        s = (2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1) * 32767 * v
        s = s.astype(np.int16)
    # === PYTHON 3.13/PYGAME 2.x STEREO PATCH ===
    ch = pygame.mixer.get_init()[2] if pygame.mixer.get_init() else 2
    if s.ndim == 1 and ch == 2:
        s = np.column_stack((s, s))
    snd = pygame.sndarray.make_sound(s)
    snd.play()

def poke_intro_jingle():
    gb_synth(523,80); gb_synth(659,70); gb_synth(784,70); gb_synth(880,120,0.12,1); gb_synth(1046,160,0.12,2)
def battle_cry():
    gb_synth(784,60,0.18,0); gb_synth(523,60,0.16,2); gb_synth(1046,80,0.12,1)
def heal_jingle():
    for f in [659,784,988]: gb_synth(f,60,0.16,0)
def wild_grass_jingle():
    for f in [392,523,392]: gb_synth(f,50,0.16,2)
def badge_jingle():
    for f in [659,784,1046]: gb_synth(f,80,0.17,0)

# --- INIT ---
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2)
WIDTH, HEIGHT, FPS = 384, 336, 60
WHITE, RED, GRAY, BLACK, GREEN = (255,255,255), (224,48,48), (180,180,180), (16,16,16), (48,224,48)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pokémon Lobster Red")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Courier", 18)
fontbig = pygame.font.SysFont("Courier", 24, bold=True)

# --- Mini-Pokedex (For Demo) ---
DEX = [
    {"name":"Bulbasaur","hp":45,"atk":12,"moves":["Tackle","Vine Whip"]},
    {"name":"Charmander","hp":39,"atk":13,"moves":["Scratch","Ember"]},
    {"name":"Squirtle","hp":44,"atk":11,"moves":["Tackle","Bubble"]},
    {"name":"Pidgey","hp":40,"atk":8,"moves":["Gust"]},
    {"name":"Caterpie","hp":35,"atk":7,"moves":["Tackle"]},
    {"name":"Rattata","hp":34,"atk":10,"moves":["Quick Attack"]},
    {"name":"Pikachu","hp":35,"atk":15,"moves":["Thundershock"]},
    {"name":"Zubat","hp":38,"atk":9,"moves":["Bite"]},
    {"name":"Onix","hp":55,"atk":15,"moves":["Rock Throw"]},
    {"name":"Geodude","hp":40,"atk":12,"moves":["Tackle"]},
    {"name":"Eevee","hp":36,"atk":13,"moves":["Quick Attack"]},
    {"name":"Mewtwo","hp":106,"atk":35,"moves":["Psychic","Swift"]},
]
WILD_GRASS = [3,4,5,6,7,8]

# --- World Map (Tiny but Real) ---
WORLD = [
    "########################",
    "#R..p..g..g..g..g..@..C#",
    "#..###.....###.....###..#",
    "#..#.#..@..#.#..@..#.#..#",
    "#..###.....###.....###..#",
    "#........G............P.#",
    "#####....#####....#####.#",
    "#....@..#....@..#....@..#",
    "#..#####..#####..#####..#",
    "#...............@.......#",
    "########################"
]
TILE = 16
MAP_W, MAP_H = len(WORLD[0]), len(WORLD)
START_X, START_Y = 2, 1

# --- State ---
state = {
    "x": START_X, "y": START_Y, "facing":0,
    "poke": DEX[1].copy(), "party": [], "bag":[],"badges":0,"hp": DEX[1]["hp"], "balls": 5, "money": 500,
    "mode":"intro","msg":"Press Z to Start!", "area":"Pallet Town", "rival":"Blue", "boss":False
}

def draw_map():
    for y in range(MAP_H):
        for x in range(MAP_W):
            tile = WORLD[y][x]
            col = WHITE
            if tile=="#": col=GRAY
            if tile=="g": col=(130,200,130)
            if tile=="@": col=(224,128,255)
            if tile=="P": col=(255,210,0)
            if tile=="G": col=(128,210,255)
            if tile=="R": col=(220, 100, 64)
            if tile=="C": col=(200, 40, 200)
            pygame.draw.rect(screen, col, (x*TILE, y*TILE, TILE, TILE))
    pygame.draw.rect(screen, RED, (state["x"]*TILE, state["y"]*TILE, TILE, TILE),0,3)
    tx = font.render(state["area"],1,BLACK)
    screen.blit(tx,(6,6))

def draw_hud():
    pygame.draw.rect(screen, WHITE, (0, 272, 384, 64))
    pygame.draw.rect(screen, RED, (0, 272, 384, 3))
    t = font.render(state["msg"], 1, BLACK)
    screen.blit(t, (12, 288))
    t2 = font.render(f"HP:{state['hp']}/{state['poke']['hp']} POKé: {len(state['party'])+1} BADGES:{state['badges']} $: {state['money']}",1,RED)
    screen.blit(t2, (8, 315))
    t3 = font.render(f"BALLS:{state['balls']}",1,BLACK)
    screen.blit(t3,(300,315))

def draw_poke(x,y,poke,side):
    col = (224,64,64) if side=="player" else (90,90,90)
    pygame.draw.rect(screen, col, (x,y,24,24), 0, 4)
    pygame.draw.rect(screen, BLACK, (x,y,24,24), 2, 4)
    t = font.render(poke["name"], 1, BLACK)
    screen.blit(t, (x+26,y+8))

def rand_encounter():
    if random.random()<0.12:
        wi = random.choice(WILD_GRASS)
        wild = DEX[wi].copy()
        return wild
    return None

def area_name(x,y):
    tile = WORLD[y][x]
    if tile=="g": return "Route 1"
    if tile=="@": return "Pokecenter"
    if tile=="G": return "Pewter Gym"
    if tile=="P": return "Pokemart"
    if tile=="R": return "Rival's House"
    if tile=="C": return "League Hall"
    return "Pallet Town"

def battle(enemy, trainer=False):
    state["mode"] = "battle"
    battle_cry()
    msg = f"{'Trainer' if trainer else 'Wild'} {enemy['name']} appears!"
    enehp, plhp = enemy["hp"], state["hp"]
    turn = 0
    caught = False
    while enehp>0 and plhp>0:
        screen.fill(WHITE)
        draw_poke(40, 60, state["poke"], "player")
        draw_poke(230, 40, enemy, "enemy")
        t1 = fontbig.render(f"{state['poke']['name']} HP:{plhp}",1,RED)
        t2 = fontbig.render(f"{enemy['name']} HP:{enehp}",1,GRAY)
        screen.blit(t1,(30,120)); screen.blit(t2,(180,120))
        t = font.render(f"1:{state['poke']['moves'][0]} 2:{state['poke']['moves'][1] if len(state['poke']['moves'])>1 else ''}",1,BLACK)
        screen.blit(t,(30,180))
        t = font.render("B:Bag  R:Run  Space:Throw Ball",1,BLACK)
        screen.blit(t,(30,210))
        pygame.display.flip()
        atk = None
        waiting=True
        while waiting:
            for e in pygame.event.get():
                if e.type==pygame.QUIT: sys.exit()
                if e.type==pygame.KEYDOWN:
                    if e.key==pygame.K_1: atk=0; waiting=False
                    if e.key==pygame.K_2: atk=1 if len(state["poke"]["moves"])>1 else 0; waiting=False
                    if e.key==pygame.K_r: state["msg"]="You ran!"; return
                    if e.key==pygame.K_b: state["msg"]="Bag: Pokéball x%d"%state["balls"]; pygame.time.wait(400)
                    if e.key==pygame.K_SPACE and not trainer and state["balls"]>0:
                        state["balls"] -= 1
                        catch_chance = 40 + (state["poke"]["atk"]*2) - (enehp*0.6)
                        if random.randint(0,100)<catch_chance:
                            caught = True
                            state["party"].append(enemy["name"])
                            gb_synth(1568,200,0.14,1)
                            state["msg"]=f"Caught {enemy['name']}!"
                            pygame.display.flip(); pygame.time.wait(800)
                            return
                        else:
                            state["msg"]="Oh no! Broke free!"
                            pygame.display.flip(); pygame.time.wait(400)
                            waiting=False
        hit = state['poke']['atk']+random.randint(-2,4)
        enehp -= max(1, hit)
        gb_synth(880,60+random.randint(0,40),0.12,turn%2)
        state["msg"]=f"{state['poke']['name']} used {state['poke']['moves'][atk]}!"
        pygame.display.flip(); pygame.time.wait(350)
        if enehp<=0: break
        hit = enemy['atk']+random.randint(-2,2)
        plhp -= max(1, hit)
        gb_synth(156+random.randint(0,30),40+random.randint(0,80),0.11,1)
        state["msg"]=f"{enemy['name']} used {enemy['moves'][0]}!"
        pygame.display.flip(); pygame.time.wait(300)
    if plhp>0:
        state["hp"]=plhp
        if not trainer:
            state["msg"]=f"You defeated wild {enemy['name']}!"
            state["money"]+=random.randint(20,45)
        else:
            state["msg"]=f"You defeated {state['rival']}!"
            state["badges"]+=1
            badge_jingle()
    else:
        state["msg"]="You fainted! Back to Pokecenter."
        state["hp"]=1
    pygame.display.flip(); pygame.time.wait(1200)
    state["mode"]="overworld"

def heal_center():
    heal_jingle()
    state["hp"] = state["poke"]["hp"]
    state["msg"] = "Pokémon healed!"
    pygame.display.flip(); pygame.time.wait(700)

def shop_mart():
    state["msg"] = "Mart: Z=Ball($200) X=Potion($300)"
    pygame.display.flip()
    buying = True
    while buying:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: sys.exit()
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_z and state["money"]>=200:
                    state["balls"]+=1; state["money"]-=200
                    state["msg"]="Bought Pokéball!"; buying=False
                if e.key==pygame.K_x and state["money"]>=300:
                    state["hp"]=min(state["poke"]["hp"], state["hp"]+15); state["money"]-=300
                    state["msg"]="Bought Potion!"; buying=False
                if e.key==pygame.K_ESCAPE: buying=False
        pygame.display.flip()

def gym_boss():
    boss = DEX[8].copy() # Onix
    state["msg"]="GYM LEADER: Brock challenges you!"
    pygame.display.flip(); pygame.time.wait(700)
    battle(boss,trainer=True)
    if state["hp"]>0:
        state["msg"]="BADGE GET! To the League Hall!"
        state["badges"]+=1
        badge_jingle()
        pygame.display.flip(); pygame.time.wait(900)

def league_boss():
    boss = DEX[11].copy() # Mewtwo
    state["msg"]="CHAMPION: Mewtwo blocks your way!"
    pygame.display.flip(); pygame.time.wait(700)
    battle(boss,trainer=True)
    if state["hp"]>0:
        state["msg"]="You are the LOBSTER CHAMPION!"
        badge_jingle()
        pygame.display.flip(); pygame.time.wait(1500)
        state["mode"]="ending"

poke_intro_jingle()
while True:
    screen.fill(WHITE)
    if state["mode"]=="intro":
        t = fontbig.render("Pokémon Lobster Red",1,RED)
        screen.blit(t,(30,100))
        t2 = font.render("The Ultra Zero-Shot Vibe Demo",1,BLACK)
        screen.blit(t2,(60,140))
        t3 = font.render("Press Z to Start",1,GRAY)
        screen.blit(t3,(100,180))
        draw_hud()
    elif state["mode"]=="overworld":
        draw_map(); draw_hud()
    elif state["mode"]=="ending":
        t = fontbig.render("CONGRATULATIONS!",1,GREEN)
        screen.blit(t,(40,130))
        t2 = fontbig.render("You are the LOBSTER CHAMPION!",1,RED)
        screen.blit(t2,(10,180))
        pygame.display.flip(); pygame.time.wait(2700); sys.exit()
    pygame.display.flip()
    for e in pygame.event.get():
        if e.type==pygame.QUIT: sys.exit()
        if e.type==pygame.KEYDOWN:
            if state["mode"]=="intro" and e.key==pygame.K_z:
                state["mode"]="overworld"
                state["msg"]="Arrow keys: Move. Grass: Encounter. @: Heal. G: Gym. C: League."
            elif state["mode"]=="overworld":
                dx,dy=0,0
                if e.key==pygame.K_LEFT: dx=-1
                if e.key==pygame.K_RIGHT: dx=1
                if e.key==pygame.K_UP: dy=-1
                if e.key==pygame.K_DOWN: dy=1
                nx, ny = state["x"]+dx, state["y"]+dy
                if 0<=nx<MAP_W and 0<=ny<MAP_H and WORLD[ny][nx]!="#":
                    state["x"], state["y"] = nx, ny
                    an = area_name(nx,ny)
                    state["area"]=an
                    tile = WORLD[ny][nx]
                    if tile=="g":
                        wild_grass_jingle()
                        wild = rand_encounter()
                        if wild: battle(wild)
                    elif tile=="@": heal_center()
                    elif tile=="G": gym_boss()
                    elif tile=="C": league_boss()
                    elif tile=="P": shop_mart()
                    elif tile=="R":
                        if not state.get("rival_win",False):
                            battle(DEX[0].copy(),trainer=True)
                            state["rival_win"]=True
                            state["msg"]="You defeated Blue! Head north."
                            pygame.display.flip(); pygame.time.wait(900)
                if e.key==pygame.K_ESCAPE: sys.exit()
    clock.tick(FPS)
