import tkinter as tk
import random
import time
from tkinter import font as tkfont

class PaperMarioKoopaBoss:
    def __init__(self, root):
        self.root = root
        self.root.title("TEAM SPECIALEMU AGI Division Presents: Paper Mario - Koopa Showdown")
        self.root.geometry("600x400")
        self.root.configure(bg='#87CEEB')
        
        # Game state
        self.mario_hp = 50
        self.mario_max_hp = 50
        self.koopa_hp = 80
        self.koopa_max_hp = 80
        self.koopa_phase = 1
        self.turn = 1
        self.battle_log = []
        self.mario_stickers = [
            {"name": "Jump", "damage": 5, "type": "basic"},
            {"name": "Hammer", "damage": 7, "type": "basic"},
            {"name": "Fire Flower", "damage": 10, "type": "special"},
            {"name": "POW Block", "damage": 12, "type": "special"},
            {"name": "Mushroom", "damage": -15, "type": "heal"},
            {"name": "Shell Shield", "damage": 0, "type": "defense"}
        ]
        self.koopa_shell_mode = False
        self.action_command_active = False
        
        # Fonts
        self.title_font = tkfont.Font(family="Arial", size=14, weight="bold")
        self.text_font = tkfont.Font(family="Arial", size=10)
        
        self.setup_ui()
        self.start_battle()
        
    def setup_ui(self):
        # Title
        title_label = tk.Label(self.root, text="TEAM SPECIALEMU AGI Division Presents", 
                              font=self.title_font, bg='#87CEEB', fg='red')
        title_label.pack(pady=5)
        
        # Battle arena
        self.arena_frame = tk.Frame(self.root, bg='#F0E68C', relief=tk.RAISED, bd=3)
        self.arena_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Character frames
        self.mario_frame = tk.Frame(self.arena_frame, bg='#F0E68C')
        self.mario_frame.place(x=100, y=150)
        
        self.koopa_frame = tk.Frame(self.arena_frame, bg='#F0E68C')
        self.koopa_frame.place(x=400, y=150)
        
        # Mario sprite (simplified)
        self.mario_label = tk.Label(self.mario_frame, text="🦸", font=("Arial", 40), bg='#F0E68C')
        self.mario_label.pack()
        self.mario_hp_label = tk.Label(self.mario_frame, text=f"HP: {self.mario_hp}/{self.mario_max_hp}", 
                                      font=self.text_font, bg='#F0E68C')
        self.mario_hp_label.pack()
        
        # Koopa sprite
        self.koopa_label = tk.Label(self.koopa_frame, text="🐢", font=("Arial", 40), bg='#F0E68C')
        self.koopa_label.pack()
        self.koopa_hp_label = tk.Label(self.koopa_frame, text=f"HP: {self.koopa_hp}/{self.koopa_max_hp}", 
                                      font=self.text_font, bg='#F0E68C')
        self.koopa_hp_label.pack()
        
        # Dialog box
        self.dialog_frame = tk.Frame(self.root, bg='white', relief=tk.RAISED, bd=2)
        self.dialog_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.dialog_text = tk.Text(self.dialog_frame, height=4, wrap=tk.WORD, font=self.text_font)
        self.dialog_text.pack(padx=5, pady=5)
        
        # Sticker selection
        self.sticker_frame = tk.Frame(self.root, bg='#87CEEB')
        self.sticker_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.sticker_buttons = []
        for i, sticker in enumerate(self.mario_stickers):
            btn = tk.Button(self.sticker_frame, text=sticker["name"], 
                           command=lambda s=sticker: self.use_sticker(s),
                           font=self.text_font, width=12)
            btn.grid(row=0, column=i, padx=2)
            self.sticker_buttons.append(btn)
            
    def start_battle(self):
        self.add_dialog("💥 BOSS BATTLE START! 💥")
        self.add_dialog('Koopa: "You think you can peel past my shell? Let\'s see you try, flatty!"')
        self.add_dialog(f"Turn {self.turn}: Choose your sticker!")
        
    def add_dialog(self, text):
        self.dialog_text.insert(tk.END, text + "\n")
        self.dialog_text.see(tk.END)
        self.root.update()
        
    def use_sticker(self, sticker):
        if self.action_command_active:
            return
            
        self.disable_stickers()
        
        # Mario's turn
        self.add_dialog(f"\nMario uses {sticker['name']}!")
        
        # Action command mini-game
        if sticker['type'] in ['basic', 'special']:
            self.action_command(sticker)
        else:
            self.execute_mario_action(sticker, 1.0)
            
    def action_command(self, sticker):
        self.action_command_active = True
        self.add_dialog("⚡ ACTION COMMAND! Press SPACE at the right time! ⚡")
        
        # Create timing indicator
        self.timing_bar = tk.Canvas(self.root, width=200, height=30, bg='gray')
        self.timing_bar.pack(pady=5)
        
        # Moving indicator
        self.indicator = self.timing_bar.create_rectangle(0, 5, 10, 25, fill='red')
        self.target_zone = self.timing_bar.create_rectangle(80, 0, 120, 30, fill='green', outline='darkgreen', width=2)
        
        self.indicator_pos = 0
        self.indicator_speed = 5
        self.command_success = False
        
        self.root.bind('<space>', lambda e: self.check_action_command())
        self.move_indicator(sticker)
        
    def move_indicator(self, sticker):
        if self.indicator_pos <= 200:
            self.timing_bar.coords(self.indicator, self.indicator_pos, 5, self.indicator_pos + 10, 25)
            self.indicator_pos += self.indicator_speed
            self.root.after(50, lambda: self.move_indicator(sticker))
        else:
            self.finish_action_command(sticker)
            
    def check_action_command(self):
        if 80 <= self.indicator_pos <= 120:
            self.command_success = True
            self.add_dialog("💫 EXCELLENT! 💫")
        else:
            self.add_dialog("💢 Missed! 💢")
            
    def finish_action_command(self, sticker):
        self.root.unbind('<space>')
        self.timing_bar.destroy()
        self.action_command_active = False
        
        multiplier = 1.5 if self.command_success else 1.0
        self.execute_mario_action(sticker, multiplier)
        
    def execute_mario_action(self, sticker, multiplier):
        if sticker['type'] == 'heal':
            heal_amount = int(-sticker['damage'] * multiplier)
            self.mario_hp = min(self.mario_max_hp, self.mario_hp + heal_amount)
            self.add_dialog(f"Mario recovers {heal_amount} HP!")
        elif sticker['type'] == 'defense':
            self.add_dialog("Mario prepares to defend!")
        else:
            damage = int(sticker['damage'] * multiplier)
            
            if self.koopa_shell_mode and sticker['name'] in ['Jump', 'Hammer']:
                self.add_dialog("Koopa's shell blocks the attack!")
                damage = 0
            else:
                if self.koopa_shell_mode:
                    self.koopa_shell_mode = False
                    self.koopa_label.config(text="🐢")
                    self.add_dialog("Koopa is knocked out of shell mode!")
                
                self.koopa_hp -= damage
                self.add_dialog(f"Koopa takes {damage} damage!")
                
                # Shake animation
                self.shake_character(self.koopa_frame)
                
        self.update_hp()
        self.root.after(1500, self.koopa_turn)
        
    def koopa_turn(self):
        if self.koopa_hp <= 0:
            self.victory()
            return
            
        # Phase transitions
        if self.koopa_hp <= 50 and self.koopa_phase == 1:
            self.koopa_phase = 2
            self.add_dialog("\n🔥 Koopa: 'Now you've done it! Time for my STICKER POWER!' 🔥")
            
        # Koopa attacks
        attack_choice = random.choice(['shell_spin', 'sticker_steal', 'power_up', 'basic_attack'])
        
        if attack_choice == 'shell_spin':
            self.add_dialog("\nKoopa enters Shell Mode and spins!")
            self.koopa_shell_mode = True
            self.koopa_label.config(text="🟢")
            damage = 8 if self.koopa_phase == 2 else 5
            self.mario_hp -= damage
            self.add_dialog(f"Mario takes {damage} damage from the spinning shell!")
            self.shake_character(self.mario_frame)
            
        elif attack_choice == 'sticker_steal' and self.koopa_phase == 2:
            self.add_dialog("\nKoopa uses Sticker Steal!")
            stolen = random.choice(self.mario_stickers)
            self.add_dialog(f"Koopa steals your {stolen['name']} sticker for this turn!")
            
        elif attack_choice == 'power_up' and self.koopa_phase == 2:
            self.add_dialog("\nKoopa uses Power-Up Sticker!")
            self.add_dialog("Koopa's attack increases!")
            
        else:
            self.add_dialog("\nKoopa attacks with a shell bash!")
            damage = 10 if self.koopa_phase == 2 else 6
            self.mario_hp -= damage
            self.add_dialog(f"Mario takes {damage} damage!")
            self.shake_character(self.mario_frame)
            
        self.update_hp()
        
        if self.mario_hp <= 0:
            self.game_over()
        else:
            self.turn += 1
            self.add_dialog(f"\nTurn {self.turn}: Choose your sticker!")
            self.enable_stickers()
            
    def shake_character(self, frame):
        original_x = frame.winfo_x()
        for i in range(3):
            frame.place(x=original_x + 5)
            self.root.update()
            time.sleep(0.05)
            frame.place(x=original_x - 5)
            self.root.update()
            time.sleep(0.05)
        frame.place(x=original_x)
        
    def update_hp(self):
        self.mario_hp_label.config(text=f"HP: {max(0, self.mario_hp)}/{self.mario_max_hp}")
        self.koopa_hp_label.config(text=f"HP: {max(0, self.koopa_hp)}/{self.koopa_max_hp}")
        
    def disable_stickers(self):
        for btn in self.sticker_buttons:
            btn.config(state=tk.DISABLED)
            
    def enable_stickers(self):
        for btn in self.sticker_buttons:
            btn.config(state=tk.NORMAL)
            
    def victory(self):
        self.add_dialog("\n🎉 VICTORY! 🎉")
        self.add_dialog("Koopa: 'My beautiful shell! You haven't seen the last of me!'")
        self.add_dialog("You earned the Shell Sticker!")
        self.disable_stickers()
        
    def game_over(self):
        self.add_dialog("\n💀 GAME OVER 💀")
        self.add_dialog("Koopa: 'Better luck next time, paper boy!'")
        self.disable_stickers()

if __name__ == "__main__":
    root = tk.Tk()
    game = PaperMarioKoopaBoss(root)
    root.mainloop()
