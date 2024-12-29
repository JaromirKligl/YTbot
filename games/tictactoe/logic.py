from . import ui

async def play_tic(ctx, *args):
    """Starts a tic-tac-toe game with yourself."""
    if args:
        await ctx.send('Tic Tac Toe: X goes first', view=ui.TicTacToe(args[0]))
    else:
        await ctx.send('Tic Tac Toe: X goes first', view=ui.TicTacToe())