import discord
from discord.utils import get
from discord.ext import commands
import logging 
import numbers
from datetime import datetime, time, timedelta
import json
import requests
import random
import asyncio
from dotenv import load_dotenv
import youtube_dl
import os
from prsaw import RandomStuff
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO

load_dotenv()

intents = discord.Intents().all()

DISCORD_TOKEN = os.getenv("discord_token")
AI_API_KEY = os.getenv('ai_api_key')

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = commands.Bot(command_prefix='=', description='A simple bot to learn python.', intents = intents)

deletedMsgs = []
deletedChnl = []
deletedAthr = []
editedMsgB = []
editedMsgA = []
editedAthr = []

youtube_dl.utils.bug_reports_message = lambda: ''

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

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.1):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""
        self.volume = volume

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

@bot.event
async def on_ready():
    print('Logged on as ')
    print(bot.user.name)
    print(bot.user.id)
    print('-----')

@bot.event
async def on_message_delete(message):
    deletedAthr.clear()
    deletedChnl.clear()
    deletedMsgs.clear()

    author = str(message.author) 
    deletedAthr.append(author)

    channel= '<#'+str(message.channel.id)+'>: '
    deletedChnl.append(channel)

    content= str(message.content)
    deletedMsgs.append(content)

@bot.event
async def on_message_edit(message_before, message_after):
    editedMsgA.clear()
    editedMsgB.clear()
    editedAthr.clear()

    author = message_before.author
    editedAthr.append(author)

    msgb4 = message_before.content
    editedMsgB.append(msgb4)

    msga = message_after.content
    editedMsgA.append(msga)

@bot.command()
async def ldm(ctx):
    try:
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        embedVar = discord.Embed(title=deletedAthr[0], description=deletedMsgs[0], color=0xff0000)
        embedVar.add_field(name="Time: ", value=current_time)
        embedVar.add_field(name="Channel: ", value=deletedChnl[0])

        await ctx.send(embed = embedVar)
    except:
        await ctx.send('I couldnt find any deleted messages. :(')

@bot.command()
async def lem(ctx):
    try:
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        embedVar = discord.Embed(title="👁️Message Edit Watcher👁️", description = current_time)
        embedVar.add_field(name="Message Before: ", value=editedMsgB[0])
        embedVar.add_field(name="Message After: ", value=editedMsgA[0])
        embedVar.set_author(name=editedAthr[0],icon_url=editedAthr[0].avatar_url)

        await ctx.send(embed = embedVar)
    except:
        await ctx.send('I couldnt find any edited messages. :(')

sudoPriv = None
sudoers = open('sudoers.txt', 'r').read()
sudos = open('sudo.txt', 'r+')
sudosContent = sudos.read()
sudos.seek(0)
sudos.truncate()
sudos.write('False')

@bot.command()
async def sudo(message):
    print(sudoers)
    if str(message.author.id) in sudoers:
        sudos = open('sudo.txt', 'r+')
        sudos.seek(0)
        sudos.truncate()
        sudos.write('True')
        sudos.close()
        print(sudosContent)
        await message.channel.send('200')
    if not str(message.author.id) in sudoers:
        await message.channel.send(f'<@{message.author.id}> is not in the sudoers file. This incident will be reported.')
        sudos.seek(0)
        sudos.truncate()
        sudos.write('False')
        sudos.close()
        print(sudosContent)

@bot.command()
async def hello(message):
    await message.channel.send('Hello!')

@bot.command()
async def dt (ctx):
    now = datetime.now()
    formatTime = now.strftime("%a, %B %d, %Y | %H:%M")
    await ctx.reply('It is: ' + formatTime)

@bot.command()
async def delete(ctx, amount):
    try:
        amount = int(amount)
        if ctx.author.id == 342874810868826112:
            return
        else:
            if amount > 100:
                ctx.send('Thats too many messages for me!')
            else:
                await ctx.channel.purge(limit=amount)

    except:
        ctx.send('An error occured.')

@bot.command()
async def add(ctx, *nums):
    result = 0
    for num in nums:
        try:
            result += int(num)
        
        except:
            await ctx.send('Numbers, please!')
            break
    await ctx.send("{} = {}".format((' + '.join(map(str, list(nums)))), result))

@bot.command()
async def dv(ctx, num1, num2):
    try:
        await ctx.send(f'{int(num1)/int(num2)}')
        
    except:
        await ctx.send('Numbers, please!')    

@bot.command()
async def mul(ctx, *nums):
    result = 1
    for num in nums:
        try:
            result *= int(num)
        except:
            await ctx.send('Numbers, please!')    
            break
    await ctx.send(f'{result}')


