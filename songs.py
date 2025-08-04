import asyncio
from asyncio import to_thread

from yt_dlp import YoutubeDL
import discord
from discord.ext import commands
import random


YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'quiet': True,
    'ignoreerrors': True,
    'abort_on_unavailable_fragments': True,
    'concurrent_downloads': 8,
    'concurrent_fragments': 16,
    'extract_flat' : 'in_playlist',

    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}

# Plne extraktuje jednotlive songy pred prehratim :)
YTDL_AFTER_EXTRACT = {
    'format': 'bestaudio/best',
    'quiet': True,
    'ignoreerrors': True,
    'abort_on_unavailable_fragments': True,
    'concurrent_fragments': 64,
    'extract_flat' : 'True',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}


FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

FFMPEG_NIGHTCORE_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -filter:a "asetrate=44100*1.25,atempo=1.1"'
}

FFMPEG_FAST = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -filter:a "asetrate=44100*1.25,atempo=5"'
}

FFMPEG_DAYCORE = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -filter:a "asetrate=44100*1.25,atempo=0.9"'
}
# Initialize yt-dlp instance
ytdl = YoutubeDL(YTDL_OPTIONS)

# inicializuj non-flat extrakci pro jednotlive songy playlistu, pred prehratim :)
precise_ytdl = YoutubeDL(YTDL_AFTER_EXTRACT)

background_tasks = set()



class QueueItem():

    def __init__(self, info, filter=None, is_flat=False):

        self.info = info
        self.filter = filter
        self.is_flat = is_flat
        self.semaphore = asyncio.Semaphore()

    def __repr__(self):
        return f"{self.info['title']} | Filter: {self.filter}"



class SongQueue(list):
    def __repr__(self):
        return "QUEUE:\n" + '\n'.join(map(str, self))




SONG_QUEUE = SongQueue()


async def get_precise_data(song : QueueItem):
    info = await to_thread(precise_ytdl.extract_info, song.info["url"], download=False)
    song.info = info
    song.is_flat = False


async def extract_queue_at_background():
    for song in SONG_QUEUE:
        async with song.semaphore:
            if song.is_flat:
                await get_precise_data(song)


def setup(bot):

    @bot.command()
    async def join(ctx):
        """Join the voice channel."""
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel to use this command.")
            return

        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()


    @bot.command()
    async def leave(ctx):
        """Leave the voice channel."""
        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()
            await ctx.send("Disconnected from the voice channel.")
        else:
            await ctx.send("I'm not connected to a voice channel.")

    @bot.command()
    async def play(ctx, url, filter=None, shuffle=False):
        """Play audio from a YouTube URL."""

        if not ctx.voice_client:
            await ctx.send("I need to join a voice channel first. Use `%join`.")
            return
        try:
            # Use yt-dlp to extract audio info
            info = await to_thread(ytdl.extract_info, url, download=False)

            #Playlist

            if "entries" in info:
                # To prevent keeping references to finished tasks forever,
                # make each task remove its own reference from the set after
                # completion:

                if shuffle:
                    random.shuffle(info["entries"])

                for song in info["entries"]:
                    if song:
                        SONG_QUEUE.append(QueueItem(song, filter, True))

                task = asyncio.create_task(extract_queue_at_background())
                background_tasks.add(task)
                task.add_done_callback(background_tasks.discard)

                await ctx.send(f"{url} was add to queue")

            else:
                SONG_QUEUE.append(QueueItem(info, filter, False))
                await ctx.send(f"{url} was add to queue")

            if ctx.voice_client and not ctx.voice_client.is_playing():
                await play_song(ctx,SONG_QUEUE.pop(0))

        except Exception as e:
            await ctx.send("An error occurred while trying to play the audio.")
            print(e)


    @bot.command()
    async def skip(ctx):
        """Skips the currently playing audio."""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Skipped current Song.")
        else:
            await ctx.send("No audio is currently playing.")

    @bot.command()
    async def pause(ctx):
        """Pause the currently playing audio."""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Pause current Song.")
        else:
            await ctx.send("No audio is currently playing.")


    @bot.command()
    async def resume(ctx):
        """Pause the currently playing audio."""
        if not ctx.voice_client:
            return

        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("Resumed current Song.")

        elif ctx.voice_client.is_playing():
            await ctx.send("Already playing no need to resume")

        else:
            await ctx.send("No audio is currently playing.")


    @bot.command()
    async def flush(ctx):
        """Flush the queue."""
        SONG_QUEUE.clear()
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        await ctx.send("Queue flushed.")


    @bot.command()
    async def queue(ctx):
        """Shows the queue"""
        await ctx.send(str([item for item in SONG_QUEUE if item])) # Removes None



    async def play_song(ctx, song : QueueItem):

        def after_playing(error):
            if error:
                print(f"Error occurred: {error}")
                return

            if SONG_QUEUE:
                coro = bot.loop.create_task(
                    play_song(ctx, SONG_QUEUE.pop(0))
                )
                bot.loop.create_task(coro)

            else:
                coro = ctx.send("ALL songs finished in skibidi")
                bot.loop.create_task(coro)

        options = None
        match song.filter:
            case "nightcore":
                options = FFMPEG_NIGHTCORE_OPTIONS

            case "fast":
                options = FFMPEG_FAST

            case "daycore":
                options = FFMPEG_DAYCORE

            case _:
                options = FFMPEG_OPTIONS


        # Gain full info about next song if it is from playlist
        async with song.semaphore:
            if song.is_flat:
                await get_precise_data(song)


        info = song.info


        if info:
            url = info["url"]
            ctx.voice_client.play(discord.FFmpegPCMAudio(url, **options), after=after_playing)
        else:
            if SONG_QUEUE:
                await play_song(ctx, SONG_QUEUE.pop(0))
            else:
                await ctx.send("ALL songs finished in skibidi")



        await ctx.send(f"Now playing: {info['title']}")
        return

