import tkinter as tk
from tkinter import messagebox, ttk

# Levelengine Simulator

class LevelEngineSimulator:
    def __init__(self, selected_skin):
        self.day = True
        self.level = 1
        self.thirst = 100  # Max thirst
        self.xp = 0
        self.coins = 0
        self.uploading = False
        self.progress = 0
        self.selected_skin = selected_skin  # Skin selected by the player

        self.create_game_window()

    def create_game_window(self):
        self.game = tk.Tk()
        self.game.title("Levelengine Simulator")
        self.game.geometry("600x400")

        # UI Elements
        self.day_night_label = tk.Label(self.game, text="Day", font=("Arial", 16))
        self.day_night_label.pack(pady=5)

        self.level_label = tk.Label(self.game, text=f"Level: {self.level}", font=("Arial", 16))
        self.level_label.pack(pady=5)

        self.xp_label = tk.Label(self.game, text=f"XP: {self.xp}", font=("Arial", 12))
        self.xp_label.pack(pady=5)

        self.coins_label = tk.Label(self.game, text=f"Coins: {self.coins}", font=("Arial", 12))
        self.coins_label.pack(pady=5)

        self.thirst_label = tk.Label(self.game, text=f"Thirst: {self.thirst}%", font=("Arial", 12))
        self.thirst_label.pack(pady=5)

        # Player Avatar
        self.avatar_label = tk.Label(self.game, text="Player", font=("Arial", 24), bg=self.selected_skin)
        self.avatar_label.pack(pady=10)

        self.drink_button = tk.Button(self.game, text="Drink Water", command=self.drink_water, font=("Arial", 12))
        self.drink_button.pack(pady=5)

        self.upload_button = tk.Button(self.game, text="Upload Video", command=self.upload_video, font=("Arial", 12))
        self.upload_button.pack(pady=5)

        self.next_level_button = tk.Button(self.game, text="Next Level", command=self.next_level, font=("Arial", 12))
        self.next_level_button.pack(pady=5)

        self.sleep_button = tk.Button(self.game, text="Sleep", command=self.sleep, font=("Arial", 12))
        self.sleep_button.pack(pady=5)

        # Progress Bar for Upload
        self.progress_bar = ttk.Progressbar(self.game, orient='horizontal', length=200, mode='determinate')
        self.progress_label = tk.Label(self.game, text="Uploading... 0%", font=("Arial", 10))

        # Initialize background and start cycles
        self.game.config(bg="skyblue")
        self.game.after(5000, self.toggle_day_night)
        self.game.after(1000, self.decrease_thirst)

        self.game.mainloop()

    def toggle_day_night(self):
        self.day = not self.day
        if self.day:
            self.game.config(bg="skyblue")
            self.day_night_label.config(text="Day")
        else:
            self.game.config(bg="darkblue")
            self.day_night_label.config(text="Night")
        self.game.after(5000, self.toggle_day_night)  # Change every 5 seconds

    def decrease_thirst(self):
        if self.thirst > 0:
            # Decrease thirst faster if uploading
            self.thirst -= 2 if self.uploading else 1
            self.thirst_label.config(text=f"Thirst: {self.thirst}%")
        else:
            messagebox.showwarning("Dehydration", "You are dehydrated!")
        self.game.after(1000, self.decrease_thirst)  # Decrease every second

    def drink_water(self):
        self.thirst = 100
        self.thirst_label.config(text=f"Thirst: {self.thirst}%")
        messagebox.showinfo("Hydration", "You drank water!")

    def upload_video(self):
        if self.uploading:
            messagebox.showinfo("Upload", "Already uploading a video!")
            return

        self.uploading = True
        self.upload_button.config(state="disabled")
        self.progress_bar.place(relx=0.5, rely=0.8, anchor="center")
        self.progress_label.place(relx=0.5, rely=0.85, anchor="center")
        self.progress = 0

        self.upload_progress()

    def upload_progress(self):
        if self.progress < 100:
            self.progress += 10
            self.progress_bar['value'] = self.progress
            self.progress_label.config(text=f"Uploading... {self.progress}%")
            self.game.after(500, self.upload_progress)
        else:
            self.uploading = False
            self.progress_bar.place_forget()
            self.progress_label.place_forget()
            self.upload_button.config(state="normal")
            self.xp += 10
            self.coins += 5  # Award coins
            self.xp_label.config(text=f"XP: {self.xp}")
            self.coins_label.config(text=f"Coins: {self.coins}")
            messagebox.showinfo("Upload Complete", "Video uploaded! Gained 10 XP and 5 Coins.")

    def next_level(self):
        self.level += 1
        self.level_label.config(text=f"Level: {self.level}")
        self.coins += 10  # Award coins
        self.coins_label.config(text=f"Coins: {self.coins}")
        messagebox.showinfo("Level Up", f"Advanced to level {self.level} and gained 10 Coins")

    def sleep(self):
        self.thirst = 100
        self.thirst_label.config(text=f"Thirst: {self.thirst}%")
        # Advance time
        self.day = not self.day
        if self.day:
            self.game.config(bg="skyblue")
            self.day_night_label.config(text="Day")
        else:
            self.game.config(bg="darkblue")
            self.day_night_label.config(text="Night")
        messagebox.showinfo("Sleep", "You slept and feel refreshed!")

