# N64 Pong Game
# Assembled with modern MIPS assembler compatible with N64 SDK

.include "n64.inc"  # Include N64 hardware definitions

# === Data Section ===
.data
.align 4

# Game State Variables
ball_x:         .word 320    # Ball X position
ball_y:         .word 120    # Ball Y position
ball_vel_x:     .word 2      # Ball X velocity
ball_vel_y:     .word 1      # Ball Y velocity
left_paddle_y:  .word 100    # Left paddle Y position
right_paddle_y: .word 100    # Right paddle Y position
player1_score:  .word 0      # Player 1 score
player2_score:  .word 0      # Player 2 score
game_state:     .word 0      # 0 = title, 1 = playing, 2 = game over

# Constants
LEFT_PADDLE_X   = 50         # Left paddle X position
RIGHT_PADDLE_X  = 570        # Right paddle X position
PADDLE_HEIGHT   = 40         # Paddle height
PADDLE_SPEED    = 3          # Paddle movement speed
BALL_SIZE       = 4          # Ball size
SCREEN_WIDTH    = 640        # Screen width
SCREEN_HEIGHT   = 480        # Screen height
FRAMEBUFFER     = 0xA0100000 # RDRAM framebuffer address

# Color Constants
WHITE           = 0xFFFFFFFF
RED             = 0xFF0000FF
BLUE            = 0x0000FFFF
BLACK           = 0x000000FF

# Text/UI Resources
title_text:     .asciiz "N64 PONG"
start_text:     .asciiz "PRESS START"
score_text:     .asciiz "PLAYER 1:    PLAYER 2:   "
game_over_text: .asciiz "GAME OVER"

# Sound effect data would go here if we had actual samples

# === Code Section ===
.text
.align 4
.global _start

_start:
    # Initialize the N64 hardware
    jal init_hardware
    
    # Initialize the game
    jal init_game
    
    # Main game loop
main_loop:
    # Wait for VSync
    jal wait_vsync
    
    # Read controller inputs
    jal read_controllers
    
    # Update game state
    jal update_game
    
    # Render frame
    jal render_frame
    
    j main_loop

# Initialize N64 hardware
init_hardware:
    # Save return address
    addi $sp, $sp, -4
    sw $ra, 0($sp)
    
    # Initialize VI (Video Interface)
    li $t0, VI_BASE_REG
    li $t1, SCREEN_WIDTH
    sw $t1, VI_WIDTH($t0)
    
    # Set up framebuffer address
    li $t1, FRAMEBUFFER
    sw $t1, VI_ORIGIN($t0)
    
    # Set VI control register for 16-bit color
    li $t1, VI_CTRL_TYPE_16 | VI_CTRL_GAMMA_ON | VI_CTRL_ANTIALIAS_ON
    sw $t1, VI_CONTROL($t0)
    
    # Set up VI interrupt
    li $t0, MI_BASE_REG
    li $t1, MI_INTR_MASK_VI
    sw $t1, MI_INTR_MASK($t0)
    
    # Initialize AI (Audio Interface) - basic setup
    li $t0, AI_BASE_REG
    li $t1, AI_CONTROL_DMA_ON
    sw $t1, AI_CONTROL($t0)
    
    # Initialize PI (Peripheral Interface) for controllers
    li $t0, PI_BASE_REG
    li $t1, PI_STATUS_RESET
    sw $t1, PI_STATUS($t0)
    
    # Restore return address and return
    lw $ra, 0($sp)
    addi $sp, $sp, 4
    jr $ra

# Initialize game state
init_game:
    # Save return address
    addi $sp, $sp, -4
    sw $ra, 0($sp)
    
    # Set initial game state (title screen)
    li $t0, 0
    sw $t0, game_state
    
    # Reset scores
    sw $zero, player1_score
    sw $zero, player2_score
    
    # Set ball to center position
    li $t0, 320
    sw $t0, ball_x
    li $t0, 120
    sw $t0, ball_y
    
    # Set initial ball velocity (random direction)
    jal random_seed    # Get a pseudo-random value in $v0
    andi $t0, $v0, 1   # Get lowest bit
    beqz $t0, ball_right
    li $t0, -2
    j save_ball_vx
