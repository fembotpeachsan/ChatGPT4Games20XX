from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# Set window properties
window.title = 'Super Mario Odyssey 2'
window.borderless = False
window.fullscreen = False
window.size = (600, 400)
window.position = (100, 100)
window.fps_counter.enabled = True
window.exit_button.visible = False
app.target_fps = 60

# Global variables
current_kingdom = "n64_express"
current_player = "mario"
coins = 0
stars = 0
player_speed = 5
player_jump = 1.5

# Create custom models
def create_mario_model():
    mario = Entity(model='cube', color=color.red, scale=(1, 1.5, 1))
    mario_head = Entity(model='sphere', color=color.red, scale=0.8, position=(0, 0.8, 0), parent=mario)
    mario_hat = Entity(model='cube', color=color.red, scale=(1.2, 0.2, 1.2), position=(0, 1, 0), parent=mario)
    return mario

def create_luigi_model():
    luigi = Entity(model='cube', color=color.green, scale=(1, 1.5, 1))
    luigi_head = Entity(model='sphere', color=color.green, scale=0.8, position=(0, 0.8, 0), parent=luigi)
    luigi_hat = Entity(model='cube', color=color.green, scale=(1.2, 0.2, 1.2), position=(0, 1, 0), parent=luigi)
    return luigi

# Create players
mario = create_mario_model()
luigi = create_luigi_model()
player = FirstPersonController()
player.collider = 'box'
player.scale_y = 1.8
player.speed = player_speed
player.jump_height = player_jump
player.gravity = 1
player.cursor.visible = False
player.visible = False

# Kingdom environments
kingdoms = {}
sky = Sky(texture='sky_default')
ground = Entity(model='plane', scale=100, texture='grass', collider='mesh')

# N64 Express Hub
def create_n64_express():
    # Train base
    train = Entity(model='cube', scale=(20, 4, 5), texture='brick', position=(0, 2, 0))
    
    # Train cars
    car1 = Entity(model='cube', scale=(5, 3, 4), texture='brick', position=(-8, 1.5, 0))
    car2 = Entity(model='cube', scale=(5, 3, 4), texture='brick', position=(-13, 1.5, 0))
    car3 = Entity(model='cube', scale=(5, 3, 4), texture='brick', position=(-18, 1.5, 0))
    
    # Wheels
    wheel_positions = [
        (7, 0.5, 2.5), (7, 0.5, -2.5),
        (3, 0.5, 2.5), (3, 0.5, -2.5),
        (-1, 0.5, 2.5), (-1, 0.5, -2.5),
        (-5, 0.5, 2.5), (-5, 0.5, -2.5),
        (-10, 0.5, 2.5), (-10, 0.5, -2.5),
        (-15, 0.5, 2.5), (-15, 0.5, -2.5),
        (-20, 0.5, 2.5), (-20, 0.5, -2.5)
    ]
    
    wheels = []
    for pos in wheel_positions:
        wheel = Entity(model='cylinder', scale=(1, 0.2, 1), color=color.gray, position=pos)
        wheels.append(wheel)
    
    # Kingdom portals
    portal_positions = [
        (-3, 2.5, 0, "Waterfront Kingdom"),
        (-8, 2.5, 0, "Flower Kingdom"),
        (-13, 2.5, 0, "Shimmerock Kingdom"),
        (-18, 2.5, 0, "Bowser Jr. Kingdom")
    ]
    
    portals = []
    for x, y, z, name in portal_positions:
        portal = Entity(
            model='circle', 
            scale=2, 
            color=color.azure, 
            position=(x, y, z),
            rotation_x=90,
            collider='box'
        )
        portal.name = name
        portals.append(portal)
    
    return [train, car1, car2, car3] + wheels + portals

