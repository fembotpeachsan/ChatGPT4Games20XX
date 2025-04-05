import tkinter as tk
from tkinter import ttk # For potential future styling, though not heavily used here
import pygame
import sys
import os
import random
from PIL import Image, ImageTk # Pillow library for image conversion

# --- Constants ---
# Window dimensions
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600

# Colors
NT_GREY = "#c0c0c0" # Classic Windows grey
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
TV_BORDER_COLOR = "#555555" # Dark grey for TV border

# Pong game area (relative to TV frame)
PONG_WIDTH = 300
PONG_HEIGHT = 200

# Paddle properties
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 40
PADDLE_SPEED = 4 # Speed for AI paddle

# Ball properties
BALL_SIZE = 8
BALL_SPEED_X = 2
BALL_SPEED_Y = 2

# Update delay (milliseconds)
GAME_UPDATE_DELAY = 16 # roughly 60 FPS

# --- Pygame Setup (No window needed here) ---
pygame.init()
# Create an off-screen surface for Pong
pong_surface = pygame.Surface((PONG_WIDTH, PONG_HEIGHT))

# --- Pong Game Variables ---
paddle_a_y = (PONG_HEIGHT - PADDLE_HEIGHT) // 2
paddle_b_y = (PONG_HEIGHT - PADDLE_HEIGHT) // 2
ball_x = PONG_WIDTH // 2 - BALL_SIZE // 2
ball_y = PONG_HEIGHT // 2 - BALL_SIZE // 2
ball_vel_x = random.choice([-BALL_SPEED_X, BALL_SPEED_X])
ball_vel_y = random.choice([-BALL_SPEED_Y, BALL_SPEED_Y])
score_a = 0
score_b = 0

# --- Tkinter Setup ---
root = tk.Tk()
root.title("Windows NT Pong TV")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.configure(bg=NT_GREY)
root.resizable(False, False) # Prevent resizing

# --- Main Frame ---
main_frame = tk.Frame(root, bg=NT_GREY, padx=10, pady=10)
main_frame.pack(fill=tk.BOTH, expand=True)

# --- TV Frame (Outer Border) ---
tv_outer_frame = tk.Frame(main_frame, bg=TV_BORDER_COLOR, bd=5, relief=tk.GROOVE)
# Center the TV frame - adjust padding as needed
tv_outer_frame.pack(pady=50) # Add padding to center vertically

# --- TV Screen Frame (Inner Area for Pygame) ---
# Using a Label to display the Pygame image
tv_screen_label = tk.Label(tv_outer_frame, bg="black", width=PONG_WIDTH, height=PONG_HEIGHT)
tv_screen_label.pack(padx=10, pady=10) # Padding inside the TV border

# --- Fake Taskbar ---
taskbar_frame = tk.Frame(root, bg=NT_GREY, height=30, bd=1, relief=tk.RAISED)
taskbar_frame.pack(side=tk.BOTTOM, fill=tk.X)

# Fake Start Button
start_button = tk.Button(taskbar_frame, text="Start", relief=tk.RAISED, width=8, state=tk.DISABLED) # Disabled look
start_button.pack(side=tk.LEFT, padx=5, pady=3)