ball_right:
    li $t0, 2
save_ball_vx:
    sw $t0, ball_vel_x
    
    # Randomize Y velocity too
    jal random_seed
    andi $t0, $v0, 1
    beqz $t0, ball_down
    li $t0, -1
    j save_ball_vy
ball_down:
    li $t0, 1
save_ball_vy:
    sw $t0, ball_vel_y
    
    # Reset paddles
    li $t0, 100
    sw $t0, left_paddle_y
    sw $t0, right_paddle_y
    
    # Restore return address and return
    lw $ra, 0($sp)
    addi $sp, $sp, 4
    jr $ra

# Wait for vertical sync
wait_vsync:
    # Read VI current line
    li $t0, VI_BASE_REG
vsync_loop:
    lw $t1, VI_V_CURRENT($t0)
    andi $t1, $t1, 0x3FF
    bne $t1, $zero, vsync_loop  # Wait until we hit line 0
    jr $ra

# Read controller inputs
read_controllers:
    # Read controller 1 (Player 1)
    li $t0, CONT1_BASE
    lw $t1, CONT_BUTTONS($t0)   # Get button state
    
    # Check for up/down input for left paddle
    andi $t2, $t1, CONT_UP
    beqz $t2, check_p1_down
    # Move paddle up
    lw $t3, left_paddle_y
    subi $t3, $t3, PADDLE_SPEED
    # Ensure paddle stays on screen
    bltz $t3, p1_clamp_top
    j save_p1_y
p1_clamp_top:
    li $t3, 0
save_p1_y:
    sw $t3, left_paddle_y
    
check_p1_down:
    andi $t2, $t1, CONT_DOWN
    beqz $t2, check_start_button
    # Move paddle down
    lw $t3, left_paddle_y
    addi $t3, $t3, PADDLE_SPEED
    # Ensure paddle stays on screen
    addi $t4, $t3, PADDLE_HEIGHT
    li $t5, SCREEN_HEIGHT
    blt $t4, $t5, save_p1_y_down
    sub $t3, $t5, PADDLE_HEIGHT
save_p1_y_down:
    sw $t3, left_paddle_y
    
check_start_button:
    # Check if START button pressed (to begin game from title)
    andi $t2, $t1, CONT_START
    beqz $t2, read_cont2
    # If on title screen, start the game
    lw $t3, game_state
    bnez $t3, read_cont2  # Only respond to START on title screen
    li $t3, 1             # Set game state to playing
    sw $t3, game_state
    
read_cont2:
    # Read controller 2 (Player 2 or AI)
    li $t0, CONT2_BASE
    lw $t1, CONT_BUTTONS($t0)
    
    # Check if player 2 controller is connected
    andi $t2, $t1, CONT_PRESENT
    beqz $t2, ai_control  # If no controller, use AI
    
    # Check for up/down input for right paddle
    andi $t2, $t1, CONT_UP
    beqz $t2, check_p2_down
    # Move paddle up
    lw $t3, right_paddle_y
    subi $t3, $t3, PADDLE_SPEED
    # Ensure paddle stays on screen
    bltz $t3, p2_clamp_top
    j save_p2_y
p2_clamp_top:
    li $t3, 0
save_p2_y:
    sw $t3, right_paddle_y
    
check_p2_down:
    andi $t2, $t1, CONT_DOWN
    beqz $t2, controller_done
    # Move paddle down
    lw $t3, right_paddle_y
    addi $t3, $t3, PADDLE_SPEED
    # Ensure paddle stays on screen
    addi $t4, $t3, PADDLE_HEIGHT
    li $t5, SCREEN_HEIGHT
    blt $t4, $t5, save_p2_y_down
    sub $t3, $t5, PADDLE_HEIGHT
save_p2_y_down:
    sw $t3, right_paddle_y
    j controller_done
    
ai_control:
    # Simple AI follows the ball
    lw $t0, ball_y
    lw $t1, right_paddle_y
    addi $t2, $t1, PADDLE_HEIGHT/2  # Paddle center point
    
    # Move toward ball
    blt $t0, $t2, ai_move_up
    bgt $t0, $t2, ai_move_down
    j controller_done  # Ball is aligned with paddle center
    
