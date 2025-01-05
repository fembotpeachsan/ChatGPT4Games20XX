import tkinter as tk
from tkinter import ttk, messagebox

class WawaSims2025:
    def __init__(self, root):
        self.root = root
        self.root.title("Wawa Sims 2025")  # Set the title of the window

        # Initialize the pet's energy level (0 to 100)
        self.energy_level = 50

        # Create a label for the game title
        self.title_label = tk.Label(root, text="Welcome to Wawa Sims 2025!", font=("Arial", 24))
        self.title_label.pack(pady=20)

        # Create a progress bar to track the pet's energy level
        self.energy_progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.energy_progress.pack(pady=10)
        self.energy_progress["value"] = self.energy_level  # Set initial value

        # Create a label to display the energy level
        self.energy_label = tk.Label(root, text=f"Energy: {self.energy_level}%", font=("Arial", 14))
        self.energy_label.pack(pady=10)

        # Create a button to feed the pet
        self.feed_button = tk.Button(root, text="Feed Your Wa Wa", command=self.feed_pet, bg="lightblue", fg="black")
        self.feed_button.pack(pady=10)

        # Create a button to walk the pet
        self.walk_button = tk.Button(root, text="Walk Your Wa Wa", command=self.walk_pet, bg="lightgreen", fg="black")
        self.walk_button.pack(pady=10)

        # Create a button to put the pet to sleep
        self.sleep_button = tk.Button(root, text="Put Your Wa Wa to Sleep", command=self.put_to_sleep, bg="lavender", fg="black")
        self.sleep_button.pack(pady=10)

        # Create a button to exit the game
        self.exit_button = tk.Button(root, text="Exit", command=self.exit_game, bg="red", fg="white")
        self.exit_button.pack(pady=10)

    # Function to feed the pet
    def feed_pet(self):
        if self.energy_level < 100:
            self.energy_level += 10  # Increase energy by 10%
            if self.energy_level > 100:
                self.energy_level = 100  # Cap energy at 100%
            self.update_energy()
            messagebox.showinfo("Feed Your Wa Wa", "Your Wa Wa has been fed! Energy +10%")
        else:
            messagebox.showinfo("Feed Your Wa Wa", "Your Wa Wa is already full!")

    # Function to walk the pet
    def walk_pet(self):
        if self.energy_level > 0:
            self.energy_level -= 10  # Decrease energy by 10%
            if self.energy_level < 0:
                self.energy_level = 0  # Cap energy at 0%
            self.update_energy()
            messagebox.showinfo("Walk Your Wa Wa", "Your Wa Wa has been walked! Energy -10%")
        else:
            messagebox.showinfo("Walk Your Wa Wa", "Your Wa Wa is too tired to walk!")

    # Function to put the pet to sleep
    def put_to_sleep(self):
        if self.energy_level < 100:
            self.energy_level += 20  # Increase energy by 20%
            if self.energy_level > 100:
                self.energy_level = 100  # Cap energy at 100%
            self.update_energy()
            messagebox.showinfo("Put Your Wa Wa to Sleep", "Your Wa Wa is now sleeping! Energy +20%")
        else:
            messagebox.showinfo("Put Your Wa Wa to Sleep", "Your Wa Wa is already fully rested!")

    # Function to update the progress bar and energy label
    def update_energy(self):
        self.energy_progress["value"] = self.energy_level
        self.energy_label.config(text=f"Energy: {self.energy_level}%")

    # Function to exit the game
    def exit_game(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.destroy()

# Main function to run the application
if __name__ == "__main__":
    root = tk.Tk()  # Create the main window
    app = WawaSims2025(root)  # Instantiate the application
    root.mainloop()  # Start the main event loops