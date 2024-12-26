import os

# Tic Tac Toe game in Python

def print_board(board):
  for i in range(3):
    print('|', end='')
    for j in range(3):
      print(board[i][j], end=' |')
    print('\n---------')

def check_win(board):
  for i in range(3):
    if board[i][0] == board[i][1] == board[i][2] != ' ':
      return True
    if board[0][i] == board[1][i] == board[2][i] != ' ':
      return True
  if board[0][0] == board[1][1] == board[2][2] != ' ' or board[0][2] == board[1][1] == board[2][0] != ' ':
    return True
  return False

def tic_tac_toe():
  board = [[' ' for _ in range(3)] for _ in range(3)]
  current_player = 'X'
  while True:
    print_board(board)
    while True:
      move_row = int(input('Enter the row for your move (0, 1, or 2): '))
      move_col = int(input('Enter the column for your move (0, 1, or 2): '))
      if board[move_row][move_col] == ' ':
        board[move_row][move_col] = current_player
        break
      print('Invalid move, try again.')
    if check_win(board):
      print('Player', current_player, 'wins!')
      break
    current_player = 'O' if current_player == 'X' else 'X'

tic_tac_toe()