ai_move_up:
    # Move paddle up
    subi $t1, $t1, PADDLE_SPEED/2  # AI moves at half speed
    # Ensure paddle stays on screen
    bltz $t1, ai_clamp_top
    j save_ai_y
ai_clamp_top:
    li $t1, 0
save_ai_y:
    sw $t1, right_paddle_y
    j controller_done
    
ai_move_down:
    # Move paddle down
    addi $t1, $t1, PADDLE_SPEED/2  # AI moves at half speed
    # Ensure paddle stays on screen
    addi $t4, $t1, PADDLE_HEIGHT
    li $t5, SCREEN_HEIGHT
    blt $t4, $t5, save_ai_y_down
    sub $t1, $t5, PADDLE_HEIGHT
save_ai_y_down:
    sw $t1, right_paddle_y
    
controller_done:
    jr $ra

# Update game state
update_game:
    # Check current game state
    lw $t0, game_state
    beq $t0, $zero, title_screen_update  # Title screen
    beq $t0, 1, playing_update          # Playing
    beq $t0, 2, game_over_update        # Game over
    jr $ra  # Unknown state, just return
    
title_screen_update:
    # Title screen has no updates except for controller input
    jr $ra
    
playing_update:
    # Update ball position based on velocity
    lw $t0, ball_x
    lw $t1, ball_vel_x
    add $t0, $t0, $t1
    sw $t0, ball_x
    
    lw $t0, ball_y
    lw $t1, ball_vel_y
    add $t0, $t0, $t1
    sw $t0, ball_y
    
    # Check for collisions with top/bottom of screen
    lw $t0, ball_y
    ble $t0, 0, bounce_top
    addi $t1, $t0, BALL_SIZE
    li $t2, SCREEN_HEIGHT
    bge $t1, $t2, bounce_bottom
    j check_paddle_collision
    
bounce_top:
    # Bounce off top of screen
    li $t0, 0
    sw $t0, ball_y
    lw $t0, ball_vel_y
    neg $t0, $t0      # Reverse Y velocity
    sw $t0, ball_vel_y
    j check_paddle_collision
    
bounce_bottom:
    # Bounce off bottom of screen
    li $t0, SCREEN_HEIGHT
    subi $t0, $t0, BALL_SIZE
    sw $t0, ball_y
    lw $t0, ball_vel_y
    neg $t0, $t0      # Reverse Y velocity
    sw $t0, ball_vel_y
    
check_paddle_collision:
    # Check for collision with left paddle
    lw $t0, ball_x
    ble $t0, LEFT_PADDLE_X, check_left_paddle_y
    j check_right_paddle
    
check_left_paddle_y:
    addi $t1, $t0, BALL_SIZE      # Ball right edge
    blt $t1, LEFT_PADDLE_X, check_right_paddle  # Ball is to left of paddle
    
    subi $t1, LEFT_PADDLE_X, BALL_SIZE
    bgt $t0, $t1, check_left_paddle_height  # Ball is within X range of paddle
    j check_right_paddle
    
check_left_paddle_height:
    # Check if ball Y position overlaps with paddle
    lw $t0, ball_y
    lw $t1, left_paddle_y
    blt $t0, $t1, check_right_paddle  # Ball above paddle
    
    lw $t0, ball_y
    addi $t0, $t0, BALL_SIZE      # Ball bottom edge
    lw $t1, left_paddle_y
    addi $t1, $t1, PADDLE_HEIGHT  # Paddle bottom edge
    bgt $t0, $t1, check_right_paddle  # Ball below paddle
    
    # Ball hit left paddle, bounce!
    lw $t0, ball_vel_x
    neg $t0, $t0                  # Reverse X velocity
    addi $t0, $t0, 1              # Increase speed slightly
    sw $t0, ball_vel_x
    
    # Adjust Y velocity based on where ball hit paddle (for angle)
    lw $t0, ball_y
    addi $t0, $t0, BALL_SIZE/2    # Ball center
    lw $t1, left_paddle_y
    addi $t1, $t1, PADDLE_HEIGHT/2  # Paddle center
    sub $t0, $t0, $t1             # Difference from center
    
    # Normalize to range -2 to 2 for Y velocity
    sra $t0, $t0, 4               # Divide by 16 to scale down
    lw $t1, ball_vel_y
    add $t1, $t1, $t0             # Add angle adjustment
    
    # Ensure Y velocity is not zero
    beqz $t1, fix_zero_y_vel
    j save_new_y_vel
