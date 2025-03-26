#!/usr/bin/env python3
"""
Create Your Own Frisk - Tkinter Editor with Overworld and Battle System
=====================================================================

A Tkinter-based editor for designing Frisk-like overworlds and battles.
Features drag-and-drop for overworld elements and battle system design.
Outputs to test.py.

Usage:
    python frisk_engine.py
"""

import json
import tkinter as tk
from tkinter import messagebox, filedialog

class FriskEngineEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Create Your Own Frisk - Editor")
        self.root.geometry("800x600")

        # Data structures
        self.overworld_data = {"elements": []}  # {type: "frisk/kris/npc/item", x: int, y: int, name: str}
        self.battle_data = {"enemies": []}      # {name: str, hp: int, attack: int, defense: int, action: str}
        self.selected_char = "Frisk"            # Default character (Frisk or Kris)

        # UI Elements
        self.create_widgets()

    def create_widgets(self):
        # Title
        tk.Label(self.root, text="Create Your Own Frisk", font=("Arial", 16, "bold")).pack(pady=5)

        # Tabs for Overworld and Battle
        self.tab_frame = tk.Frame(self.root)
        self.tab_frame.pack(fill="x")
        tk.Button(self.tab_frame, text="Overworld", command=self.show_overworld).pack(side=tk.LEFT, padx=5)
        tk.Button(self.tab_frame, text="Battle System", command=self.show_battle).pack(side=tk.LEFT, padx=5)

        # Main Frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(expand=True, fill="both")

        # Character Selection
        tk.Label(self.main_frame, text="Select Character:").pack(pady=5)
        self.char_var = tk.StringVar(value="Frisk")
        tk.Radiobutton(self.main_frame, text="Frisk", variable=self.char_var, value="Frisk", command=self.update_char).pack(side=tk.LEFT)
        tk.Radiobutton(self.main_frame, text="Kris", variable=self.char_var, value="Kris", command=self.update_char).pack(side=tk.LEFT)

        # Overworld Canvas (initially visible)
        self.overworld_canvas = tk.Canvas(self.main_frame, width=400, height=300, bg="lightgray")
        self.overworld_canvas.pack(pady=10)
        self.overworld_canvas.bind("<B1-Motion>", self.drag_element)
        self.overworld_canvas.bind("<Button-1>", self.start_drag)

        # Overworld Controls
        self.overworld_controls = tk.Frame(self.main_frame)
        self.overworld_controls.pack()
        tk.Button(self.overworld_controls, text="Add Player", command=lambda: self.add_element(self.char_var.get())).pack(side=tk.LEFT, padx=5)
        tk.Button(self.overworld_controls, text="Add NPC", command=lambda: self.add_element("NPC")).pack(side=tk.LEFT, padx=5)
        tk.Button(self.overworld_controls, text="Add Item", command=lambda: self.add_element("Item")).pack(side=tk.LEFT, padx=5)

        # Battle Frame (hidden initially)
        self.battle_frame = tk.Frame(self.main_frame)
        self.battle_canvas = tk.Canvas(self.battle_frame, width=400, height=200, bg="white")
        self.battle_canvas.bind("<B1-Motion>", self.drag_battle_element)
        self.battle_canvas.bind("<Button-1>", self.start_battle_drag)

        # Battle Controls
        self.battle_controls = tk.Frame(self.battle_frame)
        tk.Button(self.battle_controls, text="Add Enemy", command=self.add_enemy).pack(side=tk.LEFT, padx=5)
        self.enemy_name = tk.Entry(self.battle_controls, width=10)
        self.enemy_name.pack(side=tk.LEFT, padx=5)
        self.enemy_name.insert(0, "Enemy")
        tk.Label(self.battle_controls, text="HP:").pack(side=tk.LEFT)
        self.enemy_hp = tk.Entry(self.battle_controls, width=5)
        self.enemy_hp.pack(side=tk.LEFT, padx=5)
        self.enemy_hp.insert(0, "50")
        tk.Label(self.battle_controls, text="ATK:").pack(side=tk.LEFT)
        self.enemy_atk = tk.Entry(self.battle_controls, width=5)
        self.enemy_atk.pack(side=tk.LEFT, padx=5)
        self.enemy_atk.insert(0, "5")
        tk.Label(self.battle_controls, text="DEF:").pack(side=tk.LEFT)
        self.enemy_def = tk.Entry(self.battle_controls, width=5)
        self.enemy_def.pack(side=tk.LEFT, padx=5)
        self.enemy_def.insert(0, "2")
        tk.Label(self.battle_controls, text="Action:").pack(side=tk.LEFT)
        self.enemy_action = tk.Entry(self.battle_controls, width=10)
        self.enemy_action.pack(side=tk.LEFT, padx=5)
        self.enemy_action.insert(0, "Attack")

        # Bottom Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Save", command=self.save_data).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Load", command=self.load_data).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Export to test.py", command=self.export_to_test).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Quit", command=self.root.quit).pack(side=tk.LEFT, padx=10)

        self.show_overworld()  # Start with overworld view

    def update_char(self):
        self.selected_char = self.char_var.get()

    def show_overworld(self):
        self.battle_frame.pack_forget()
        self.overworld_canvas.pack(pady=10)
        self.overworld_controls.pack()

    def show_battle(self):
        self.overworld_canvas.pack_forget()
        self.overworld_controls.pack_forget()
        self.battle_frame.pack()
        self.battle_canvas.pack(pady=10)
        self.battle_controls.pack()

    def start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def drag_element(self, event):
        for elem in self.overworld_data["elements"]:
            if abs(elem["x"] - self.drag_start_x) < 20 and abs(elem["y"] - self.drag_start_y) < 20:
                elem["x"] = event.x
                elem["y"] = event.y
                self.update_overworld()
                break

    def start_battle_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def drag_battle_element(self, event):
        for enemy in self.battle_data["enemies"]:
            if abs(enemy["x"] - self.drag_start_x) < 20 and abs(enemy["y"] - self.drag_start_y) < 20:
                enemy["x"] = event.x
                enemy["y"] = event.y
                self.update_battle()
                break

    def add_element(self, elem_type):
        name = f"{elem_type}_{len(self.overworld_data['elements']) + 1}"
        self.overworld_data["elements"].append({"type": elem_type, "x": 50, "y": 50, "name": name})
        self.update_overworld()

    def add_enemy(self):
        try:
            enemy = {
                "name": self.enemy_name.get(),
                "hp": int(self.enemy_hp.get()),
                "attack": int(self.enemy_atk.get()),
                "defense": int(self.enemy_def.get()),
                "action": self.enemy_action.get(),
                "x": 50,
                "y": 50
            }
            self.battle_data["enemies"].append(enemy)
            self.update_battle()
        except ValueError:
            messagebox.showerror("Error", "HP, Attack, and Defense must be integers!")

    def update_overworld(self):
        self.overworld_canvas.delete("all")
        for elem in self.overworld_data["elements"]:
            self.overworld_canvas.create_rectangle(
                elem["x"] - 10, elem["y"] - 10, elem["x"] + 10, elem["y"] + 10,
                fill="blue" if elem["type"] in ["Frisk", "Kris"] else "green" if elem["type"] == "NPC" else "yellow"
            )
            self.overworld_canvas.create_text(elem["x"], elem["y"], text=elem["name"], font=("Arial", 8))

    def update_battle(self):
        self.battle_canvas.delete("all")
        for enemy in self.battle_data["enemies"]:
            self.battle_canvas.create_oval(
                enemy["x"] - 10, enemy["y"] - 10, enemy["x"] + 10, enemy["y"] + 10, fill="red"
            )
            self.battle_canvas.create_text(enemy["x"], enemy["y"], text=enemy["name"], font=("Arial", 8))

    def save_data(self):
        data = {"overworld": self.overworld_data, "battle": self.battle_data}
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("Success", f"Saved to {file_path}")

    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.overworld_data = data["overworld"]
                self.battle_data = data["battle"]
                self.update_overworld()
                self.update_battle()
                messagebox.showinfo("Success", f"Loaded from {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load: {str(e)}")

    def export_to_test(self):
        test_code = """#!/usr/bin/env python3
# Generated test.py for Create Your Own Frisk
import json

overworld = {overworld}
battle = {battle}

print("Overworld Elements:")
for elem in overworld['elements']:
    print(f"{{elem['name']}} at ({{elem['x']}}, {{elem['y']}}) - Type: {{elem['type']}}")

print("\\nBattle Enemies:")
for enemy in battle['enemies']:
    print(f"{{enemy['name']}}: HP={{enemy['hp']}}, ATK={{enemy['attack']}}, DEF={{enemy['defense']}}, Action={{enemy['action']}}")
"""
        with open("test.py", "w", encoding="utf-8") as f:
            f.write(test_code.format(overworld=repr(self.overworld_data), battle=repr(self.battle_data)))
        messagebox.showinfo("Success", "Exported to test.py")

def main():
    root = tk.Tk()
    app = FriskEngineEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
