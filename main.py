import discord
from discord.ext import commands
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
async def appartement(ctx):
    def checkRep(message):
        return message.author == ctx.message.author and ctx.message.channel == message.channel
    db = sqlite3.connect("owlly.db")
    c = db.cursor()
    data=c.fetchall()
    question = await ctx.send (f"Quel est le titre de l'embed ?")
    titre = await bot.wait_for("message", timeout = 300, check = checkRep)
    titre = titre.content
    question = await ctx.send (f"Quelle est sa description ?")
    desc = await bot.wait_for("message", timeout=300, check=checkRep)
    desc = desc.content
    question = await ctx.send (f"Quelle couleur voulez vous utiliser ?")
    col = await bot.wait_for("message", timeout=300, check=checkRep)
    col = col.content
    if (col.find ("#") == -1):
        await ctx.send (f"Erreur ! Vous avez oublié le # !")
        return
    else:
        col = col.replace("#", "0x")
        col = int(col, 16)
    embed = discord.Embed(title=titre, description=desc, color=col)
    react = await ctx.send(embed=embed)
    await react.add_reaction("🏠")
    sql= ("INSERT INTO config (type, chan, mid) VALUES (?,?,?)")
    mid= react.id
    chan = react.channel.id
    var=(titre, chan, mid)
    print(var)
    c.execute(sql, var)
    db.commit()
    c.close()
    db.close()

@bot.command()
async def dbtest(ctx):
    db = sqlite3.connect("owlly.db")
    c = db.cursor()
    c.execute("SELECT * FROM config")
    data = c.fetchall()
    for x in data:
        print(x)
bot.run(token)
