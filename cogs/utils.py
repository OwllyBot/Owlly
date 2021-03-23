import discord
from discord.enums import _is_descriptor
from discord.ext import commands, tasks
import re
import sqlite3
from typing import Optional, Union
from discord import Colour
from discord.ext.commands import ColourConverter
import unidecode as uni

from discord.ext.commands.errors import CommandError
intents = discord.Intents(messages=True, guilds=True,reactions=True, members=True)


class CogUtils(commands.Cog, name="Utilitaire", description="Une série de commande permettant notamment le débug, mais donnant aussi des informations."):
	def __init__(self, bot):
		self.bot = bot
	
	@commands.Cog.listener()
	async def on_ready(self):
		print("[LOGS] ONLINE")

	@commands.Cog.listener()
	async def on_message(self, message):
		channel = message.channel
		db = sqlite3.connect("owlly.db", timeout=3000)
		c = db.cursor()
		prefix = "SELECT prefix FROM SERVEUR WHERE idS = ?"
		c.execute(prefix, (int(message.guild.id), ))
		prefix = c.fetchone()
		if prefix is not None:
			prefix = prefix[0]
		if self.bot.user.mentioned_in(message) and 'prefix' in message.content:
			await channel.send(f'Mon prefix est `{prefix}`')
		
	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		db = sqlite3.connect("owlly.db", timeout=3000)
		c = db.cursor()
		sql = "INSERT INTO SERVEUR (prefix, idS) VALUES (?,?)"
		var = ("?", guild.id)
		c.execute(sql, var)
		db.commit()
		c.close()
		db.close()

	@commands.command(name="ping", brief="Permet d'avoir la latence du bot.", help="Permet d'avoir la latence du bot.")
	async def ping(self, ctx):
		await ctx.send(f"🏓 Pong with {str(round(self.bot.latency, 2))}")
	
	@commands.Cog.listener()
	async def on_message(self, message):
		channel = message.channel
		if self.bot.user.mentioned_in(message) and 'prefix' in message.content:
			db = sqlite3.connect("owlly.db", timeout=3000)
			c = db.cursor()
			prefix = "SELECT prefix FROM SERVEUR WHERE idS = ?"
			c.execute(prefix, (int(message.guild.id),))
			prefix = c.fetchone()
			if prefix is not None:
				prefix = prefix[0]
			else:
				prefix="?"
			await channel.send(f'Mon prefix est `{prefix}`')
		else:
			if message.type == discord.MessageType.pins_add:
				await message.delete()


	@commands.command(name="prefix", help="Affiche le prefix du bot. Il est possible de l'obtenir en le mentionnant simplement.", brief="Donne le préfix du bot. ")
	async def prefix(self, ctx):
		server = ctx.guild.id
		db = sqlite3.connect("owlly.db", timeout=3000)
		c = db.cursor()
		prefix = "SELECT prefix FROM SERVEUR WHERE idS = ?"
		c.execute(prefix, (server, ))
		prefix = c.fetchone()
		message = await ctx.send(f"Mon préfix est {prefix}")
		return commands.when_mentioned_or(prefix)(self.bot, message)

	@commands.command(name="whoami", help="Affiche simplement votre nom...", brief="Affiche votre nom.")
	async def whoami(self, ctx):
		await ctx.send(f"You are {ctx.message.author.name}")

	@commands.command(name="info", help="Affiche des infos sur le bot.", brief="Informations sur le bot.")
	async def info(self, ctx):
		db = sqlite3.connect("owlly.db", timeout=3000)
		c = db.cursor()
		prefix = "SELECT prefix FROM SERVEUR WHERE idS = ?"
		c.execute(prefix, (int(ctx.guild.id),))
		prefix = c.fetchone()
		if prefix is not None:
			prefix = prefix[0]
		else:
			prefix="?"
		embed = discord.Embed(
			title="Owlly", description=f"\n 🦉 Développeur : @Mara#3000 \n <:commandline:823856723441221692> Prefix: `{prefix}`\n 🏓 Latence : {str(round(self.bot.latency, 2))}\n <:python:823857333259730964> Language : Python \n<:git:823857771584684032> Github : [Github](https://github.com/OwllyBot/OwllyDocs)", color=0x438f8c)
		await ctx.send(embed=embed)
	
	@commands.command(name="bug", help="Permet d'afficher les infos afin de signaler un bug.", brief="Informations sur le signalement de bug.")
	async def bug(self, ctx):
		bloc="```\n	# Commande : \n # Résultat : \n # Reproduction : \n # Description / autres informations : \n # Screenshot :\n```"
		embed = discord.Embed(title="Signaler un bug",
		                      description=f"Vous avez vu un bug et vous aimeriez le signaler ? Voici la marche à suivre : \n:white_small_square: Aller sur (le github)[https://github.com/OwllyBot/OwllyDocs/issues]\n:white_small_square: Remplissez la template suivante en donnant le plus d'information possible :\n {bloc}\n\n N'oubliez pas de créer un compte Github. Vous pouvez aussi MP @Mara#3000 avec la description du bug.", color=0x438f8c)
		await ctx.send(embed=embed)
	

	@commands.command(aliases=["purge", "clean"], help="Permet de nettoyer un channel. Attention, nécessite d'être administrateur.", brief="Purge un channel.")
	@commands.has_permissions(administrator=True)
	async def clear(self, ctx, nombre: int):
		messages = await ctx.channel.history(limit=nombre + 1).flatten()
		a = 0
		for message in messages:
			await message.delete()
			a += 1
		await ctx.send(f"J'ai nettoyé {a} messages", delete_after=30)
	
	@commands.command()
	async def convertColor(self, ctx, color):
		print(color)
		try:
			colur = await ColourConverter.convert(self,ctx, color)
		except CommandError:
			colur=Colour.random()
			print(colur)

	@commands.command(brief="Une recherche dans un channel", help="Permet de chercher un texte parmi le channel fixée", aliases=['search'])
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
			msg_content=[]
			msg_content_uni=[]
			for i in messages:
				msg_content_uni.append(uni.unidecode(i.content))
				msg_content.append(i.content)
			w = re.compile(f"(.*)?{uni.unidecode(word)}(.*)?(\W+)?:",flags=re.IGNORECASE| re.UNICODE)
			search=list(filter(w.match,msg_content_uni))
			lg=len(search)
			if lg == 0:
				await ctx.send("Pas de résultat.")
				await ctx.message.delete()
			elif lg==1:
				found=search[0]
				for msg in messages:
					if found in uni.unidecode(msg.content):
						await ctx.send(f"{msg.content}")
				await ctx.message.delete()
			else:
				phrase=[]
				for i in search:
					for msg in messages:
						if i in msg.content:
							phrase.append(f":white_small_square:{msg.content}")
				phrase_rep="\n".join(phrase)
				await ctx.send(f"__Résultats__ :\n{phrase_rep}")
				await ctx.message.delete()

def setup(bot):
	bot.add_cog(CogUtils(bot))
