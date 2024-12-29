from .tictactoe import logic

GAMES = {'tictactoe' : logic.play_tic}
def setup(bot):

    @bot.command()
    async def game(ctx, option, *args):
        """Can play some games"""
        if option in GAMES:
            await GAMES[option](ctx, *args)