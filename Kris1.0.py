#!/usr/bin/env python3
"""
Create Your Own Kris - Tkinter Engine Editor
===========================================

A simple Tkinter-based editor for creating Kris-like characters or encounters.
Features include editing properties, saving to a file, and loading from a file.

Usage:
    python kris_engine.py
"""

import os
import json
import tkinter as tk
from tkinter import messagebox, filedialog

class KrisEngineEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Create Your Own Kris - Editor")
        self.root.geometry("600x400")

        # Kris data structure (editable properties)
        self.kris_data = {
            "name": "Kris",
            "hp": 100,
            "attack": 10,
            "defense": 5,
            "sprite": "default_kris.png",
            "description": "A mysterious hero."
        }

        # UI Elements
        self.create_widgets()

    def create_widgets(self):
        # Title
        tk.Label(self.root, text="Create Your Own Kris", font=("Arial", 16, "bold")).pack(pady=10)

        # Frame for editing properties
        edit_frame = tk.Frame(self.root)
        edit_frame.pack(pady=10)

        # Name
        tk.Label(edit_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(edit_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.name_entry.insert(0, self.kris_data["name"])

        # HP
        tk.Label(edit_frame, text="HP:").grid(row=1, column=0, padx=5, pady=5)
        self.hp_entry = tk.Entry(edit_frame)
        self.hp_entry.grid(row=1, column=1, padx=5, pady=5)
        self.hp_entry.insert(0, self.kris_data["hp"])

        # Attack
        tk.Label(edit_frame, text="Attack:").grid(row=2, column=0, padx=5, pady=5)
        self.attack_entry = tk.Entry(edit_frame)
        self.attack_entry.grid(row=2, column=1, padx=5, pady=5)
        self.attack_entry.insert(0, self.kris_data["attack"])

        # Defense
        tk.Label(edit_frame, text="Defense:").grid(row=3, column=0, padx=5, pady=5)
        self.defense_entry = tk.Entry(edit_frame)
        self.defense_entry.grid(row=3, column=1, padx=5, pady=5)
        self.defense_entry.insert(0, self.kris_data["defense"])

        # Sprite
        tk.Label(edit_frame, text="Sprite:").grid(row=4, column=0, padx=5, pady=5)
        self.sprite_entry = tk.Entry(edit_frame)
        self.sprite_entry.grid(row=4, column=1, padx=5, pady=5)
        self.sprite_entry.insert(0, self.kris_data["sprite"])

        # Description
        tk.Label(edit_frame, text="Description:").grid(row=5, column=0, padx=5, pady=5)
        self.desc_entry = tk.Text(edit_frame, height=3, width=30)
        self.desc_entry.grid(row=5, column=1, padx=5, pady=5)
        self.desc_entry.insert("1.0", self.kris_data["description"])

        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Save", command=self.save_data).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Load", command=self.load_data).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Apply", command=self.apply_changes).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Quit", command=self.root.quit).pack(side=tk.LEFT, padx=10)

    def apply_changes(self):
        """Apply the changes from the UI to the kris_data dictionary."""
        try:
            self.kris_data["name"] = self.name_entry.get()
            self.kris_data["hp"] = int(self.hp_entry.get())
            self.kris_data["attack"] = int(self.attack_entry.get())
            self.kris_data["defense"] = int(self.defense_entry.get())
            self.kris_data["sprite"] = self.sprite_entry.get()
            self.kris_data["description"] = self.desc_entry.get("1.0", tk.END).strip()
            messagebox.showinfo("Success", "Changes applied successfully!")
        except ValueError:
            messagebox.showerror("Error", "HP, Attack, and Defense must be integers!")

    def save_data(self):
        """Save the current kris_data to a JSON file."""
        self.apply_changes()  # Ensure latest changes are applied
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.kris_data, f, indent=4)
            messagebox.showinfo("Success", f"Saved to {file_path}")

    def load_data(self):
        """Load kris_data from a JSON file and update the UI."""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.kris_data = json.load(f)
                # Update UI
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, self.kris_data["name"])
                self.hp_entry.delete(0, tk.END)
                self.hp_entry.insert(0, self.kris_data["hp"])
                self.attack_entry.delete(0, tk.END)
                self.attack_entry.insert(0, self.kris_data["attack"])
                self.defense_entry.delete(0, tk.END)
                self.defense_entry.insert(0, self.kris_data["defense"])
                self.sprite_entry.delete(0, tk.END)
                self.sprite_entry.insert(0, self.kris_data["sprite"])
                self.desc_entry.delete("1.0", tk.END)
                self.desc_entry.insert("1.0", self.kris_data["description"])
                messagebox.showinfo("Success", f"Loaded from {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")

def main():
    root = tk.Tk()
    app = KrisEngineEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