fix_zero_y_vel:
    li $t1, 1
save_new_y_vel:
    sw $t1, ball_vel_y
    
    # Sound effect for paddle hit would go here
    j check_score
    
check_right_paddle:
    # Check for collision with right paddle
    lw $t0, ball_x
    addi $t0, $t0, BALL_SIZE      # Ball right edge
    bge $t0, RIGHT_PADDLE_X, check_right_paddle_y
    j check_score
    
check_right_paddle_y:
    subi $t1, $t0, BALL_SIZE
    bgt $t1, RIGHT_PADDLE_X, check_score  # Ball is to right of paddle
    
    addi $t1, RIGHT_PADDLE_X, BALL_SIZE
    blt $t0, $t1, check_right_paddle_height  # Ball is within X range of paddle
    j check_score
    
check_right_paddle_height:
    # Check if ball Y position overlaps with paddle
    lw $t0, ball_y
    lw $t1, right_paddle_y
    blt $t0, $t1, check_score  # Ball above paddle
    
    lw $t0, ball_y
    addi $t0, $t0, BALL_SIZE      # Ball bottom edge
    lw $t1, right_paddle_y
    addi $t1, $t1, PADDLE_HEIGHT  # Paddle bottom edge
    bgt $t0, $t1, check_score     # Ball below paddle
    
    # Ball hit right paddle, bounce!
    lw $t0, ball_vel_x
    neg $t0, $t0                  # Reverse X velocity
    subi $t0, $t0, 1              # Increase speed slightly
    sw $t0, ball_vel_x
    
    # Adjust Y velocity based on where ball hit paddle (for angle)
    lw $t0, ball_y
    addi $t0, $t0, BALL_SIZE/2    # Ball center
    lw $t1, right_paddle_y
    addi $t1, $t1, PADDLE_HEIGHT/2  # Paddle center
    sub $t0, $t0, $t1             # Difference from center
    
    # Normalize to range -2 to 2 for Y velocity
    sra $t0, $t0, 4               # Divide by 16 to scale down
    lw $t1, ball_vel_y
    add $t1, $t1, $t0             # Add angle adjustment
    
    # Ensure Y velocity is not zero
    beqz $t1, fix_zero_y_vel_right
    j save_new_y_vel_right
fix_zero_y_vel_right:
    li $t1, 1
save_new_y_vel_right:
    sw $t1, ball_vel_y
    
    # Sound effect for paddle hit would go here
    
check_score:
    # Check if ball has gone off either edge
    lw $t0, ball_x
    ble $t0, 0, player2_scores
    addi $t1, $t0, BALL_SIZE
    li $t2, SCREEN_WIDTH
    bge $t1, $t2, player1_scores
    j update_done    # Ball still in play
    
player1_scores:
    # Player 1 scored a point
    lw $t0, player1_score
    addi $t0, $t0, 1
    sw $t0, player1_score
    
    # Check if game over (e.g., score >= 10)
    li $t1, 10
    bge $t0, $t1, game_over
    
    # Reset ball to center
    jal reset_ball
    
    # Sound effect for scoring would go here
    j update_done
    
player2_scores:
    # Player 2 scored a point
    lw $t0, player2_score
    addi $t0, $t0, 1
    sw $t0, player2_score
    
    # Check if game over (e.g., score >= 10)
    li $t1, 10
    bge $t0, $t1, game_over
    
    # Reset ball to center
    jal reset_ball
    
    # Sound effect for scoring would go here
    j update_done
    
game_over:
    # Set game state to game over
    li $t0, 2
    sw $t0, game_state
    j update_done
    
game_over_update:
    # Wait for START button to return to title
    # Already handled in read_controllers
    
update_done:
    jr $ra

