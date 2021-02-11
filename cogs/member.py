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
 
 @commands.has_permissions(administrator=True)
 @commands.command()
 async def roliste(self, ctx, *role : discord.Role):
   db = sqlite3.connect("owlly.db", timeout=3000)
   c = db.cursor()
   #mettre rôle dans la DB + indiquer message qu'il a été enregistré
   #check pour la transfo en "tuple" comme les channels 
 
 
 @commands.command()
 async def member(self, ctx, user: discord.User, *role: str):
  addRole=[]
  infoNew = []
  for i in role:
    i=i.replace("<","")
    i=i.replace(">","")
    i=i.replace("@","")
    i=i.replace("&","")
    if i.isnumeric():
      i=int(i)
      roleCheck=get(ctx.guild.roles, id=i)
    else:
      roleCheck=get(ctx.guild.roles, name=i)
    if roleCheck is None:
      NewRole = await self.bot.create_role(name=i, mentionnable=True)
      await NewRole.edit(position = 14)
      addRole.append(NewRole)
      infoNew.append(NewRole.name)
    else:  
      addRole.append(i)
  roleInfo = []
  for plus in addRole:
    user.add_role(plus)
    roleInfo.append(plus.name)
  roleInfo=" ,".join(roleInfo)
  if (len (infoNew)) > 0:
    infoNew="\n ◽".join(infoNew)
    roleInfo=roleInfo+" "+infoNew
  await ctx.send(f"{user.display_name} est devenu un membre du serveur ! Il a donc reçu les rôles : {roleInfo}. ")

def setup(bot):
 bot.add_cog(memberAssign(bot))
   