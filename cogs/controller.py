import emoji
import discord
from discord.ext import commands, tasks
from discord.utils import get
from discord import CategoryChannel
import os
import sqlite3
import sys
import traceback
import keep_alive
import re
import random
from emoji import unicode_codes
from discord import Color
from discord import NotFound
intents = discord.Intents(messages=True,
                          guilds=True,
                          reactions=True,
                          members=True)


class controlleur(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="description", aliases=['desc', 'edit_desc'])
	async def description(self, ctx, arg):
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
			await ctx.delete()
		else:
			ctx.send("Erreur, vous n'êtes pas l'auteur de ce channel !",
			         delete_after=30)
			await ctx.delete()
		c.close()
		db.close()

  @commands.command(name="description", aliases=['desc', 'edit_desc'])
  async def description(self,ctx, arg):
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
        await ctx.message.delete()
    else:
      ctx.send("Erreur, vous n'êtes pas l'auteur de ce channel !", delete_after=30)
      await ctx.message.delete()
    c.close()
    db.close()

	@commands.command()
	async def unpin(self, ctx, id_message):
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
			await ctx.delete()
		else:
			await ctx.send("Vous n'êtes pas l'auteur de ce channel !",
			               delete_after=10)
			await ctx.delete()
		c.close()
		db.close()

  @commands.command(aliases=['pin'])
  async def pins(self,ctx, id_message):
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
      await ctx.message.delete()
    else:
      await ctx.send("Vous n'êtes pas l'auteur de ce channel !", delete_after=10)
      await ctx.message.delete()
    c.close()
    db.close()


  @commands.command()
  async def unpin(self,ctx, id_message):
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
        await ctx.message.delete()
    else:
        await ctx.send("Vous n'êtes pas l'auteur de ce channel !", delete_after=10)
        await ctx.message.delete()
    c.close()
    db.close()


  @commands.command(aliases=['name'])
  async def rename(self,ctx, arg):
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
        await ctx.message.delete()
    else:
        ctx.send("Erreur, vous n'êtes pas l'auteur de ce channel !",delete_after=30)
        await ctx.message.delete()
    c.close()
    db.close()


def setup(bot):
	bot.add_cog(controlleur(bot))
