import discord
from discord.ext import commands, tasks
from discord.utils import get
from discord import CategoryChannel
from discord import NotFound
import os
import sqlite3
intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True)

class CogUtils(commands.Cog):
  def __init__ (self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
      print("[LOGS] ONLINE")
      await self.bot.change_presence(activity=discord.Game("ouvrir des portes !"))


  @commands.Cog.listener()
  async def on_command_error(self, ctx, error):
      db = sqlite3.connect("owlly.db", timeout=3000)
      c = db.cursor()
      serv = ctx.guild.id
      sql = "SELECT prefix FROM SERVEUR WHERE idS = ?"
      c.execute(sql, (serv,))
      p = c.fetchone()
      p = p[0]
      if isinstance(error, discord.ext.commands.errors.CommandNotFound):
          await ctx.send(f"Commande inconnue ! \n Pour avoir la liste des commandes utilisables, utilise `{p}help` ou `{p}command`")


  @commands.Cog.listener()
  async def on_guild_join(self,guild):
      db = sqlite3.connect("owlly.db", timeout=3000)
      c = db.cursor()
      sql = "INSERT INTO SERVEUR (prefix, idS) VALUES (?,?)"
      var = ("?", guild.id)
      c.execute(sql, var)
      db.commit()
      c.close()
      db.close()


  @commands.Cog.listener()
  async def on_message(self,message):
      channel = message.channel
      db = sqlite3.connect("owlly.db", timeout=3000)
      c = db.cursor()
      prefix = "SELECT prefix FROM SERVEUR WHERE idS = ?"
      c.execute(prefix, (int(message.guild.id),))
      prefix = c.fetchone()
      if prefix is not None:
          prefix = prefix[0]
      if self.bot.user.mentioned_in(message) and 'prefix' in message.content:
          await channel.send(f'Mon prefix est `{prefix}`')


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


  @commands.command()
  async def ping(self,ctx):
    await ctx.send(f"🏓 Pong with {str(round(self.bot.latency, 2))}")


  @commands.command(name="whoami")
  async def whoami(self,ctx):
      await ctx.send(f"You are {ctx.message.author.name}")


  @commands.command()
  async def serv(self,ctx):
    await ctx.send(f"{ctx.message.guild.id}")


  @commands.command()
  async def clear(self,ctx, amount=3):
    await ctx.channel.purge(limit=amount)

  @commands.command(aliases=['command', 'commands', 'owlly'])
  async def help(self,ctx):
      db = sqlite3.connect("owlly.db", timeout=3000)
      c = db.cursor()
      serv = ctx.guild.id
      sql = "SELECT prefix FROM SERVEUR WHERE idS = ?"
      c.execute(sql, (serv,))
      p = c.fetchone()
      p = p[0]
      embed = discord.Embed(title="Liste des commandes",
                            description="", color=0xaac0cc)
      embed.add_field(name=f"Configurer les créateurs (administrateur)",
                      value=f":white_small_square: Ticket : `{p}ticket`\n :white_small_square: Catégories : `{p}category` \n :white_small_square: Créateur de pièce (1 catégorie) :`{p}channel`", inline=False)
      embed.add_field(name="Fonction sur les channels",
                      value=f"Vous devez être l'auteur original du channel et utiliser ses commandes sur le channel voulu !\n :white_small_square: Editer la description : `{p}desc description` ou `{p}description`\n :white_small_square: Pin un message : `{p}pins <idmessage>` \n :white_small_square: Unpin un message : `{p}unpin <idmessage>` \n :white_small_square: Changer le nom du channel : `{p}rename nom`", inline=False)
      embed.add_field(name="Administration",
                      value=f":white_small_square: Prefix : `{p}prefix` \n :white_small_square: Changer le prefix (administrateur) : `{p}set_prefix` \n :white_small_square: Changer le compteur des tickets (administrateur): `{p}recount nb`", inline=False)
      await ctx.send(embed=embed)
  
  @commands.command()
  async def prefix(self,ctx):
    server = ctx.guild.id
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    prefix = "SELECT prefix FROM SERVEUR WHERE idS = ?"
    c.execute(prefix, (server,))
    prefix = c.fetchone()
    message = await ctx.send(f"Mon préfix est {prefix}")
    return commands.when_mentioned_or(prefix)(self.bot, message)
    

def setup(bot):
  bot.add_cog(CogUtils(bot))
