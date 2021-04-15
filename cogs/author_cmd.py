import discord
from discord.ext import commands, tasks
import sqlite3
intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True)


class controlleur(commands.Cog, name="Auteur", description="Permet aux auteurs des channels de modifiers certains attributs du dit channel. Attention, toutes les commandes doivent être faites dans le channel créées."):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(aliases=['edit_desc'], brief="Edition de la description",help="Permet à un auteur de modifier la description de son channel.", usage="description du channel", description="La commande doit être faite sur le channel que l'on souhaite modifier.")
  async def desc(self, ctx, arg):
    await ctx.message.delete()
    channel_here = ctx.channel.id
    channel = self.bot.get_channel(channel_here)
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    sql = "SELECT channel_id FROM AUTHOR WHERE (userID = ? AND idS = ?)"
    var = (ctx.author.id, ctx.guild.id)
    c.execute(sql, var)
    list_chan = c.fetchall()
    list_chan = list(sum(list_chan, ()))
    if channel_here in list_chan:
      await channel.edit(topic=arg)
      await ctx.send("Changé !", delete_after=10)
    else:
      ctx.send("Erreur, vous n'êtes pas l'auteur de ce channel !",delete_after=30)
    c.close()
    db.close()

  @commands.command(usage="id du message à unpin", brief="Désépingle un message", help="Permet de désépingler un message.")
  async def unpin(self, ctx, id_message):
    await ctx.message.delete()
    channel_here = ctx.channel.id
    channel = self.bot.get_channel(channel_here)
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    sql = "SELECT channel_id FROM AUTHOR WHERE (userID = ? AND idS = ?)"
    var = (ctx.author.id, ctx.guild.id)
    c.execute(sql, var)
    list_chan = c.fetchall()
    list_chan = list(sum(list_chan, ()))
    if channel_here in list_chan:
      message = await channel.fetch_message(id_message)
      await message.unpin()
    else:
      await ctx.send("Vous n'êtes pas l'auteur de ce channel !",delete_after=10)
    c.close()
    db.close()

  @commands.command(aliases=['pin'], help="Permet d'épingler un message sur le channel", usage="id du message à épingler", brief="Epingle un message.")
  async def pins(self, ctx, id_message):
    await ctx.message.delete()
    channel_here = ctx.channel.id
    channel = self.bot.get_channel(channel_here)
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    sql = "SELECT channel_id FROM AUTHOR WHERE (userID = ? AND idS = ?)"
    var = (ctx.author.id, ctx.guild.id)
    c.execute(sql, var)
    list_chan = c.fetchall()
    list_chan = list(sum(list_chan, ()))
    if channel_here in list_chan:
      message = await channel.fetch_message(id_message)
      await message.pin()
    else:
      await ctx.send("Vous n'êtes pas l'auteur de ce channel !", delete_after=10)
    c.close()
    db.close()
	
  @commands.command(aliases=['name'], usage="nouveau nom", brief="Renomme un channel", help="Permet de changer le nom d'un channel, même un ticket, tant que vous êtes l'auteur. Attention, la commande doit-être faite dans le channel que vous souhaitez modifier.")
  async def rename(self, ctx, arg):
    await ctx.message.delete()
    channel_here = ctx.channel.id
    channel = self.bot.get_channel(channel_here)
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    sql = "SELECT channel_id FROM AUTHOR WHERE (userID = ? AND idS = ?)"
    var = (ctx.author.id, ctx.guild.id)
    c.execute(sql, var)
    list_chan = c.fetchall()
    list_chan = list(sum(list_chan, ()))
    if channel_here in list_chan:
        await channel.edit(name=arg)
        await ctx.send("Changé !", delete_after=10)
    else:
        await ctx.send("Erreur, vous n'êtes pas l'auteur de ce channel !", delete_after=30)
    c.close()
    db.close()

def setup(bot):
  bot.add_cog(controlleur(bot))
