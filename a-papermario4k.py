import tkinter as tk
import pygame
import os
import random
import math

# Define screen dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400

# Colors
COLOR_SKY_BLUE = (135, 206, 235)
COLOR_GRASS_GREEN = (34, 177, 76)
COLOR_RED = (255, 0, 0) # Player color
COLOR_BROWN = (139, 69, 19) # Obstacle color
COLOR_GOLD = (255, 215, 0) # Coin color
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)

# Paper Mario Logo Specific Colors
COLOR_PM_LOGO_RED = (230, 20, 20)       # Vibrant red for title text
COLOR_PM_LOGO_WHITE = COLOR_WHITE       # White for the main outline
COLOR_PM_LOGO_DARK_BROWN = (78, 53, 36) # Dark brown for the outer thin outline (same as COLOR_STROKE_PM)
COLOR_PM_LOGO_SHADOW = COLOR_BLACK      # Shadow color

# Game States
class GameState:
    MENU = 0
    PLAYING = 1

class PaperPlayerPygame:
    def __init__(self, x, y, z): # World coordinates (Ursina-like: Y is height)
        self.x = float(x)
        self.y = float(y) # Height above ground plane
        self.z = float(z)
        
        self.world_width = 0.8  # Logical width for collision/drawing base
        self.world_depth = 0.8  # Logical depth for collision/drawing base
        self.body_height = 1.0  # Logical height of the player model

        self.color = COLOR_RED # Player's body color
        self.outline_color = COLOR_BLACK # Player's body outline

        self.speed = 5.0 # World units per second
        self.direction = 'down' # 'up', 'down', 'left', 'right'
        self.collision_radius = self.world_width / 2 

    def update(self, keys, dt, obstacles):
        prev_x, prev_z = self.x, self.z
        moved = False
        if keys[pygame.K_w]:
            self.z -= self.speed * dt; self.direction = 'up'; moved = True
        if keys[pygame.K_s]:
            self.z += self.speed * dt; self.direction = 'down'; moved = True
        if keys[pygame.K_a]:
            self.x -= self.speed * dt; self.direction = 'left'; moved = True
        if keys[pygame.K_d]:
            self.x += self.speed * dt; self.direction = 'right'; moved = True

        if moved:
            for obs in obstacles:
                # Simple AABB collision for player base against obstacle base (XZ plane)
                player_rect_xz = pygame.Rect(self.x - self.world_width / 2, self.z - self.world_depth / 2, self.world_width, self.world_depth)
                obs_rect_xz = pygame.Rect(obs.x - obs.world_width / 2, obs.z - obs.world_width / 2, obs.world_width, obs.world_width) # Assuming obs.world_depth = obs.world_width
                
                # More accurate circular collision for player
                dist_sq = (self.x - obs.x)**2 + (self.z - obs.z)**2
                # Assuming obstacle is roughly circular for collision for simplicity, using its width
                if dist_sq < (self.collision_radius + obs.world_width / 2)**2:
                    self.x, self.z = prev_x, prev_z
                    break
    
    def draw(self, surface, game_app_instance):
        body_center_y_world = self.y + self.body_height / 2
        sx_center, sy_center = game_app_instance.world_to_screen(self.x, body_center_y_world, self.z)
        player_screen_width = 20 
        player_screen_height = 25
        rect_draw = pygame.Rect(sx_center - player_screen_width / 2, sy_center - player_screen_height / 2, player_screen_width, player_screen_height)
        pygame.draw.rect(surface, self.color, rect_draw)
        pygame.draw.rect(surface, self.outline_color, rect_draw, 1)
        nose_length = 8
        r_center_x, r_center_y = rect_draw.centerx, rect_draw.centery
        if self.direction == 'up': pygame.draw.line(surface, self.outline_color, (r_center_x, rect_draw.top), (r_center_x, rect_draw.top - nose_length), 2)
        elif self.direction == 'down': pygame.draw.line(surface, self.outline_color, (r_center_x, rect_draw.bottom), (r_center_x, rect_draw.bottom + nose_length), 2)
        elif self.direction == 'left': pygame.draw.line(surface, self.outline_color, (rect_draw.left, r_center_y), (rect_draw.left - nose_length, r_center_y), 2)
        elif self.direction == 'right': pygame.draw.line(surface, self.outline_color, (rect_draw.right, r_center_y), (rect_draw.right + nose_length, r_center_y), 2)