# Kingdoms
def create_waterfront_kingdom():
    # Base terrain
    terrain = Entity(model='plane', scale=50, texture='water', collider='mesh')
    
    # Islands
    island1 = Entity(model='cube', scale=(10, 1, 10), position=(20, 0, 0), texture='grass', collider='box')
    island2 = Entity(model='cube', scale=(10, 1, 10), position=(0, 0, 20), texture='grass', collider='box')
    island3 = Entity(model='cube', scale=(10, 1, 10), position=(-20, 0, 0), texture='grass', collider='box')
    
    # Buildings
    buildings = []
    for i in range(5):
        building = Entity(
            model='cube', 
            scale=(random.uniform(2,4), random.uniform(4,8), random.uniform(2,4)),
            position=(random.uniform(-40,40), random.uniform(0,10), random.uniform(-40,40)),
            texture='brick',
            collider='box'
        )
        buildings.append(building)
    
    # Collectibles
    coin_positions = [(15, 2, 0), (0, 2, 15), (-15, 2, 0), (0, 2, -15)]
    coins = []
    for pos in coin_positions:
        coin = Entity(
            model='sphere', 
            scale=0.5,
            color=color.gold,
            position=pos,
            collider='sphere'
        )
        coins.append(coin)
    
    star = Entity(
        model='sphere', 
        scale=1,
        color=color.yellow,
        position=(0, 5, 0),
        collider='box'
    )
    
    return [terrain, island1, island2, island3] + buildings + coins + [star]

def create_flower_kingdom():
    # Base terrain
    terrain = Entity(model='plane', scale=50, texture='grass', collider='mesh')
    
    # Flowers
    flowers = []
    for i in range(20):
        stem = Entity(
            model='cube',
            scale=(0.1, random.uniform(0.5, 1.5), 0.1),
            position=(random.uniform(-45,45), 0.5, random.uniform(-45,45)),
            color=color.green
        )
        flower = Entity(
            model='sphere',
            scale=0.5,
            position=stem.position + (0, stem.scale_y/2 + 0.25, 0),
            color=random.choice([color.red, color.yellow, color.pink])
        )
        flowers.append(stem)
        flowers.append(flower)
    
    # Trees
    trees = []
    for i in range(10):
        trunk = Entity(
            model='cylinder',
            scale=(1, random.uniform(3,5), 1),
            position=(random.uniform(-40,40), 1.5, random.uniform(-40,40)),
            color=color.brown,
            collider='box'
        )
        leaves = Entity(
            model='sphere',
            scale=random.uniform(3,5),
            position=trunk.position + (0, trunk.scale_y, 0),
            color=color.green,
            collider='box'
        )
        trees.append(trunk)
        trees.append(leaves)
    
    # Collectibles
    coin_positions = [(20, 2, 20), (20, 2, -20), (-20, 2, 20), (-20, 2, -20)]
    coins = []
    for pos in coin_positions:
        coin = Entity(
            model='sphere', 
            scale=0.5,
            color=color.gold,
            position=pos,
            collider='sphere'
        )
        coins.append(coin)
    
    star = Entity(
        model='sphere', 
        scale=1,
        color=color.yellow,
        position=(0, 5, 0),
        collider='box'
    )
    
    return [terrain] + flowers + trees + coins + [star]

# UI Elements
def create_ui():
    # Coin counter
    coin_icon = Entity(
        model='quad',
        texture='circle',
        color=color.gold,
        scale=(0.05, 0.05),
        position=window.top_left + (0.05, -0.05, 0)
    )
    
    coin_text = Text(
        text=f"Coins: {coins}",
        position=window.top_left + (0.1, -0.05, 0),
        origin=(0, 0),
        scale=1.5
    )
    
    # Star counter
    star_icon = Entity(
        model='quad',
        texture='circle',
        color=color.yellow,
        scale=(0.05, 0.05),
        position=window.top_left + (0.05, -0.12, 0)
    )
    
    star_text = Text(
        text=f"Stars: {stars}",
        position=window.top_left + (0.1, -0.12, 0),
        origin=(0, 0),
        scale=1.5
    )
    
    # Kingdom name
    kingdom_text = Text(
        text="N64 Express",
        position=window.top,
        origin=(0, 0),
        scale=2,
        y=-0.05
    )
    
    # Character indicator
    character_text = Text(
        text=f"Character: {current_player.capitalize()}",
        position=window.bottom_left,
        origin=(0, 0),
        scale=1.5,
        x=0.05,
        y=0.05
    )
    
    return [coin_icon, coin_text, star_icon, star_text, kingdom_text, character_text]

