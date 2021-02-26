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

  @commands.command()
  async def test(self, ctx):
    await ctx.message.delete()

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


    @commands.command(aliases=['search'])
    async def lexique(self, ctx, *, word:str):
        server = ctx.guild.id
        db = sqlite3.connect("owlly.db", timeout=3000)
        c = db.cursor()
        sql="SELECT notes FROM SERVEUR WHERE idS=?"
        c.execute(sql,(server,))
        chanID = c.fetchone()
        if chanID is None:
            await ctx.send("Vous n'avez pas configuré le channel des notes. Faites `notes_config` pour cela. ", delete_after=30)
            await ctx.message.delete()
            return
        else:
            chanID=chanID[0]
            chan=self.bot.get_channel(chanID)
            messages=await chan.history(limit=300).flatten()
            w = re.compile(f"{word}(\W+)?:", re.IGNORECASE)
            print(w)
            search=list(filter(w.match, messages))
            print(search)
            lg=len(search)
            if lg == 0:
                await ctx.send("Pas de résultat.")
                await ctx.message.delete()
            else:
                found=search[0]
                for msg in messages:
                    if found in msg.content:
                        await ctx.send(f"Résultat : \n {msg.content}")
                await ctx.message.delete()
    

def setup(bot):
  bot.add_cog(CogUtils(bot))