# Shop Window
class ShopWindow:
    def __init__(self, parent):
        self.parent = parent
        self.skins = {
            "Red": {"price": 20, "owned": False},
            "Green": {"price": 30, "owned": False},
            "Blue": {"price": 40, "owned": False},
        }
        self.create_shop_window()

    def create_shop_window(self):
        self.shop_window = tk.Toplevel(self.parent)
        self.shop_window.title("Shop")
        self.shop_window.geometry("400x300")

        tk.Label(self.shop_window, text="Shop - Buy Skins", font=("Arial", 16)).pack(pady=10)

        for skin, info in self.skins.items():
            frame = tk.Frame(self.shop_window)
            frame.pack(pady=5)

            skin_label = tk.Label(frame, text=f"Skin: {skin}", font=("Arial", 12))
            skin_label.pack(side="left", padx=10)

            status = "Owned" if info["owned"] else f"Price: {info['price']} Coins"
            status_label = tk.Label(frame, text=status, font=("Arial", 12))
            status_label.pack(side="left", padx=10)

            action_button = tk.Button(frame, text="Select" if info["owned"] else "Buy",
                                      command=lambda s=skin: self.buy_or_select_skin(s))
            action_button.pack(side="left", padx=10)

    def buy_or_select_skin(self, skin_name):
        skin_info = self.skins[skin_name]
        if skin_info["owned"]:
            # Select the skin
            self.parent.selected_skin = skin_name.lower()
            messagebox.showinfo("Skin Selected", f"You have selected the {skin_name} skin!")
            self.shop_window.destroy()
        else:
            # Attempt to buy the skin
            if self.parent.coins >= skin_info["price"]:
                self.parent.coins -= skin_info["price"]
                self.parent.coins_label.config(text=f"Coins: {self.parent.coins}")
                skin_info["owned"] = True
                messagebox.showinfo("Purchase Successful", f"You have purchased the {skin_name} skin!")
                self.shop_window.destroy()
                ShopWindow(self.parent)  # Re-open shop to update statuses
            else:
                messagebox.showwarning("Insufficient Coins", "You don't have enough coins to buy this skin.")

def start_game(selected_skin):
    main_menu.destroy()
    LevelEngineSimulator(selected_skin)

def open_shop():
    ShopWindow(main_menu)

# Main Menu
main_menu = tk.Tk()
main_menu.title("Levelengine Simulator - Main Menu")
main_menu.geometry("600x400")

selected_skin = "white"  # Default skin color

start_button = tk.Button(main_menu, text="Start Game", command=lambda: start_game(selected_skin), font=("Arial", 14))
start_button.pack(pady=50)

shop_button = tk.Button(main_menu, text="Shop", command=open_shop, font=("Arial", 14))
shop_button.pack(pady=10)

main_menu.mainloop()
