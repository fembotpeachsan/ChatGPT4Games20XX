def print_board(board):
    for row in board:
        print(' | '.join(row))
        print('-' * 5)

def check_win(board):
    # Check rows
    for row in board:
        if row.count(row[0]) == len(row) and row[0] != ' ':
            return True

    # Check columns
    for col in range(len(board)):
        check_col = [row[col] for row in board]
        if check_col.count(check_col[0]) == len(check_col) and check_col[0] != ' ':
            return True

    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != ' ':
        return True
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != ' ':
        return True

    return False

def check_draw(board):
    for row in board:
        if ' ' in row:
            return False
    return True

def tic_tac_toe():
    board = [[' ' for _ in range(3)] for _ in range(3)]
    current_player = 'X'

    while True:
        print_board(board)
        print(f'Player {current_player}, make your move.')

        try:
            row = int(input('Enter the row (0-2): '))
            col = int(input('Enter the column (0-2): '))
        except ValueError:
            print('Invalid input. Please enter numbers between 0 and 2.')
            continue

        if row < 0 or row > 2 or col < 0 or col > 2:
            print('Invalid input. Row and column must be between 0 and 2.')
            continue

        if board[row][col] != ' ':
            print('This cell is already occupied. Try again.')
            continue

        board[row][col] = current_player

        if check_win(board):
            print_board(board)
            print(f'Player {current_player} wins!')
            break

        if check_draw(board):
            print_board(board)
            print('The game is a draw!')
            break

        current_player = 'O' if current_player == 'X' else 'X'

if __name__ == '__main__':
    tic_tac_toe()