@bot.command()
async def keyword(ctx, *, word:str):
    # channel = bot.get_channel(ctx.channel.id)
    messages = await ctx.channel.history(limit=200).flatten()

    for msg in messages:
        if word in msg.content:
            await ctx.send(msg.jump_url)
            time.sleep(1.2)

@bot.command()
async def cry(ctx):
    await ctx.message.delete()
    await ctx.send("<:chriscry:758862800637657118>")

@bot.command()
async def pog(ctx):
    await ctx.message.delete()
    await ctx.send("<:pog:766067548520448001>")


@bot.command()
async def val(ctx, name, tag):
    try:
        response = requests.get(f'https://api.henrikdev.xyz/valorant/v1/mmr/na/{name}/{tag}')
        jsonR = response.json()

        def last_2_digits_at_best(n):
            return float(str(n)[-3:]) if '.' in str(n)[-2:] else int(str(n)[-2:])
        fElo = last_2_digits_at_best(jsonR["data"]["elo"])

        embedR = discord.Embed(title=name+"#"+tag, description=jsonR["data"]["currenttierpatched"], color=0x0000ff)
        embedR.add_field(name="Elo: ", value= str(fElo) + "/100")
        embedR.add_field(name="Last Game Change: ", value=jsonR["data"]["mmr_change_to_last_game"])
        await ctx.send(embed = embedR)
    except:
        await ctx.send("I couldn't find a VALORANT profile with that name and/or tag. Try again. :(")

@bot.command()
async def ras(ctx, option=''):
    agentList = ["Astra", "Breach", "Skye", "Yoru", "Phoenix", "Brimstone", "Sova", "Jett", "Reyna", "Omen", "Viper", "Cypher", "Killjoy", "Sage", "Raze"]
    agentListNF = ["Astra", "Brimstone", "Sova", "Jett", "Reyna", "Omen", "Viper", "Cypher", "Killjoy", "Sage", "Raze"]
    
    embedN = discord.Embed(title="Random Agent Selector", description=random.choice(agentList))
    embedNF = discord.Embed(title="Random Agent Selector", description=random.choice(agentListNF))

    if option == "nf":
        await ctx.send(embed = embedNF)
    if not option:
        await ctx.send(embed=embedN)

@bot.command(pass_context=True)
async def randomchoice(ctx, *, question):
    randomAnswers = ["Don't bother asking", "It will certainly happen", "Only to you.", "Maybe or maybe not"]

    embed8 = discord.Embed(title="The Magic 8ball", description=random.choice(randomAnswers))

    await ctx.send(embed = embed8)
bot.command(name="ball", pass_context=True,)(randomchoice.callback)

@bot.command()
async def write(ctx, title:str, url:str):
    if ctx.message.author.id == 564466359107321856 and sudoPriv:
        def write_json(data, filename='clips.json'):
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)

        with open('clips.json') as json_file:
            data = json.load(json_file)
            
            temp = data['clips']
            clips = {
                'title': title,
                'url': url
            }
            temp.append(clips)
            
        write_json(data)
    else:
        await ctx.send('You are not authorized to use this command.')

@bot.command()
async def read(ctx, title=''):
    if not title:
        titles = []
        with open('clips.json') as f:
            data = json.load(f)
            dataClips = data['clips']
        for i in dataClips:
            titles.append(i['title'])
        await ctx.send(f'These are the clip titles I\'ve got: ```{str(titles)}```. Run command ``=read [title]`` to watch the clip.')
    else:        
        with open('clips.json') as f:
            data = json.load(f)
            dataClips = data['clips']
        
        for i in dataClips:
            if i['title'] == title:
                await ctx.send(i['url'])

@bot.command()
async def kissme(ctx):
    if ctx.message.author.id == 543866993602723843 or ctx.message.author.id == 564466359107321856 or ctx.message.author.id == 564562239739396098:
       await ctx.send('Ok <:happier:821406857678946394> , nht.')
    else:
       await ctx.send('Ew, no.') 

@bot.command()
async def vote(ctx):
    voteMsg = await ctx.channel.send('This is a test message for reactions.')
    await voteMsg.add_reaction('✅')
    await voteMsg.add_reaction('❎')
    await asyncio.sleep(30)
    voteMsg = await voteMsg.channel.fetch_message(voteMsg.id)
    positive = 0
    negative = 0

    for reaction in voteMsg.reactions:
        if reaction.emoji == '✅':
            positive = reaction.count - 1
        if reaction.emoji == '❎':
            negative = reaction.count - 1
    
    print(f'Vote Result: {positive} postiive and {negative} negative reactions.')

