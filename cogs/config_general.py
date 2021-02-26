import discord
from discord.ext import commands, tasks
import sqlite3
intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True)

class CogAdmins(commands.Cog):
  def __init__ (self, bot):
    self.bot = bot
    
  @commands.command()
  @commands.has_permissions(administrator=True)
  async def set_prefix(self, ctx, prefix):
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    sql = "UPDATE SERVEUR SET prefix = ? WHERE idS = ?"
    var = (prefix, ctx.guild.id)
    c.execute(sql, var)
    await ctx.send(f"Prefix changé pour {prefix}")
    db.commit()
    c.close()
    db.close()
      
  @commands.command(aliases=['lexique_config'])
  @commands.has_permissions(administrator=True)
  async def notes_config(self, ctx, chan:discord.TextChannel):
    server = ctx.guild.id
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    sql="UPDATE SERVEUR SET notes=? WHERE idS=?"
    chanID=chan.id
    var=(chanID,server)
    c.execute(sql,var)
    db.commit()
    c.close()
    db.close()
    await ctx.send(f"Le channels des notes est donc {chan}", delete_after=30)
    await ctx.message.delete()
    
  @commands.has_permissions(administrator=True)
  @commands.command()
  async def roliste(self, ctx, *role: discord.Role):
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    sql = "UPDATE SERVEUR SET roliste = ? WHERE idS = ?"
    role_list=[]
    if (len(role)) > 1:
      for i in role :
        role_list.append(str(i.id))
    else:
      role_str = str(role[0].id)
    role_str= ",".join((role_list))
    var = (role_str, ctx.guild.id)
    c.execute(sql, var)
    phrase=[]
    for i in role:
      phrase.append(i.name)
    phrase=", ".join(phrase)
    await ctx.send(f"Les rôles {phrase} ont bien été enregistré dans la base de données")
    db.commit()
    c.close()
    db.close()
  
def setup(bot):
  bot.add_cog(CogAdmins(bot))