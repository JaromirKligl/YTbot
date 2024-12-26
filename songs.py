from yt_dlp import YoutubeDL
import discord
from discord.ext import commands


YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'quiet': True,
    'ignoreerrors': True,
    'abort_on_unavailable_fragments': True,
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


class QueueItem(tuple):
    def __repr__(self):
        return f"{self[0]} | Filter: {self[1]}"

class SongQueue(list):
    def __repr__(self):
        return "QUEUE:\n" + '\n'.join(map(str, self))




SONG_QUEUE = SongQueue()

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
    async def play(ctx, url, filter=None):
        """Play audio from a YouTube URL."""

        if not ctx.voice_client:
            await ctx.send("I need to join a voice channel first. Use `%join`.")
            return
        try:
            # Use yt-dlp to extract audio info
            info = ytdl.extract_info(url, download=False)
            if "entries" in info:

                url2 = info["entries"][0]["url"]

                for song in info["entries"][1:]:
                    if song:
                        print(song["title"])
                        song_url = song.get("webpage_url")

                        SONG_QUEUE.append(QueueItem((song_url, filter)))

                await ctx.send(f"{url} was add to queue")

            else:
                url2 = info['url']

            if ctx.voice_client and ctx.voice_client.is_playing():
                SONG_QUEUE.append(QueueItem((url, filter)))
                await ctx.send(f"{url} was add to queue")
                return

            await play_song(ctx, url2, filter,info)

        except Exception as e:
            await ctx.send("An error occurred while trying to play the audio.")
            print(e)


    @bot.command()
    async def stop(ctx):
        """Stop the currently playing audio."""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Stopped playing.")
        else:
            await ctx.send("No audio is currently playing.")


    @bot.command()
    async def queue(ctx):
        """Shows the que"""
        await ctx.send(str(SONG_QUEUE))


    async def play_song(ctx, url2, filter, info):

        def after_playing(error):
            if error:
                print(f"Error occurred: {error}")
                return

            if SONG_QUEUE:
                info2, filter2 = SONG_QUEUE.pop(0)

                coro = bot.loop.create_task(
                    play(ctx, info2, filter2)
                )
                bot.loop.create_task(coro)
            else:
                coro = ctx.send("ALL songs finished in skibidi")
                bot.loop.create_task(coro)

        options = None
        match filter:
            case "nightcore":
                options = FFMPEG_NIGHTCORE_OPTIONS

            case "fast":
                options = FFMPEG_FAST

            case "daycore":
                options = FFMPEG_DAYCORE

            case _:
                options = FFMPEG_OPTIONS

        ctx.voice_client.play(discord.FFmpegPCMAudio(url2, **options), after=after_playing)

        await ctx.send(f"Now playing: {info['title']}")
        return