@bot.command()
async def quiz(ctx):
    voteMsg = await ctx.channel.send('Check mark or X mark?')
    await voteMsg.add_reaction('✅')
    await voteMsg.add_reaction('❎')
    await asyncio.sleep(10)
   
    voteMsg = await voteMsg.channel.fetch_message(voteMsg.id)
    positive = 0
    negative = 0
    randomC = random.choice(['✅', '❎'])
    
    try:
        if randomC == '✅' and positive > 0:
            await ctx.send('You guessed correctly!')
        elif randomC == '❎' and negative > 0:
            await ctx.send('You guessed correctly!')
        else:
            await ctx.send('You did not guess correctly.')
        
        for reaction in voteMsg.reactions:
            if reaction.emoji == '✅':
                positive = reaction.count - 1
            if reaction.emoji == '❎':
                negative = reaction.count - 1
    
            
    except:
        await ctx.send('An error occured.')


WHEN = time(9, 28, 0)  # 6:00 PM
channel_id = 801520877753597974 # Put your channel id here

async def called_once_a_day():
    await bot.wait_until_ready()
    channel = bot.get_channel(channel_id) 
    await channel.send(f"<@564466359107321856>, <@564562239739396098>, <@543866993602723843>, <@380761443479322624> This is an automated message to remind you all to take attendance at {WHEN} EDT. This message was set to send to <#{channel_id}> by <@564466359107321856>.")

async def background_task():
    now = datetime.now()
    if now.time() > WHEN:  
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
        seconds = (tomorrow - now).total_seconds()  
        await asyncio.sleep(seconds)   
    while True:
        now = datetime.now() 
        target_time = datetime.combine(now.date(), WHEN)  
        seconds_until_target = (target_time - now).total_seconds()
        await asyncio.sleep(seconds_until_target)  
        await called_once_a_day()  
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
        seconds = (tomorrow - now).total_seconds()  
        await asyncio.sleep(seconds)   

