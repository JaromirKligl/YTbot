import random
import discord
from discord.ext import commands
import os

def read_pool(pool_name):
	FILENAME = f"{os.path.dirname(__file__)}/gamba/{pool_name}.txt"
	names = []
	weights = []
	with open(FILENAME, "r") as f:
		for line in f:
			item = line.split()
			names.append(" ".join(item[:-1]))
			weights.append(float(item[-1]))
	return names, weights

def make_string(pool_name):
	"""Creates table to display gamba pool"""
	names, weights = read_pool(pool_name)
	total_sum = sum(weights)
	probabilities = [f"{x/total_sum:.2%}" for x in weights]
	result = """"""
	for i in range(len(names)):
		result = result + f"`{names[i]}: {probabilities[i]}` \n"
	return result

def setup(bot):
	@bot.command()
	async def roll(ctx, pool_name):
		"""Roll from pool_name"""
		names, weights = read_pool(pool_name)
		rolled = random.choices(names,weights=weights)[0]
		await ctx.send(rolled)

	@bot.command()
	async def gamba_show(ctx, pool_name):
		"""Show pool"""
		await ctx.send(make_string(pool_name))

if __name__=="__main__":
	read_pool("dice")