class ObstaclePygame:
    def __init__(self, x, y, z):
        self.x = float(x); self.y = float(y); self.z = float(z)
        self.color = COLOR_BROWN
        self.world_width = 2.0; self.world_height = 2.0 # Using world_width for depth as well for square base

    def draw(self, surface, game_app_instance):
        center_y_world = self.y + self.world_height / 2
        sx_center, sy_center = game_app_instance.world_to_screen(self.x, center_y_world, self.z)
        # Approximate screen size based on one dimension, assuming roughly isometric scaling
        screen_dimension_obj_approx = self.world_width * game_app_instance.PIXELS_PER_WORLD_UNIT_X_APPROX 
        obj_rect = pygame.Rect(sx_center - screen_dimension_obj_approx / 2, 
                               sy_center - screen_dimension_obj_approx / 2, # Assuming roughly square on screen for simplicity
                               screen_dimension_obj_approx, screen_dimension_obj_approx)
        pygame.draw.rect(surface, self.color, obj_rect)
        pygame.draw.rect(surface, COLOR_BLACK, obj_rect, 1)

class CoinPygame:
    def __init__(self, x, y, z):
        self.x = float(x); self.y = float(y); self.z = float(z)
        self.color = COLOR_GOLD
        self.world_radius = 0.25
        self.animation_angle_rad = random.uniform(0, 2 * math.pi) # Start at random rotation
        self.collected = False

    def update(self, dt):
        self.animation_angle_rad = (self.animation_angle_rad + math.pi * dt * 2) % (2 * math.pi) # Faster spin

    def draw(self, surface, game_app_instance):
        if self.collected: return
        sx_center, sy_center = game_app_instance.world_to_screen(self.x, self.y, self.z)
        max_screen_radius = self.world_radius * game_app_instance.PIXELS_PER_WORLD_UNIT_X_APPROX * 1.5
        width_factor = abs(math.cos(self.animation_angle_rad))
        current_ellipse_width = max(3, max_screen_radius * 2 * width_factor) # Ensure min width
        current_ellipse_height = max(3,max_screen_radius * 2)
        coin_ellipse_rect = pygame.Rect(sx_center - current_ellipse_width / 2, sy_center - current_ellipse_height / 2, current_ellipse_width, current_ellipse_height)
        pygame.draw.ellipse(surface, self.color, coin_ellipse_rect)
        pygame.draw.ellipse(surface, COLOR_BLACK, coin_ellipse_rect, 1)