@bot.command(name='join', help='Joins the voice channel.')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send('{} is not connected to a voice channel'.format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()


@bot.command(name='leave', help='Leaves voice channel.')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")

@bot.command(name='play', help='play a youtube URL.')
async def play(ctx, url):
    if str(ctx.message.author.id) in sudoers and sudosContent == 'True':
        voice = get(bot.voice_clients, guild=ctx.guild)

        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            voice.play(discord.FFmpegPCMAudio(executable="/usr/bin/ffmpeg", source=filename))
        await ctx.send('**Now playing** {}'.format(filename))
    else:
        await ctx.send(f'{ctx.message.author} is not in the sudoers file. This instance will be reported.')

@bot.command()
async def rmd(ctx, time, *, reason:str = ''):
    try:
        timeLen = len(time)
        if not len(reason):
            newReason = f'<@{ctx.message.author.id}>, you set a reminder ``{time}`` ago without a reason.'
        else: 
            newReason = f'<@{ctx.message.author.id}>, you set a reminder ``{time}`` ago with reason ``{reason}``'
        if timeLen == 3:
            lastChar = time[-1]
            if lastChar == 'm':
                newTime = int(60*int(time[:2]))
                await asyncio.sleep(newTime)
                await ctx.send(newReason)
            elif lastChar == 's':
                newTime = int(time[:2])
                await asyncio.sleep(newTime)
                await ctx.send(newReason)
            elif lastChar == 'h':
                newTime = int(60*60*int(time[:1]))
                await asyncio.sleep(newTime)
                await ctx.send(newReason)
            else:
                await ctx.send('That amount of time is not supported!')
        elif timeLen == 2:
            lastChar = time[-1]
            if lastChar == 'm':
                newTime = int(60*int(time[:1]))
                print(f'sleeping for {newTime} seconds.')
                await asyncio.sleep(newTime)
                await ctx.send(newReason)
            elif lastChar == 's':
                newTime = int(time[:1])
                await asyncio.sleep(newTime)
                await ctx.send(newReason)
            elif lastChar == 'h':
                newTime = int(60*60*int(time[:1]))
                await asyncio.sleep(newTime)
                await ctx.send(newReason)
            else:
                await ctx.send('That amount of time is not supported!')
        else:
            await ctx.send('Value ``time`` must be of length ``2``.')
    except:
        await ctx.send('An error occured in the command. Check usage, then try again.')


@bot.command()
async def whoami(ctx, user: discord.Member = None):
    if user == None:
        user = ctx.author
    
    secondFont = ImageFont.truetype("./fonts/Hind-Regular.ttf", 110)
    wanted = Image.open("./imgs/background.jpg")

    draw = ImageDraw.Draw(wanted)

    asset = user.avatar_url_as(size=128)
    data = BytesIO(await asset.read())
    pfp = Image.open(data)

    pfp = pfp.resize((450, 450))
    secondText = f'{user.name}#{user.discriminator}'

    draw.text((150, 1075), secondText, (255, 255, 255), font=secondFont)

    wanted.paste(pfp, (250, 500))

    wanted.save("profile.jpg")
    
    await ctx.send(file = discord.File("profile.jpg"))

@bot.command()
async def braindead(ctx, user: discord.Member = None):
    if user == None:
        user = ctx.author

    braindead = Image.open("./imgs/braindead.jpg")
    
    asset = user.avatar_url_as(size=128)
    data = BytesIO(await asset.read())
    pfp = Image.open(data)

    pfp = pfp.resize((750, 750))

    braindead.paste(pfp, (850, 650))

    braindead.save("stupid.jpg")

    await ctx.send(file = discord.File("stupid.jpg"))


@bot.command()
async def gigachad(ctx, user: discord.Member = None):
    if user == None:
        user = ctx.author

    gigachad = Image.open("./imgs/gigachad.jpg")
    
    asset = user.avatar_url_as(size=128)
    data = BytesIO(await asset.read())
    pfp = Image.open(data)

    pfp = pfp.resize((250, 250))

    gigachad.paste(pfp, (250, 35))

    gigachad.save("chad.jpg")

    await ctx.send(file = discord.File("chad.jpg"))

@bot.command()
async def soyjak(ctx, user: discord.Member = None):
    if user == None:
        user = ctx.author

    soyjak = Image.open("./imgs/soyjak.jpg")
    
    asset = user.avatar_url_as(size=128)
    data = BytesIO(await asset.read())
    pfp = Image.open(data)

    pfp = pfp.resize((300, 300))

    soyjak.paste(pfp, (160, 190))

    soyjak.save("soy.jpg")

    await ctx.send(file = discord.File("soy.jpg"))


@bot.command()
async def talk(ctx, *, args):
    rs = RandomStuff(api_key= AI_API_KEY)
    response = rs.get_ai_response(args)
    await ctx.send(response)
    rs.close()

@bot.command()
async def test(ctx):
    print(sudosContent)
    if sudosContent == 'True' and str(ctx.author.id) in sudoers:
        await ctx.send('sudo works')
    
@bot.command()
async def gh(ctx):
    await ctx.send('https://github.com/5late/Pepe-Bot')

@bot.command()
async def bj(ctx):
    cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K', 'A']
    faceCards = ['J','Q','K']
    playerCard = []
    dealerCard = []
    randomCard = random.choice(cards)
    shownCard = random.choice(cards)

    def intize(cpc, cdc):
        dealerCard.append(shownCard)
        dealerCard.append(randomCard)
        playerCard.append(randomCard)
        playerCard.append(randomCard)
        print(playerCard)
        print(shownCard)
        print(dealerCard)
        playerCount = int(cpc)
        dealerCount = int(cdc)
        for playerCardnow in playerCard:
            if playerCardnow in faceCards:
                playerCount += 10
            elif int(playerCount) <= 10 and playerCardnow == 'A':
                playerCount += 11
            elif int(playerCount) > 10 and playerCardnow == 'A':
                playerCount+= 1
            else:
                playerCount+=int(playerCardnow)
        print(playerCount)
        for dealerCardnow in dealerCard:
            if dealerCardnow in faceCards:
                dealerCount += 10
            elif int(dealerCount) <= 10 and dealerCardnow == 'A':
                dealerCount += 11
            elif int(dealerCount) > 10 and dealerCardnow == 'A':
                dealerCount+= 1
            else:
                dealerCount+=int(dealerCardnow)
        print(dealerCount)

    intize(0,0)

    def check(author):
        def inner_check(ctx):
            return ctx.author == author and ctx.content == 'h' or 's'
        return inner_check
    await ctx.send(f'Your cards are {playerCard}. Do you want to hit or stand?')
    
    msg = await bot.wait_for('message', check=check(ctx.author), timeout=30)
    if msg.content == 'h':
        playerCard.append(randomCard)
        await ctx.send(f'Your new cards are: {playerCard}')
        msg2 = await bot.wait_for('message', check=check(ctx.author), timeout=30)
    
        if msg2.content == 'h':
            playerCard.append(randomCard)
            await ctx.send(f'Your new cards are: {playerCard}')
            msg3 = await bot.wait_for('message', check=check(ctx.author), timeout=30)
            
            if msg3.content == 'h':
                playerCard.append(randomCard)
                await ctx.send(f'Your new cards are: {playerCard}')
                msg4 = await bot.wait_for('message', check=check(ctx.author), timeout=30)
            elif msg3.content == 's':
                await ctx.send(f'You stood. The dealers cards were: {dealerCard}.')
        
        elif msg2.content == 's':
            await ctx.send(f'You stood. The dealers cards were: {dealerCard}.')
        
    elif msg.content == 's':
        await ctx.send(f'You stood. The dealers cards were: {dealerCard}.')
                


if __name__ == "__main__":
    bot.loop.create_task(background_task())
    bot.run(DISCORD_TOKEN)