import discord
import pickle
import os
import random
import pathlib

ACTIVE_ROLL_SET : pathlib.Path | None = None

GAMBA_HELP_MSG = """
**ACTIVE POOL COMMANDS**
- `gamba show`: Shows list of options and probabilities.
- `gamba add <name> <probability>`: Adds an option with a `(name: str, probability: float)`, then adjusts all other probabilities.
- `gamba remove <name>`: Removes an option `(name: str)`.
- `gamba roll <*names>`: Rolls for each name once

**POOLS COMMANDS**
- `gamba active_pool`: Shows the currently active pool.
- `gamba swap <name>`: Switches to the pool `<name>`.
- `gamba create_pool <name>`: Creates an empty pool with the name `<name>`.
- `gamba pools`: Shows the list of available pools.
"""

GAMBA_DIRECTORY = pathlib.Path.cwd() / "gamba"

async def show_pools(ctx):
    pools = GAMBA_DIRECTORY.glob("*")
    pool_list = [pool.parts[-1] for pool in pools]
    await ctx.send("pools: \n" + ", ".join(pool_list))
    return

async def swap_pools(ctx, name):
    pool_file = GAMBA_DIRECTORY / name
    if not os.path.exists(pool_file):
        await ctx.send("The pool isn't here")
        return

    global ACTIVE_ROLL_SET
    ACTIVE_ROLL_SET = pool_file

    return

async def initialize_data(name):
    pool_file = GAMBA_DIRECTORY / name

    if os.path.exists(pool_file):
        return False

    with open(pool_file, "wb") as file:
        pickle.dump({}, file)

    global ACTIVE_ROLL_SET
    ACTIVE_ROLL_SET = pool_file
    return True


async def upload_data(name, prob):

    if not ACTIVE_ROLL_SET:
        return "ACTIVE_ROLL_SET is not set."

    try:
        prob = float(prob)
        with open( ACTIVE_ROLL_SET, "rb") as file: # NOQA
            db = pickle.load(file)

    except Exception as e:
        return str(e)

    db[name] = {"name": name, "probability": prob}
    for key in db.keys():
        if key != name:
            db[key]["probability"] = db[key]["probability"] * (1 - prob)

    try:
        with open(ACTIVE_ROLL_SET, "wb") as file:
            pickle.dump(db, file)

    except Exception as e:
        return str(e)


async def read_data():

    if not ACTIVE_ROLL_SET:
        return "ACTIVE_ROLL_SET is not set."

    try:
        msg = ""
        with open(ACTIVE_ROLL_SET, "rb") as file:
            db = pickle.load(file)
            for key in db.keys():
                x = db[key]
                msg += f"{x['probability']:.4g} pro {x['name']} \n"
            return msg
    except Exception as e:
        return str(e)


async def remove_data(name):

    if not ACTIVE_ROLL_SET:
        return "ACTIVE_ROLL_SET is not set."

    try:
        file = open(ACTIVE_ROLL_SET, "rb")
        db = pickle.load(file)
    except Exception as e:
        return str(e)

    x = db.pop(name)
    for key in db.keys():
        db[key]["probability"] /= 1 - x["probability"]

    try:
        file = open(ACTIVE_ROLL_SET, "wb")
        pickle.dump(db, file)
    except Exception as e:
        return str(e)


async def roll(*args):
    try:
        with open(ACTIVE_ROLL_SET, "rb") as file:
            db = pickle.load(file)

    except Exception as e:
        return str(e)

    names = []
    probabilities = []
    result = []
    n = len(args)
    for x in db.values():
        names.append(x["name"])
        probabilities.append(x["probability"])

    for arg in args:
        rolled = random.choices(names, weights=probabilities)[0]
        result.append(rolled)
    return list(args), result



def setup(bot):

    @bot.command()
    async def gamba(ctx, option, *args):
        """see gamba help"""
        match option:

            case 'show':
                await ctx.send(await read_data())

            case 'help':
                await ctx.send(GAMBA_HELP_MSG)

            case 'add':
                await upload_data(*args)

            case 'remove':
                await remove_data(*args)

            case 'pools':
                await show_pools(ctx)

            case 'swap':
                await swap_pools(ctx, args[0])

            case 'create_pool':
                if await initialize_data(args[0]):
                    await ctx.send("Pool created")
                else:
                    await ctx.send("Pool already exists all another problem appears")

            case 'remove_pool':
                await ctx.send("Not Implemented yet too dangerous (i am lazy)")

            case 'active_pool':

                if ACTIVE_ROLL_SET:
                    await ctx.send(ACTIVE_ROLL_SET.parts[-1])
                else:
                    await ctx.send("No active pool")

            case 'roll':
                people, results = await roll(*args)
                msg = ""
                for i in range(len(args)):
                    msg += f"{people[i]} vylosoval {results[i]}\n"
                await ctx.send(msg)