# Reset ball to center with new trajectory
reset_ball:
    # Save return address
    addi $sp, $sp, -4
    sw $ra, 0($sp)
    
    # Center the ball
    li $t0, 320
    sw $t0, ball_x
    li $t0, 120
    sw $t0, ball_y
    
    # Randomize direction
    jal random_seed
    andi $t0, $v0, 1
    beqz $t0, reset_ball_right
    li $t0, -2
    j reset_save_vx
reset_ball_right:
    li $t0, 2
reset_save_vx:
    sw $t0, ball_vel_x
    
    jal random_seed
    andi $t0, $v0, 1
    beqz $t0, reset_ball_down
    li $t0, -1
    j reset_save_vy
reset_ball_down:
    li $t0, 1
reset_save_vy:
    sw $t0, ball_vel_y
    
    # Small delay before continuing
    li $t0, 1000000
reset_delay:
    subi $t0, $t0, 1
    bnez $t0, reset_delay
    
    # Restore return address and return
    lw $ra, 0($sp)
    addi $sp, $sp, 4
    jr $ra

# Simple pseudo-random number generator
random_seed:
    # We use a linear congruential generator: X_n+1 = (aX_n + c) mod m
    # Constants: a=1664525, c=1013904223, m=2^32
    li $t0, 1664525
    li $t1, 1013904223
    
    # Get current time as seed
    li $v0, 12  # SYSCALL: get time
    syscall
    
    # Calculate next value
    mul $v0, $v0, $t0
    add $v0, $v0, $t1
    
    jr $ra

# Render a frame
render_frame:
    # Clear screen to black
    jal clear_screen
    
    # Check game state and render appropriate screen
    lw $t0, game_state
    beq $t0, $zero, render_title_screen
    beq $t0, 1, render_gameplay
    beq $t0, 2, render_game_over
    jr $ra  # Unknown state, just return
    
render_title_screen:
    # Draw title and start message
    la $a0, title_text
    li $a1, 260
    li $a2, 100
    li $a3, WHITE
    jal draw_text
    
    la $a0, start_text
    li $a1, 240
    li $a2, 200
    li $a3, WHITE
    jal draw_text
    
    # Draw paddles and ball for visual effect
    li $t2, LEFT_PADDLE_X
    lw $t3, left_paddle_y
    li $t7, WHITE
    jal draw_paddle
    
    li $t2, RIGHT_PADDLE_X
    lw $t3, right_paddle_y
    li $t7, WHITE
    jal draw_paddle
    
    lw $t2, ball_x
    lw $t3, ball_y
    li $t7, WHITE
    jal draw_ball
    
    jr $ra
    
render_gameplay:
    # Draw scores
    la $a0, score_text
    li $a1, 200
    li $a2, 20
    li $a3, WHITE
    jal draw_text
    
    # Draw player 1 score
    lw $a0, player1_score
    li $a1, 270
    li $a2, 20
    li $a3, WHITE
    jal draw_number
    
    # Draw player 2 score
    lw $a0, player2_score
    li $a1, 400
    li $a2, 20
    li $a3, WHITE
    jal draw_number
    
    # Draw center line
    li $t2, 320
    li $t3, 0
    li $t4, 480
    li $t7, WHITE
    jal draw_dashed_line
    
    # Draw paddles
    li $t2, LEFT_PADDLE_X
    lw $t3, left_paddle_y
    li $t7, BLUE
    jal draw_paddle
    
    li $t2, RIGHT_PADDLE_X
    lw $t3, right_paddle_y
    li $t7, RED
    jal draw_paddle
    
    # Draw ball
    lw $t2, ball_x
    lw $t3, ball_y
    li $t7, WHITE
    jal draw_ball
    
    jr $ra
    
render_game_over:
    # Draw game over message
    la $a0, game_over_text
    li $a1, 250
    li $a2, 100
    li $a3, WHITE
    jal draw_text
    
    # Draw final scores
    la $a0, score_text
    li $a1, 200
    li $a2, 160
    li $a3, WHITE
    jal draw_text
    
    # Draw player 1 score
    lw $a0, player1_score
    li $a1, 270
    li $a2, 160
    li $a3, WHITE
    jal draw_number
    
    # Draw player 2 score
    lw $a0, player2_score
    li $a1, 400
    li $a2, 160
    li $a3, WHITE
    jal draw_number
    
    # Draw winner message
    lw $t0, player1_score
    lw $t1, player2_score
    bgt $t0, $t1, p1_winner
    # Player 2 wins
    la $a0, "PLAYER 2 WINS!"
    j draw_winner
