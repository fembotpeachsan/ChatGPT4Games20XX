from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
from ursina.prefabs.health_bar import HealthBar
import random

class MenuButton(Button):
    def __init__(self, text='', **kwargs):
        super().__init__(
            text=text,
            color=color.dark_gray,
            highlight_color=color.azure,
            pressed_color=color.azure,
            scale=(0.4, 0.075),
            text_origin=(0, 0),
            **kwargs
        )
        self.text_entity.scale = 1.5
        self.text_entity.color = color.white
        
    def on_mouse_enter(self):
        self.animate_scale(1.1, duration=0.1)
        self.text_entity.animate_scale(1.1, duration=0.1)
        
    def on_mouse_exit(self):
        self.animate_scale(1, duration=0.1)
        self.text_entity.animate_scale(1, duration=0.1)

class MainMenu(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui)
        
        # Background
        Entity(
            parent=self,
            model='quad',
            texture='noise',
            scale=(2, 1),
            color=color.dark_gray.tint(-.2),
            z=1
        )
        
        self.main_menu = Entity(parent=self, enabled=True)
        
        # Title with glow effect
        self.title = Text(
            text="CYBERMONK",
            origin=(0, -1.5),
            scale=4,
            parent=self.main_menu,
            color=color.cyan,
        )
        self.title_glow = Text(
            text="CYBERMONK",
            origin=(0, -1.5),
            scale=4.1,
            parent=self.main_menu,
            color=color.rgba(0, 255, 255, 100),
            z=0.1
        )
        
        # Subtitle
        Text(
            text="Journey into the Digital Realm",
            origin=(0, -2),
            scale=1.5,
            parent=self.main_menu,
            color=color.light_gray,
            y=-0.1
        )
        
        def start_game():
            self.animate_out()
            invoke(self.enable_game_scene, delay=0.5)
            
        def show_how_to_play():
            self.transition_to(self.how_to_play)
            
        def show_settings():
            self.transition_to(self.settings)
            
        def exit_game():
            application.quit()
        
        # Main menu buttons
        self.buttons = Entity(parent=self.main_menu)
        button_spacing = 0.1
        buttons_data = [
            ("Start Game", start_game),
            ("How to Play", show_how_to_play),
            ("Settings", show_settings),
            ("Exit", exit_game)
        ]
        
        for i, (text, func) in enumerate(buttons_data):
            MenuButton(
                text=text,
                parent=self.buttons,
                y=0.1 - i * (0.1 + button_spacing),
                on_click=func
            )
        
        # Settings menu
        self.settings = Entity(parent=self, enabled=False)
        self.settings_title = Text("Settings", origin=(0,0), scale=2, y=0.3, parent=self.settings)
        
        # Audio settings
        self.audio_settings = Entity(parent=self.settings)
        self.audio_mode = "Stereo"
        self.audio_text = Text(
            "Audio Mode: Stereo",
            parent=self.audio_settings,
            y=0.1,
            origin=(0,0)
        )
        
        def toggle_audio_mode():
            self.audio_mode = "Mono" if self.audio_mode == "Stereo" else "Stereo"
            self.audio_text.text = f"Audio Mode: {self.audio_mode}"
            # Audio implementation here
        
        MenuButton(
            "Toggle Audio Mode",
            parent=self.audio_settings,
            y=0,
            on_click=toggle_audio_mode
        )
        
        # Graphics settings
        self.graphics_settings = Entity(parent=self.settings)
        self.shadow_quality = "High"
        self.shadow_text = Text(
            "Shadow Quality: High",
            parent=self.graphics_settings,
            y=-0.1,
            origin=(0,0)
        )
        
        def toggle_shadow_quality():
            qualities = ["Low", "Medium", "High"]
            current_index = qualities.index(self.shadow_quality)
            self.shadow_quality = qualities[(current_index + 1) % len(qualities)]
            self.shadow_text.text = f"Shadow Quality: {self.shadow_quality}"
            # Shadow quality implementation here
        
        MenuButton(
            "Change Shadow Quality",
            parent=self.graphics_settings,
            y=-0.2,
            on_click=toggle_shadow_quality
        )
        
        # How to play menu
        self.how_to_play = Entity(parent=self, enabled=False)
        Text(
            text="How to Play",
            origin=(0,0),
            scale=2,
            y=0.3,
            parent=self.how_to_play
        )
        
        Text(
            text=dedent('''
                Controls:
                WASD - Move
                Space - Jump
                E - Interact
                Q - Special ability
                
                Objectives:
                • Explore the ancient cyberpunk world
                • Collect energy crystals to power up
                • Avoid or neutralize hostile programs
                • Find and activate data nodes
                • Reach the mainframe core
            ''').strip(),
            parent=self.how_to_play,
            origin=(0,0),
            y=0,
            line_height=1.5
        )
        
        # Back buttons for submenus
        def back_to_menu():
            for submenu in [self.settings, self.how_to_play]:
                if submenu.enabled:
                    self.transition_to(self.main_menu)
                    
        for submenu in [self.settings, self.how_to_play]:
            MenuButton(
                "Back",
                parent=submenu,
                y=-0.4,
                on_click=back_to_menu
            )
    
    def transition_to(self, target_menu):
        # Disable all menus
        for menu in [self.main_menu, self.settings, self.how_to_play]:
            if menu.enabled:
                menu.animate_scale_x(0, duration=0.1)
                menu.animate_alpha(0, duration=0.1)
                invoke(menu.disable, delay=0.1)
        
        # Enable and animate target menu
        target_menu.scale_x = 0
        target_menu.alpha = 0
        target_menu.enable()
        target_menu.animate_scale_x(1, duration=0.1)
        target_menu.animate_alpha(1, duration=0.1)
    
    def animate_out(self):
        self.animate_position((0, 2, 0), duration=0.5, curve=curve.out_expo)
        self.animate_alpha(0, duration=0.5)
    
    def enable_game_scene(self):
        self.disable()
        game_scene.enable()

# Game scene placeholder
game_scene = Entity()
game_scene.disable()

if __name__ == '__main__':
    app = Ursina()
    
    # Set up window
    window.fullscreen = False
    window.borderless = False
    window.title = 'CYBERMONK'
    
    # Create main menu
    main_menu = MainMenu()
    
    # Run the game
    app.run()
