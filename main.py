import discord
from discord.ext import commands
from discord.utils import get
from discord import CategoryChannel
import os
import sqlite3

bot = commands.Bot(command_prefix=">")
token = os.environ.get('DISCORD_BOT_TOKEN')

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("ouvrir des portes !"))
    print("[LOGS] ONLINE")
@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong with {str(round(bot.latency, 2))}")
@bot.command(name="whoami")
async def whoami(ctx):
    await ctx.send(f"You are {ctx.message.author.name}")
@bot.command()
async def clear(ctx, amount=3):
    await ctx.channel.purge(limit=amount)

@bot.command()
async def config_appart(ctx):
    await ctx.message.delete()
    def checkRep(message):
        return message.author == ctx.message.author and ctx.message.channel == message.channel
    db = sqlite3.connect("owlly.db")
    c = db.cursor()
    question = await ctx.send (f"Quel est le titre de l'embed ?")
    titre = await bot.wait_for("message", timeout = 300, check = checkRep)
    typeM = titre.content
    await question.delete()
    question = await ctx.send (f"Quelle est sa description ?")
    desc = await bot.wait_for("message", timeout=300, check=checkRep)
    await question.delete()
    question = await ctx.send (f"Quelle couleur voulez vous utiliser ?")
    color = await bot.wait_for("message", timeout=300, check=checkRep)
    col = color.content
    if (col.find ("#") == -1):
        await ctx.send (f"Erreur ! Vous avez oublié le # !")
        return
    else:
        await question.delete()
        col = col.replace("#", "0x")
        col = int(col, 16)
    embed = discord.Embed(title=titre.content, description=desc.content, color=col)
    react = await ctx.send(embed=embed)
    await react.add_reaction("🏠")
    sql= ("INSERT INTO CONFIG (type, chan, mid) VALUES (?,?,?)")
    mid= react.id
    chan = react.channel.id
    await desc.delete()
    await titre.delete()
    await color.delete()
    var=(typeM, chan, mid)
    print(var)
    c.execute(sql, var)
    db.commit()
    c.close()
    db.close()

@bot.command()
async def config_category(ctx):
    emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    def checkEmoji(reaction, user):
        return ctx.message.author == user and message.id == reaction.message.id and (str(reaction) in emote)
    def checkRep(message):
        return message.author == ctx.message.author and ctx.message.channel == message.channel
    db = sqlite3.connect("owlly.db")
    c = db.cursor()
    chan = []
    question = await ctx.send("Merci d'envoyer l'ID des catégories que vous souhaitez utiliser pour cette configuration.")
    while True:
        channels = await bot.wait_for("message", timeout=300, check = checkRep)
        if channels.content.lower() == 'stop':
            break
        elif channels.content.lower() == 'cancel':
            return
        chan.append(channels.content)
        await channels.delete()
    if len(chan) >= 10 :
        await ctx.send ("Erreur ! Vous ne pouvez pas mettre plus de 9 catégories !")
        return
    namelist=[]
    for i in range(0,len(chan)):
        number=int(chan[i])
        guild= ctx.message.guild
        cat = get(guild.categories, id=number)
        print (cat)
        phrase = f"{emoji[i]} : {cat}"
        namelist.append(phrase)
    msg = "\n".join(namelist)
    await ctx.send (f"Votre message sera donc envoyé dans le ou les canaux suivants :\n {msg}")
    await ctx.send (f"Quel est le titre de l'embed ?")
    titre = await bot.wait_for("message", timeout = 300, check = checkRep)
    question = await ctx.send (f"Quelle couleur voulez vous utiliser ?")
    color = await bot.wait_for("message", timeout=300, check=checkRep)
    col = color.content
    if (col.find ("#") == -1):
        await ctx.send (f"Erreur ! Vous avez oublié le # !")
        return
    else:
        await question.delete()
        col = col.replace("#", "0x")
        col = int(col, 16)
    embed = discord.Embed(title=titre.content, description=msg, color=col)
    react = await ctx.send(embed=embed)
    for i in range(0,len(chan)):
        await react.add_reaction(emoji[i])
    titre = titre.content
    sql = ("INSERT INTO CHANNEL (titre, category, channel, mid) VALUES (?,?,?,?)")
    mid= react.id
    creat = react.channel.id
    var = (titre, chan, creat, mid)
    c.execute(sql, var)
    db.commit()
    c.close()
    db.close()

@bot.command()
async def msg(ctx):
    mid = 803968284072214548
    chan = bot.get_channel(803737008450043934)
    message = await chan.fetch_message(803968284072214548)
    reaction = message.content
    print(reaction)

@bot.event
async def on_reaction_add (ctx, reaction, user):
    db = sqlite3.connect("owlly.db")
    c = db.cursor()
    c.execute("SELECT * FROM CONFIG")
    appart = c.fetchall()
    appartDict={}
    for i in range(0, (len(appart))):
        extra = {appart[i][0]:(appart[i][1], appart[i][2])}
        appartDict.update(extra)
    # On a donc un dictionnaire avec les channels d'appartement (de toute façon à la fin y'aura probablement qu'un seul). On va faire pareil, mais cette fois pour les bâtiments. 
    c.execute("SELECT * FROM CHANNEL")
    room = c.fetchall()
    roomDict = {}
    for i in range(0, (len(room))):
        extra={room[i][0]:(room[i][1],room[i][2], room[i][3], room[i][4])}
        roomDict.update(extra)
    

bot.run(token)
