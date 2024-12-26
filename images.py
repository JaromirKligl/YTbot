import pathlib
import discord
import os
import random
from discord.ext import commands

def setup(bot):

    @bot.command()
    async def upload(ctx, name):
        """Upload an image to database with name name"""
        if not ctx.message.attachments:
            await ctx.send("Please attach an image to upload.")
            return

            # Process the first attachment in the message
        attachment = ctx.message.attachments[0]

        if not attachment.content_type or not attachment.content_type.startswith("image/"):
            await ctx.send("The uploaded file is not an image.")
            return

        upload_folder = pathlib.Path.cwd() / "images" / name
        if os.path.exists(upload_folder) and os.path.isdir(upload_folder):
            await ctx.send(f"Image saved as `{name}` is already in database, this task is now terminated")
            return

        upload_folder.mkdir(exist_ok=True)
        file_path = upload_folder / attachment.filename
        try:
            await attachment.save(file_path)
            await ctx.send(f"Image saved as `{name}` is now in database")

        except Exception as e:
            await ctx.send("An error occurred while saving the image.")
            print(f"Error saving image: {e}")

    @bot.command()
    async def show(ctx, name=None):
        """Shows an image with name name"""
        if name is None:
            images = pathlib.Path.cwd() / "images"
            all_img = images.glob("*")
            image_folder = random.choice(list(all_img))

        else:
            image_folder = pathlib.Path.cwd() / "images" / name

        if not os.path.exists(image_folder):
            await ctx.send("The image does not exist.")
            return

        images = image_folder.glob("*")
        for img in images:
            await ctx.send(file=discord.File(img))

        return


    @bot.command()
    async def images(ctx):
        """lists all images"""
        images_folder = pathlib.Path.cwd() / "images"
        images = images_folder.glob("*")
        img_list = [img.parts[-1] for img in images]
        await ctx.send("images: \n"+ ", ".join(img_list))
        return