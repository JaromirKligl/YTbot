import math
import random

X = -2
O = 2
Tie = 1


def available_positions (board, player : int):

    possible_boards = []
    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] == 0:
                new_board = [row.copy() for row in board]
                new_board[row][col] = player
                possible_boards.append(new_board)

    return possible_boards


def board_difference(board1, board2):
    for row_index, row in enumerate(board1):
        for col_index, col in enumerate(row):
            if board1[row_index][col_index] != board2[row_index][col_index]:
                return row_index, col_index

def minimax(board, depth):

    position_eval = check_board_winner(board)

    if depth == 0 or position_eval != 0:
        return position_eval

    value = -math.inf
    for board in available_positions(board, O):
        value = max(value, maximin(board, depth - 1))
    return value



def maximin(board, depth):

    position_eval = check_board_winner(board)

    if depth == 0 or position_eval != 0:
        return position_eval

    value = math.inf
    for board in available_positions(board, X):
        value = min(value, minimax(board, depth - 1))
    return value

def find_best_move(board, depth):

    value = -math.inf
    best_board = None
    available = available_positions(board, O)
    print("Available positions for O:", available)
    for board_s in available:
        board_eval = maximin(board_s, depth - 1)
        if value < board_eval:
            value = board_eval
            best_board = board_s

    if not best_board:
        print("here")
        best_board = random.choice(available)
    print("best")
    print(best_board)
    print("board")
    print(board)
    return board_difference(best_board, board)


def check_board_winner(board):
    for across in board:
        value = sum(across)
        if value == 6:
            return O
        elif value == -6:
            return X

    # Check vertical
    for line in range(3):
        value = board[0][line] + board[1][line] + board[2][line]
        if value == 6:
            return O
        elif value == -6:
            return X

    # Check diagonals
    diag = board[0][2] + board[1][1] + board[2][0]

    if diag == 6:
        return O
    elif diag == -6:
        return X

    diag = board[0][0] + board[1][1] + board[2][2]
    if diag == 6:
        return O
    elif diag == -6:
        return X

    # If we're here, we need to check if a tie was made
    if all(i != 0 for row in board for i in row):
        return Tie

    return 0