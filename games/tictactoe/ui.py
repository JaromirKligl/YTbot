#https://github.com/Rapptz/discord.py/blob/v2.4.0/examples/views/tic_tac_toe.py
#Taken from here
import discord
from typing import List
from discord.ext import commands
import random
from .minimax import find_best_move

class TicTacToeButton(discord.ui.Button['TicTacToe']):
    def __init__(self, x: int, y: int):
        # A label is required, but we don't need one so a zero-width space is used
        # The row parameter tells the View which row to place the button under.
        # A View can only contain up to 5 rows -- each row can only have 5 buttons.
        # Since a Tic Tac Toe grid is 3x3 that means we have 3 rows and 3 columns.
        super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', row=y)
        self.x = x
        self.y = y


    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        if view.current_player == view.X:
            self.style = discord.ButtonStyle.danger
            self.label = 'X'
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = "It is now O's turn"
        else:
            self.style = discord.ButtonStyle.success
            self.label = 'O'
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = "It is now X's turn"

        winner = view.check_board_winner()

        if winner == 0 and view.difficulty != "human" and view.current_player == view.O:
            # Bot provede svůj tah
            view.bot_make_move()
            winner = view.check_board_winner()
            content = "It is now X's turn"

        if winner != 0:
            if winner == view.X:
                content = 'X won!'
            elif winner == view.O:
                content = 'O won!'
            else:
                content = "It's a tie!"

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)


# This is our actual board View
class TicTacToe(discord.ui.View):
    # This tells the IDE or linter that all our children will be TicTacToeButtons
    # This is not required
    children: List[TicTacToeButton]

    #Pri nicem vrati 0 (vhodne pro evaluaci) (nejlespi je vyhra 2. hrace (bota), nejhorsi je vyhra 1. hrace
    X = -2
    O = 2
    Tie = 1

    def __init__(self, difficulty="human"):
        super().__init__()
        self.current_player = self.X
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]
        self. difficulty =  difficulty

        # Our board is made up of 3 by 3 TicTacToeButtons
        # The TicTacToeButton maintains the callbacks and helps steer
        # the actual game.
        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    # This method checks for the board winner -- it is used by the TicTacToeButton
    def check_board_winner(self):
        for across in self.board:
            value = sum(across)
            if value == 6:
                return self.O
            elif value == -6:
                return self.X

        # Check vertical
        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 6:
                return self.O
            elif value == -6:
                return self.X

        # Check diagonals
        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 6:
            return self.O
        elif diag == -6:
            return self.X

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 6:
            return self.O
        elif diag == -6:
            return self.X

        # If we're here, we need to check if a tie was made
        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return 0

    def medium_bot_make_move(self):
        y, x = find_best_move(self.board, 1)
        self.board[y][x] = self.O  # Bot hraje za O
        button = self.get_button(x, y)
        if button:
            button.label = "O"
            button.style = discord.ButtonStyle.success
            button.disabled = True

        # Změna hráče
        self.current_player = self.X

    def hard_bot_make_move(self):
        y, x = find_best_move(self.board, 2)
        self.board[y][x] = self.O  # Bot hraje za O
        button = self.get_button(x, y)
        if button:
            button.label = "O"
            button.style = discord.ButtonStyle.success
            button.disabled = True

        # Změna hráče
        self.current_player = self.X
    def insane_bot_make_move(self):
        y, x = find_best_move(self.board, 9)
        self.board[y][x] = self.O  # Bot hraje za O
        button = self.get_button(x, y)
        if button:
            button.label = "O"
            button.style = discord.ButtonStyle.success
            button.disabled = True

        # Změna hráče
        self.current_player = self.X


    def easy_bot_make_move(self):
        # Vyhledání volných pozic
        available_positions = [
            (x, y)
            for y, row in enumerate(self.board)
            for x, value in enumerate(row)
            if value == 0
        ]

        if not available_positions:
            return  # Není dostupný tah

        # Náhodně vybrané volné místo
        x, y = random.choice(available_positions)

        # Provedení tahu
        self.board[y][x] = self.O  # Bot hraje za O
        button = self.get_button(x, y)
        if button:
            button.label = "O"
            button.style = discord.ButtonStyle.success
            button.disabled = True

        # Změna hráče
        self.current_player = self.X

    def bot_make_move(self):

        match self.difficulty:
            case "easy":
                self.easy_bot_make_move()

            case "insane":
                self.insane_bot_make_move()

            case "medium":
                self.medium_bot_make_move()

            case "hard":
                self.hard_bot_make_move()
            case _:
                pass

    # Pomocná metoda pro získání tlačítka podle pozice
    def get_button(self, x, y):
        for child in self.children:
            if isinstance(child, TicTacToeButton) and child.x == x and child.y == y:
                return child
        return None