# --- Game Update Function ---
def update_game():
    global paddle_a_y, paddle_b_y, ball_x, ball_y, ball_vel_x, ball_vel_y, score_a, score_b

    # --- Paddle A (Left) - Mouse Control ---
    # Get mouse position relative to the screen
    mouse_screen_y = root.winfo_pointery()
    # Get the top position of the tv_screen_label relative to the screen
    widget_screen_y = tv_screen_label.winfo_rooty()
    # Calculate mouse position relative to the tv_screen_label
    mouse_relative_y = mouse_screen_y - widget_screen_y
    # Center the paddle on the mouse cursor
    paddle_a_y = mouse_relative_y - PADDLE_HEIGHT // 2
    # Clamp paddle A position within the Pong area bounds
    paddle_a_y = max(0, min(PONG_HEIGHT - PADDLE_HEIGHT, paddle_a_y))


    # --- Paddle B (Right) - Simple AI ---
    target_b_y = ball_y - PADDLE_HEIGHT // 2
    if paddle_b_y < target_b_y and paddle_b_y + PADDLE_HEIGHT < PONG_HEIGHT:
        paddle_b_y += PADDLE_SPEED
    elif paddle_b_y > target_b_y and paddle_b_y > 0:
        paddle_b_y -= PADDLE_SPEED
    # Clamp paddle B position
    paddle_b_y = max(0, min(PONG_HEIGHT - PADDLE_HEIGHT, paddle_b_y))


    # --- Ball Movement ---
    ball_x += ball_vel_x
    ball_y += ball_vel_y

    # --- Collision Detection ---
    # Ball with top/bottom walls
    if ball_y <= 0 or ball_y >= PONG_HEIGHT - BALL_SIZE:
        ball_vel_y *= -1

    # Ball with paddles
    # Create Rect objects for collision detection in this frame
    ball_rect = pygame.Rect(ball_x, ball_y, BALL_SIZE, BALL_SIZE)
    paddle_a_rect = pygame.Rect(0, paddle_a_y, PADDLE_WIDTH, PADDLE_HEIGHT)
    paddle_b_rect = pygame.Rect(PONG_WIDTH - PADDLE_WIDTH, paddle_b_y, PADDLE_WIDTH, PADDLE_HEIGHT)

    if ball_rect.colliderect(paddle_a_rect) and ball_vel_x < 0:
        ball_vel_x *= -1
        # Optional: Adjust angle based on where it hits the paddle
        delta_y = ball_y + (BALL_SIZE / 2) - (paddle_a_y + PADDLE_HEIGHT / 2)
        # Increase sensitivity slightly for better control feel
        ball_vel_y = delta_y * 0.15

    elif ball_rect.colliderect(paddle_b_rect) and ball_vel_x > 0:
        ball_vel_x *= -1
        # Optional: Adjust angle based on where it hits the paddle
        delta_y = ball_y + (BALL_SIZE / 2) - (paddle_b_y + PADDLE_HEIGHT / 2)
        ball_vel_y = delta_y * 0.1 # Keep AI sensitivity lower


    # Ball out of bounds (scoring)
    if ball_x < 0:
        score_b += 1
        # Reset ball
        ball_x = PONG_WIDTH // 2 - BALL_SIZE // 2
        ball_y = PONG_HEIGHT // 2 - BALL_SIZE // 2
        ball_vel_x = BALL_SPEED_X # Start towards player B (AI)
        ball_vel_y = random.choice([-BALL_SPEED_Y, BALL_SPEED_Y])
    elif ball_x > PONG_WIDTH - BALL_SIZE:
        score_a += 1
        # Reset ball
        ball_x = PONG_WIDTH // 2 - BALL_SIZE // 2
        ball_y = PONG_HEIGHT // 2 - BALL_SIZE // 2
        ball_vel_x = -BALL_SPEED_X # Start towards player A (Mouse)
        ball_vel_y = random.choice([-BALL_SPEED_Y, BALL_SPEED_Y])

    # --- Drawing on Pygame Surface ---
    pong_surface.fill(BLACK) # Black background for Pong screen

    # Draw paddles
    pygame.draw.rect(pong_surface, WHITE, paddle_a_rect)
    pygame.draw.rect(pong_surface, WHITE, paddle_b_rect)

    # Draw ball
    pygame.draw.ellipse(pong_surface, WHITE, ball_rect) # Use ellipse for a rounder look

    # Draw middle line (optional)
    pygame.draw.line(pong_surface, WHITE, (PONG_WIDTH // 2, 0), (PONG_WIDTH // 2, PONG_HEIGHT), 1)

    # --- Convert Pygame surface to Tkinter PhotoImage ---
    # Get RGB string data from Pygame surface
    rgb_string = pygame.image.tostring(pong_surface, 'RGB')
    # Create a PIL Image from the raw data
    pil_image = Image.frombytes('RGB', (PONG_WIDTH, PONG_HEIGHT), rgb_string)
    # Convert PIL Image to Tkinter PhotoImage
    tk_photo = ImageTk.PhotoImage(image=pil_image)

    # --- Update Tkinter Label ---
    tv_screen_label.configure(image=tk_photo)
    tv_screen_label.image = tk_photo # Keep a reference! Important!

    # --- Schedule next update ---
    root.after(GAME_UPDATE_DELAY, update_game)

# --- Start the Game Loop ---
# Ensure the window is drawn once before starting the game loop
# to allow winfo_rooty() to get the correct initial value.
root.update()
update_game()


# --- Run Tkinter Main Loop ---
root.mainloop()

# --- Clean up Pygame ---
pygame.quit()
 