# Create game world
n64_express = create_n64_express()
waterfront_kingdom = create_waterfront_kingdom()
flower_kingdom = create_flower_kingdom()
ui_elements = create_ui()

# Hide kingdoms initially
for entity in waterfront_kingdom:
    entity.enabled = False

for entity in flower_kingdom:
    entity.enabled = False

# Game state management
def switch_kingdom(kingdom_name):
    global current_kingdom
    
    # Hide current kingdom
    if current_kingdom == "n64_express":
        for entity in n64_express:
            entity.enabled = False
    elif current_kingdom == "waterfront":
        for entity in waterfront_kingdom:
            entity.enabled = False
    elif current_kingdom == "flower":
        for entity in flower_kingdom:
            entity.enabled = False
    
    # Show new kingdom
    current_kingdom = kingdom_name
    if kingdom_name == "n64_express":
        for entity in n64_express:
            entity.enabled = True
        ui_elements[4].text = "N64 Express"
        player.position = (0, 3, 0)
    elif kingdom_name == "waterfront":
        for entity in waterfront_kingdom:
            entity.enabled = True
        ui_elements[4].text = "Waterfront Kingdom"
        player.position = (0, 5, 0)
    elif kingdom_name == "flower":
        for entity in flower_kingdom:
            entity.enabled = True
        ui_elements[4].text = "Flower Kingdom"
        player.position = (0, 5, 0)

# Player controls
def switch_character():
    global current_player
    if current_player == "mario":
        current_player = "luigi"
        player.color = color.green
    else:
        current_player = "mario"
        player.color = color.red
    ui_elements[5].text = f"Character: {current_player.capitalize()}"

def collect_coin(coin):
    global coins
    coins += 1
    coin.enabled = False
    ui_elements[1].text = f"Coins: {coins}"

def collect_star(star):
    global stars
    stars += 1
    star.enabled = False
    ui_elements[3].text = f"Stars: {stars}"
    # Return to train after collecting star
    switch_kingdom("n64_express")

# Input handling
def input(key):
    # Character switching
    if key == 'c':
        switch_character()
    
    # Kingdom switching
    if current_kingdom == "n64_express" and key == 'e':
        # Check if player is near a portal
        for entity in n64_express:
            if hasattr(entity, 'name') and entity.name in ["Waterfront Kingdom", "Flower Kingdom"]:
                if distance(player.position, entity.position) < 3:
                    if entity.name == "Waterfront Kingdom":
                        switch_kingdom("waterfront")
                    elif entity.name == "Flower Kingdom":
                        switch_kingdom("flower")
    
    # Return to train
    if key == 'r' and current_kingdom != "n64_express":
        switch_kingdom("n64_express")
    
    # Quit game
    if key == 'q':
        application.quit()

# Collision detection
def update():
    # Coin collection
    if current_kingdom == "waterfront":
        for entity in waterfront_kingdom:
            if hasattr(entity, 'color') and entity.color == color.gold:
                if distance(player.position, entity.position) < 2:
                    collect_coin(entity)
        for entity in waterfront_kingdom:
            if hasattr(entity, 'color') and entity.color == color.yellow:
                if distance(player.position, entity.position) < 2:
                    collect_star(entity)
    
    if current_kingdom == "flower":
        for entity in flower_kingdom:
            if hasattr(entity, 'color') and entity.color == color.gold:
                if distance(player.position, entity.position) < 2:
                    collect_coin(entity)
        for entity in flower_kingdom:
            if hasattr(entity, 'color') and entity.color == color.yellow:
                if distance(player.position, entity.position) < 2:
                    collect_star(entity)

# Set initial state
player.visible = True
player.position = (0, 3, 0)
player.color = color.red

# Start the game
app.run()
