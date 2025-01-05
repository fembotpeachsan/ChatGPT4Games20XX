import pygame
import chess

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
TILE_SIZE = SCREEN_WIDTH // 8
FPS = 60  # Target frame rate

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TILE_LIGHT = (240, 217, 181)
TILE_DARK = (181, 136, 99)
PIECE_LIGHT = (250, 250, 210)
PIECE_DARK = (105, 105, 105)

# Chess Board
board = chess.Board()

# Game Screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('ToadChess4K')

# Fonts
font = pygame.font.SysFont("Arial", TILE_SIZE // 3)

# Chess piece symbols
piece_symbols = {
    'K': '♔',
    'Q': '♕',
    'R': '♖',
    'B': '♗',
    'N': '♘',
    'P': '♙',
    'k': '♚',
    'q': '♛',
    'r': '♜',
    'b': '♝',
    'n': '♞',
    'p': '♟',
}

# Game Loop
running = True
selected_square = None
clock = pygame.time.Clock()  # Create a clock object to control FPS

def draw_board():
    """Draw the chess board with alternating colors."""
    for rank in range(8):
        for file in range(8):
            rect = pygame.Rect(file * TILE_SIZE, rank * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            color = TILE_LIGHT if (rank + file) % 2 == 0 else TILE_DARK
            pygame.draw.rect(screen, color, rect)

def draw_pieces():
    """Draw the chess pieces dynamically."""
    for rank in range(8):
        for file in range(8):
            piece = board.piece_at(chess.square(file, 7 - rank))
            if piece:
                # Draw the piece as a circle with a symbol in the center
                center_x = file * TILE_SIZE + TILE_SIZE // 2
                center_y = rank * TILE_SIZE + TILE_SIZE // 2
                color = PIECE_LIGHT if piece.color else PIECE_DARK
                pygame.draw.circle(screen, color, (center_x, center_y), TILE_SIZE // 3)
                
                # Draw the piece symbol
                symbol = piece_symbols[piece.symbol()]
                text_surface = font.render(symbol, True, BLACK if piece.color else WHITE)
                text_rect = text_surface.get_rect(center=(center_x, center_y))
                screen.blit(text_surface, text_rect)

while running:
    # Limit the frame rate to 60 FPS
    clock.tick(FPS)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            file = x // TILE_SIZE
            rank = 7 - (y // TILE_SIZE)
            square = chess.square(file, rank)
            if selected_square is None and board.piece_at(square) is not None and board.piece_at(square).color == board.turn:
                selected_square = square
            elif selected_square is not None:
                move = chess.Move(selected_square, square)
                if move in board.legal_moves:
                    board.push(move)
                selected_square = None
    
    # Check for end conditions
    if board.is_checkmate():
        print('Checkmate!')
        running = False
    elif board.is_stalemate():
        print('Stalemate!')
        running = False

    # Draw the board and pieces
    screen.fill(WHITE)
    draw_board()
    draw_pieces()

    # Update the display
    pygame.display.flip()

pygame.quit()
