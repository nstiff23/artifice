import asyncio
from queue import Queue

import discord
from discord.ext import commands

import youtube_dl

from initiative import Initiative
from song_queue import SongQueue
from dice import tokenize
from dice import Parser

TOKEN = ""

def fetch_token():
    tokfile = open("TOKEN.txt")
    tok = tokfile.read()
    tokfile.close()
    return tok

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

async def download(url, loop):
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=True))
    filename = ytdl.prepare_filename(data)
    return filename

def is_number(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

trackers = {}
init_msg = {}

past_rolls = {}

roll_help = (
    'Rolls some dice\n'
    'format: 4d6h3: Rolls 4d6, keeps the 3 highest.\n'
    'Can also add, subtract, divide and multiply in PMDAS order.\n'
    'ex. 4d6+(3d10/2-1)-1d4+2d5\n'
)

init_help = (
    'Controls the initiative tracker\n'
    'start (or begin) : Starts the initiative tracker.\n'
    'end : Clears the initiative tracker.\n'
    'add <name> <bonus> <option> : Adds someone to initiative with a certain bonus. '
    'The optional parameter can be "adv" or "dis" to give them advantage or '
    'disadvantage on the roll, a number to specify what they roll, or "surprise" '
    'to give them a surprise round.\n'
    'remove <name> : Removes someone from initiative.\n'
    'next : Advances the initiative tracker and tags the next player.\n'
)

async def process_roll(ctx, roll):
    results, remainder = tokenize(roll)
    if remainder:
        print("parse error???")
    parser = Parser(results)
    expr = parser.parse()
    eval = expr.eval()
    out = str(expr)
    name = ctx.message.author.display_name
    response = name + " rolled " + out + "\nResult: " + str(eval)
    await ctx.channel.send(response)

def print_init(channel):
    return str(trackers[channel])
        
def in_init(channel):
    return (channel in trackers and trackers[channel] != None)

async def process_init(init_command, channel, author):
    error = False

    if init_command[0] == "start" or init_command[0] == "begin":
        if in_init(channel):
            await channel.send("Already in initiative!")
        else:
            trackers[channel] = Initiative()
            await channel.send("Initiative begun!" + 
                    " Use !init add <name> <bonus> <options> to roll initiative.")
            init_msg[channel] = await channel.send(print_init(channel))
            await init_msg[channel].pin()

    elif init_command[0] == "add":
        if in_init(channel):
            adv = 0
            roll = None
            surprise = 0

            if is_number(init_command[1]):
                await channel.send('Invalid argument, use !init add <name> <bonus> <options> to roll')
                error = True

            if not is_number(init_command[2]):
                await channel.send('Invalid argument, use !init add <name> <bonus> <options> to roll')
                error = True

            if len(init_command) >= 4:
                if init_command[3] == "adv":
                    adv = 1
                elif init_command[3] == "dis":
                    adv = -1
                elif init_command[3] == "surprise":
                    surprise = 1
                elif init_command[3] == "lost":
                    surprise = -1
                elif is_number(init_command[3]):
                    roll = int(init_command[3])
                else:
                    await channel.send('Invalid argument, use !init add <name> <bonus> <options> to roll')
                    error = True
                if len(init_command) == 5:
                    if init_command[4] == "adv":
                        adv = 1
                    elif init_command[4] == "dis":
                        adv = -1
                    elif init_command[4] == "surprise":
                        surprise = 1
                    elif init_command[4] == "lost":
                        surprise = -1
                    elif is_number(init_command[4]):
                        roll = int(init_command[4])
                    else:
                        await channel.send('Invalid argument, use !init add <name> <bonus> <options> to roll')
                        error = True
            
            if not error:
                trackers[channel].add(init_command[1], int(init_command[2]), 
                        id=author, roll=roll, adv=adv, surprise=surprise)
                await init_msg[channel].edit(content=print_init(channel))
        else:
            await channel.send("Not in initiative")

    elif init_command[0] == "remove":
        if in_init(channel):
            trackers[channel].remove(init_command[1])
            await init_msg[channel].edit(content=print_init(channel))
        else: 
            await channel.send("Not in intiative")

    elif init_command[0] == "end":
        if in_init(channel):
            trackers[channel] = None
            await init_msg[channel].unpin()
            await channel.send("Initiative ended")
        else:
            await channel.send("Not in intiative")

    elif init_command[0] == "next":
        if in_init(channel):
            tracker = trackers[channel]
            entity = tracker.next()
            member = entity.id
            name = entity.name
            await init_msg[channel].edit(content=print_init(channel))
            mention = member.mention
            await channel.send("Up next: " + name + " " + mention)
        else: 
            await channel.send("Not in initiative")
    
    else: 
        await channel.send('Invalid command, call \'!help\' for more information')

TOKEN = fetch_token()
intents = discord.Intents.default()
intents.message_content = True

song_queue = None

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command(name="join", brief="Join the user's current voice channel")
async def join(ctx):
    author = ctx.message.author
    if not author.voice:
        await ctx.send(author.display_name + " is not in a voice channel!")
        return
    channel = author.voice.channel
    await channel.connect()

@bot.command(name="leave", brief="Leave the current voice channel")
async def leave(ctx):
    global song_queue
    voice = ctx.message.guild.voice_client
    if voice and voice.is_connected():
        if song_queue is not None:
            song_queue.clear_queue()
        voice.stop()
        await voice.disconnect()
    else:
        await ctx.send("Not in a voice channel")

@bot.command(name="play", brief="Play a song from a YouTube URL")
async def play(ctx, url):
    global song_queue
    voice = ctx.message.guild.voice_client
    if not voice or not voice.is_connected():
        await join(ctx)
        voice = ctx.message.guild.voice_client
    if voice and voice.is_connected():
        async with ctx.typing():
            if song_queue is None:
                song_queue = SongQueue(ytdl_format_options, voice, bot.loop)
            title = await song_queue.add(url)
            await ctx.send("{} added to queue".format(title))

#clear -- clear queue except currently playing
#remove -- remove specified index from play queue
#cancel -- remove specified index from download queue

@bot.command(name="skip", brief="Skip the currently playing song")
async def skip(ctx):
    voice = ctx.message.guild.voice_client
    if voice.is_playing() or voice.is_paused():
        voice.stop()
    else:
        await ctx.send("Nothing is currently playing")

@bot.command(name="stop", brief="Clear the queue and stop playing")
async def stop(ctx):
    global song_queue
    voice = ctx.message.guild.voice_client
    if voice.is_playing() or voice.is_paused():
        song_queue.clear_queue()
        voice.stop()
    else:
        await ctx.send("Nothing is currently playing")

@bot.command(name="pause", brief="Pause the currently playing song")
async def pause(ctx):
    voice = ctx.message.guild.voice_client
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Not currently playing")

@bot.command(name="resume", brief="Resume the currently paused song")
async def resume(ctx):
    voice = ctx.message.guild.voice_client
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("Not currently paused")

@bot.command(name="list", brief="List songs in the queue")
async def list(ctx):
    global song_queue
    song_list = str(song_queue)
    await ctx.send(song_list)

@bot.command(name="roll", brief="Rolls some dice", help=roll_help)
async def roll(ctx, *args):
    roll = ""
    for arg in args:
        roll = roll + arg
    past_rolls[ctx.message.author.id] = roll
    await process_roll(ctx, roll)

@bot.command(name="re", brief="Repeats your last roll")
async def re(ctx):
    author = ctx.message.author
    if author.id in past_rolls:
        roll = past_rolls[author.id]
        await process_roll(ctx, roll)
    else:
        await ctx.channel.send(author.display_name + " has no previous roll on record!")

@bot.command(name="init", brief="Starts an initiative tracker in this channel", help=init_help)
async def init(ctx, *args):
    await process_init(args, ctx.channel, ctx.message.author)


if __name__ == "__main__":
    bot.run(TOKEN)