class GameApp:
    def __init__(self, root_tk_window):
        self.root = root_tk_window
        self.root.title("Paper Mario 64 Tech Demo - Pygame/Tkinter")
        self.root.resizable(False, False)
        self.embed_frame = tk.Frame(self.root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
        self.embed_frame.pack()
        os.environ['SDL_WINDOWID'] = str(self.embed_frame.winfo_id())
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        
        try:
            self.title_font = pygame.font.SysFont("Impact", 60)
        except:
            self.title_font = pygame.font.SysFont(None, 70) 
        try:
            self.prompt_font = pygame.font.SysFont("Arial", 30)
        except:
            self.prompt_font = pygame.font.SysFont(None, 40)
        self.hud_font = pygame.font.SysFont(None, 30)
        self.floating_text_font = pygame.font.SysFont(None, 24)
        
        self.show_fps = True
        self.current_state = GameState.MENU
        self.menu_blink_timer = 0
        self.menu_prompt_visible = True
        
        self.initialize_game_elements()
        
        self.TILE_WIDTH_HALF = 22; self.TILE_HEIGHT_HALF = 11; self.HEIGHT_SCALE = 20
        self.PIXELS_PER_WORLD_UNIT_X_APPROX = 20; self.PIXELS_PER_WORLD_UNIT_Y_APPROX = 20

    def initialize_game_elements(self):
        self.player = PaperPlayerPygame(x=0, y=0.5, z=0) # Player y is base height on ground
        self.ground_y_ursina = 0.0 
        self.obstacles = [ObstaclePygame(x=random.uniform(-8,8), y=0.25, z=random.uniform(-8,8)) for _ in range(5)]
        self.coins = [CoinPygame(x=random.uniform(-10.0, 10.0), y=0.75, z=random.uniform(-10.0, 10.0)) for _ in range(8)]
        self.score = 0
        self.floating_texts = []
        self.all_coins_collected_message_shown = False


        if not hasattr(self, 'camera_x') or self.current_state == GameState.MENU: 
            self.camera_x = 0.0
            self.camera_z = 0.0
        else: 
            self.camera_x = self.player.x 
            self.camera_z = self.player.z


    def world_to_screen(self, world_x_ursina, world_y_ursina, world_z_ursina):
        screen_center_x = SCREEN_WIDTH / 2; screen_center_y = SCREEN_HEIGHT / 2
        cam_proj_x_ground = (self.camera_x - self.camera_z) * self.TILE_WIDTH_HALF
        cam_proj_y_ground = (self.camera_x + self.camera_z) * self.TILE_HEIGHT_HALF
        obj_proj_x_ground = (world_x_ursina - world_z_ursina) * self.TILE_WIDTH_HALF
        obj_proj_y_ground = (world_x_ursina + world_z_ursina) * self.TILE_HEIGHT_HALF
        sx = screen_center_x + (obj_proj_x_ground - cam_proj_x_ground)
        sy = screen_center_y + (obj_proj_y_ground - cam_proj_y_ground) - (world_y_ursina * self.HEIGHT_SCALE)
        return int(sx), int(sy)

    def draw_text_outlined(self, surface, text, font, color, outline_color, pos, outline_width=2):
        text_surface = font.render(text, True, color)
        outline_surface = font.render(text, True, outline_color)
        text_rect = text_surface.get_rect(center=pos)

        for dx_offset_factor in [-1, 0, 1]:
            for dy_offset_factor in [-1, 0, 1]:
                if dx_offset_factor == 0 and dy_offset_factor == 0:
                    continue # Skip center for outline only
                # Blit outline at pixel offsets for a tighter outline
                for i in range(1, outline_width + 1):
                    outline_draw_rect = outline_surface.get_rect(center=(pos[0] + dx_offset_factor*i, pos[1] + dy_offset_factor*i))
                    surface.blit(outline_surface, outline_draw_rect)
        
        surface.blit(text_surface, text_rect) # Draw main text on top


    def draw_menu_screen(self, dt):
        self.screen.fill(COLOR_SKY_BLUE)
        original_cam_x, original_cam_z = self.camera_x, self.camera_z
        self.camera_x, self.camera_z = 0, 0 
        
        ground_span = 30
        ground_corners_world = [
            (-ground_span, self.ground_y_ursina, -ground_span), (ground_span, self.ground_y_ursina, -ground_span),
            (ground_span, self.ground_y_ursina, ground_span), (-ground_span, self.ground_y_ursina, ground_span)
        ]
        ground_corners_screen = [self.world_to_screen(x,y,z) for x,y,z in ground_corners_world]
        pygame.draw.polygon(self.screen, COLOR_GRASS_GREEN, ground_corners_screen)
        self.camera_x, self.camera_z = original_cam_x, original_cam_z

        title_text_str = "PAPER MARIO 64"
        title_center_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
        title_main_font = self.title_font

        shadow_offset_val = (5, 5)
        shadow_layer_width = 3 # How "thick" the shadow silhouette's outline component is
        dark_brown_layer_width = 3 # How "thick" the dark brown outline layer is
        white_outline_layer_width = 2 # How "thick" the white outline around the red text is

        # 1. Draw Shadow Layer (farthest back)
        shadow_draw_center_pos = (title_center_pos[0] + shadow_offset_val[0], title_center_pos[1] + shadow_offset_val[1])
        self.draw_text_outlined(self.screen, title_text_str, title_main_font,
                                COLOR_PM_LOGO_SHADOW, COLOR_PM_LOGO_SHADOW, # Solid shadow color
                                shadow_draw_center_pos, shadow_layer_width)

        # 2. Draw Dark Brown Layer (outermost edge of the logo itself)
        self.draw_text_outlined(self.screen, title_text_str, title_main_font,
                                COLOR_PM_LOGO_DARK_BROWN, COLOR_PM_LOGO_DARK_BROWN, # Solid dark brown
                                title_center_pos, dark_brown_layer_width)

        # 3. Draw Red Text with White Outline on top of the dark brown layer
        # The white outline (COLOR_PM_LOGO_WHITE) will cover some of the dark brown,
        # and the red text (COLOR_PM_LOGO_RED) will sit inside the white outline.
        self.draw_text_outlined(self.screen, title_text_str, title_main_font,
                                COLOR_PM_LOGO_RED, # Fill color for the text
                                COLOR_PM_LOGO_WHITE, # Outline color for the red text
                                title_center_pos, white_outline_layer_width)
        
        title2_text = "Tech Demo"
        self.draw_text_outlined(self.screen, title2_text, self.prompt_font, COLOR_WHITE, COLOR_BLACK,
                                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 60), 2)

        self.menu_blink_timer += dt
        if self.menu_blink_timer >= 0.5:
            self.menu_prompt_visible = not self.menu_prompt_visible
            self.menu_blink_timer = 0
        if self.menu_prompt_visible:
            prompt_text = "Press Z or ENTER to Start"
            self.draw_text_outlined(self.screen, prompt_text, self.prompt_font, COLOR_WHITE, COLOR_BLACK,
                                    (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3 + 40), 2)

    def draw_game_world_screen(self):
        fixed_ground_center_x, fixed_ground_center_z = 0,0 
        fixed_ground_span = 50 
        ground_corners_world_fixed = [
            (fixed_ground_center_x - fixed_ground_span, self.ground_y_ursina, fixed_ground_center_z - fixed_ground_span),
            (fixed_ground_center_x + fixed_ground_span, self.ground_y_ursina, fixed_ground_center_z - fixed_ground_span),
            (fixed_ground_center_x + fixed_ground_span, self.ground_y_ursina, fixed_ground_center_z + fixed_ground_span),
            (fixed_ground_center_x - fixed_ground_span, self.ground_y_ursina, fixed_ground_center_z + fixed_ground_span)
        ]
        ground_corners_screen = [self.world_to_screen(x,y,z) for x,y,z in ground_corners_world_fixed]
        pygame.draw.polygon(self.screen, COLOR_GRASS_GREEN, ground_corners_screen)

        entities_to_draw = [self.player] + self.obstacles + [c for c in self.coins if not c.collected]
        entities_to_draw.sort(key=lambda e: ((e.x + e.z) * self.TILE_HEIGHT_HALF - e.y * self.HEIGHT_SCALE, (e.x - e.z) * self.TILE_WIDTH_HALF))
        for entity in entities_to_draw:
            entity.draw(self.screen, self)

    def draw_floating_texts(self, dt):
        texts_to_keep = []
        for ft_info in self.floating_texts:
            ft_info['life'] -= dt
            if ft_info['life'] > 0:
                # Update position (move up)
                current_pos = list(ft_info['pos'])
                current_pos[1] += ft_info['vy'] * dt
                ft_info['pos'] = tuple(current_pos)
                
                # Calculate alpha for fade out (optional, simple version just draws)
                # alpha = max(0, min(255, int(255 * (ft_info['life'] / ft_info['initial_life']))))
                # For simplicity, not implementing per-surface alpha here with draw_text_outlined.
                # Will just draw solid then disappear.

                self.draw_text_outlined(self.screen, ft_info['text'], ft_info['font'],
                                        ft_info['color'], ft_info['outline_color'],
                                        ft_info['pos'], 1) # Use a thin outline
                texts_to_keep.append(ft_info)
        self.floating_texts = texts_to_keep


    def draw_hud(self):
        score_text_surf = self.hud_font.render(f"Score: {self.score}", True, COLOR_BLACK)
        self.screen.blit(score_text_surf, (SCREEN_WIDTH - score_text_surf.get_width() - 10, 10))
        if self.show_fps:
            fps_val = int(self.clock.get_fps())
            fps_text_surf = self.hud_font.render(f"FPS: {fps_val}", True, COLOR_BLACK)
            self.screen.blit(fps_text_surf, (10, 10))

        if not self.all_coins_collected_message_shown and all(c.collected for c in self.coins) and self.coins: # Check if coins exist
            self.all_coins_collected_message_shown = True # Show only once per collection set
            # Add to floating texts or draw directly. For simplicity, draw directly for now.
            win_text = "All Coins Collected!"
            win_font = self.prompt_font # Use a larger font
            
            # Use draw_text_outlined for the win message
            win_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            self.draw_text_outlined(self.screen, win_text, win_font, 
                                    COLOR_GOLD, COLOR_BLACK, 
                                    win_pos, 2)


    def handle_menu_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z or event.key == pygame.K_RETURN:
                self.current_state = GameState.PLAYING
                self.all_coins_collected_message_shown = False # Reset for new game
                self.initialize_game_elements() 

    def handle_playing_event(self, event):
        pass

    def game_loop_step(self):
        dt = self.clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False; return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.current_state == GameState.PLAYING:
                    self.current_state = GameState.MENU 
                    self.camera_x = 0.0; self.camera_z = 0.0
                else: 
                    self.running = False; return

            if self.current_state == GameState.MENU:
                self.handle_menu_event(event)
            elif self.current_state == GameState.PLAYING:
                self.handle_playing_event(event)
        
        if self.current_state == GameState.PLAYING:
            keys = pygame.key.get_pressed()
            self.player.update(keys, dt, self.obstacles)
            self.camera_x = self.player.x
            self.camera_z = self.player.z
            
            for coin in self.coins:
                coin.update(dt) # Update animation regardless of collection status for simplicity
                if not coin.collected:
                    dist_sq = (self.player.x - coin.x)**2 + (self.player.z - coin.z)**2
                    y_dist = abs((self.player.y + self.player.body_height/2) - coin.y) 
                    if dist_sq < (self.player.collision_radius + coin.world_radius)**2 and \
                       y_dist < (self.player.body_height / 2 + coin.world_radius * 2): 
                        coin.collected = True
                        self.score += 10
                        
                        # Add floating score text
                        coin_screen_x, coin_screen_y = self.world_to_screen(coin.x, coin.y + 0.5, coin.z) # Slightly above coin
                        initial_life_duration = 1.0
                        self.floating_texts.append({
                            'text': "+10", 
                            'font': self.floating_text_font,
                            'color': COLOR_GOLD,
                            'outline_color': COLOR_BLACK,
                            'pos': (coin_screen_x, coin_screen_y), 
                            'life': initial_life_duration,
                            'initial_life': initial_life_duration, # For potential alpha calculation
                            'vy': -40 # Pixels per second upwards
                        })
        
        self.screen.fill(COLOR_SKY_BLUE)

        if self.current_state == GameState.MENU:
            self.draw_menu_screen(dt)
        elif self.current_state == GameState.PLAYING:
            self.draw_game_world_screen()
            self.draw_floating_texts(dt) # Draw floating scores
            self.draw_hud()

        pygame.display.flip()
        self.root.update_idletasks(); self.root.update()

    def cleanup(self):
        pygame.quit()
        try:
            if self.root.winfo_exists(): self.root.destroy()
        except tk.TclError: pass

    def start(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_tk_close)
        while self.running:
            self.game_loop_step()
        self.cleanup()

    def on_tk_close(self):
        self.running = False # Corrected typo here

if __name__ == '__main__':
    main_tk_window = tk.Tk()
    game_app = GameApp(main_tk_window)
    game_app.start()