p1_winner:
    la $a0, "PLAYER 1 WINS!"
draw_winner:
    li $a1, 240
    li $a2, 200
    li $a3, WHITE
    jal draw_text
    
    # Draw restart message
    la $a0, "PRESS START TO PLAY AGAIN"
    li $a1, 160
    li $a2, 240
    li $a3, WHITE
    jal draw_text
    
    jr $ra

# Clear screen to black
clear_screen:
    li $t0, FRAMEBUFFER    # Start of framebuffer
    li $t1, SCREEN_WIDTH
    li $t2, SCREEN_HEIGHT
    mul $t1, $t1, $t2      # Total number of pixels
    li $t2, BLACK          # Color to fill (black)
    
clear_loop:
    sw $t2, 0($t0)         # Write pixel color
    addi $t0, $t0, 4       # Move to next pixel
    subi $t1, $t1, 1       # Decrement counter
    bnez $t1, clear_loop   # Continue until all pixels filled
    
    jr $ra

# Function: Draw a paddle
# $t2 = X position, $t3 = Y position, $t7 = Color
draw_paddle:
    li $t4, 10            # Paddle width
    li $t5, PADDLE_HEIGHT # Paddle height
    
    # Calculate starting address
    li $t0, FRAMEBUFFER
    mul $t1, $t3, SCREEN_WIDTH
    add $t1, $t1, $t2
    sll $t1, $t1, 2      # 4 bytes per pixel
    add $t0, $t0, $t1
    
paddle_y_loop:
    move $t6, $t4        # Reset width counter
    move $t1, $t0        # Reset to start of current row
    
paddle_x_loop:
    sw $t7, 0($t1)       # Draw pixel
    addi $t1, $t1, 4     # Next pixel in row
    subi $t6, $t6, 1     # Decrement width counter
    bnez $t6, paddle_x_loop
    
    # Move to next row
    addi $t0, $t0, SCREEN_WIDTH * 4
    subi $t5, $t5, 1     # Decrement height counter
    bnez $t5, paddle_y_loop
    
    jr $ra

# Function: Draw a ball
# $t2 = X position, $t3 = Y position, $t7 = Color
draw_ball:
    li $t4, BALL_SIZE    # Ball width and height
    li $t5, BALL_SIZE
    
    # Calculate starting address
    li $t0, FRAMEBUFFER
    mul $t1, $t3, SCREEN_WIDTH
    add $t1, $t1, $t2
    sll $t1, $t1, 2      # 4 bytes per pixel
    add $t0, $t0, $t1
    
ball_y_loop:
    move $t6, $t4        # Reset width counter
    move $t1, $t0        # Reset to start of current row
    
ball_x_loop:
    sw $t7, 0($t1)       # Draw pixel
    addi $t1, $t1, 4     # Next pixel in row
    subi $t6, $t6, 1     # Decrement width counter
    bnez $t6, ball_x_loop
    
    # Move to next row
    addi $t0, $t0, SCREEN_WIDTH * 4
    subi $t5, $t5, 1     # Decrement height counter
    bnez $t5, ball_y_loop
    
    jr $ra

# Draw dashed center line
# $t2 = X position, $t3 = Y start, $t4 = Y end, $t7 = Color
draw_dashed_line:
    # Calculate starting address
    li $t0, FRAMEBUFFER
    mul $t1, $t3, SCREEN_WIDTH
    add $t1, $t1, $t2
    sll $t1, $t1, 2      # 4 bytes per pixel
    add $t0, $t0, $t1
    
    li $t5, 0            # Counter for dash pattern
    
dashed_line_loop:
    # Draw 5 pixels, then skip 5 pixels (dashed pattern)
    andi $t5, $t5, 0x0F  # Modulo 16
    bge $t5, 8, skip_dash
    
    # Draw pixel
    sw $t7, 0($t0)
    
skip_dash:
    # Move to next position
    addi $t0, $t0, SCREEN_WIDTH * 4
    addi $t5, $t5, 1     # Increment dash counter
    
    addi $t3, $t3, 1     # Increment Y position
    blt $t3, $t4, dashed_line_loop
    
    jr $ra

