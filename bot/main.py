import discord
from discord.ext import commands
import os

client = commands.Bot(command_prefix="!")
token = os.environ.get('DISCORD_BOT_TOKEN')
print(token)
@client.event
async def on_ready():
    await client.change_presence(status=activity=discord.Game("J'ouvre des portes !"))
    print("[LOGS] ONLINE")
@client.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong with {str(round(client.latency, 2))}")
@client.command(name="whoami")
async def whoami(ctx):
    await ctx.send(f"You are {ctx.message.author.name}")
@client.command()
async def clear(ctx, amount=3):
    await ctx.channel.purge(limit=amount)
client.run(token)
