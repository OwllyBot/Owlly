import discord
from discord.ext import commands, tasks
from discord.utils import get
from discord import CategoryChannel
from discord import NotFound
import os
import sqlite3
intents = discord.Intents(messages=True, guilds=True,reactions=True, members=True)

class memberAssign(commands.Cog):
 def __init__(self, bot):
  self.bot = bot
 
 @commands.command()
  async def member(self, ctx, user, visib, race, job):
   userID = 
   