# Draw simple text
# $a0 = Text pointer, $a1 = X position, $a2 = Y position, $a3 = Color
draw_text:
    # This is a simplified text renderer (would be more complex in a real N64 game)
    # In reality, N64 games would use sprites or textures for text rendering
    # Here, we'll just simulate a simple text renderer
    
    move $t0, $a0        # Text pointer
    move $t1, $a1        # X position
    move $t2, $a2        # Y position
    move $t7, $a3        # Color
    
text_loop:
    lb $t3, 0($t0)       # Get next character
    beqz $t3, text_done  # If null terminator, we're done
    
    # Draw a simple 8x8 character (simplified)
    li $t4, FRAMEBUFFER
    mul $t5, $t2, SCREEN_WIDTH
    add $t5, $t5, $t1
    sll $t5, $t5, 2      # 4 bytes per pixel
    add $t4, $t4, $t5
    
    # Draw a simple box for each character (8x8 pixels)
    li $t5, 8            # Character height
char_y_loop:
    li $t6, 8            # Character width
    move $t9, $t4        # Reset to start of current row
    
char_x_loop:
    sw $t7, 0($t9)       # Draw pixel
    addi $t9, $t9, 4     # Next pixel
    subi $t6, $t6, 1
    bnez $t6, char_x_loop
    
    addi $t4, $t4, SCREEN_WIDTH * 4  # Next row
    subi $t5, $t5, 1
    bnez $t5, char_y_loop
    
    addi $t0, $t0, 1     # Next character
    addi $t1, $t1, 9     # Move X position (8 pixels plus 1 for spacing)
    j text_loop
    
text_done:
    jr $ra

# Draw a number
# $a0 = Number to draw, $a1 = X position, $a2 = Y position, $a3 = Color
draw_number:
    # Save return address
    addi $sp, $sp, -4
    sw $ra, 0($sp)
    
    # Convert number to string (simplified)
    li $t0, 10          # Base 10
    move $t1, $a0       # Number to convert
    
    # Special case for 0
    bnez $t1, not_zero
    la $a0, "0"
    j draw_num_str
    
not_zero:
    # Convert number to string (very simplified)
    la $a0, "0123456789"
    add $a0, $a0, $t1   # Just get the character for 0-9
    
draw_num_str:
    # Draw the digit
    move $a1, $a1
    move $a2, $a2
    move $a3, $a3
    jal draw_text
    
    # Restore return address and return
    lw $ra, 0($sp)
    addi $sp, $sp, 4
    jr $ra

# === N64 Hardware Definitions ===
# These would normally be in an include file (n64.inc)
# Only including minimal definitions relevant to this game

# Video Interface (VI) Registers
VI_BASE_REG        = 0xA4400000
VI_STATUS          = 0x00
VI_ORIGIN          = 0x04
VI_WIDTH           = 0x08
VI_V_CURRENT       = 0x0C
VI_CONTROL         = 0x10

# VI Control Register flags
VI_CTRL_TYPE_16    = 0x00002
VI_CTRL_GAMMA_ON   = 0x00008
VI_CTRL_ANTIALIAS_ON = 0x00100

# MIPS Interface (MI) Registers
MI_BASE_REG        = 0xA4300000
MI_INTR_MASK       = 0x0C
MI_INTR_MASK_VI    = 0x08

# Audio Interface (AI) Registers
AI_BASE_REG        = 0xA4500000
AI_CONTROL         = 0x00
AI_CONTROL_DMA_ON  = 0x01

# Peripheral Interface (PI) Registers
PI_BASE_REG        = 0xA4600000
PI_STATUS          = 0x00
PI_STATUS_RESET    = 0x02

# Controller Registers
CONT1_BASE         = 0xA4800000
CONT2_BASE         = 0xA4800004
CONT_BUTTONS       = 0x00
CONT_PRESENT       = 0x80000000
CONT_UP            = 0x00000008
CONT_DOWN          = 0x00000004
CONT_LEFT          = 0x00000002
CONT_RIGHT         = 0x00000001
CONT_START         = 0x00001000
