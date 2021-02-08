import discord
from discord.ext import commands, tasks
from discord.utils import get
from discord import CategoryChannel
from discord import NotFound
import os
import sqlite3
import re
intents = discord.Intents(messages=True,
                          guilds=True,
                          reactions=True,
                          members=True)

# ▬▬▬▬▬▬▬▬▬▬▬ SEARCH CAT NAME ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬


class config(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	async def search_cat_name(self, ctx, name):
		emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

		def checkValid(reaction, user):
			return ctx.message.author == user and q.id == reaction.message.id and str(
			    reaction.emoji) in emoji

		cat_list = []
		for cat in ctx.guild.categories:
			cat_list.append(cat.name)
		w = re.compile(f".*{name}.*", re.IGNORECASE)
		search = list(filter(w.match, cat_list))
		search_list = []
		lg = len(search)
		if lg == 0:
			return 12
		elif lg == 1:
			name = search[0]
			name = get(ctx.guild.categories, name=name)
			number = name.id
			return number
		elif lg > 1 and lg < 10:
			for i in range(0, lg):
				phrase = f"{emoji[i]} : {search[i]}"
				search_list.append(phrase)
			search_question = "\n".join(search_list)
			q = await ctx.send(
			    f"Plusieurs catégories correspondent à ce nom. Pour choisir celle que vous souhaitez, cliquez sur le numéro correspondant :\n {search_question}"
			)
			for i in range(0, lg):
				await q.add_reaction(emoji[i])
			select, user = await self.bot.wait_for("reaction_add",
			                                       timeout=300,
			                                       check=checkValid)
			for i in range(0, lg):
				if str(select) == str(emoji[i]):
					name = search[i]
					mot = search[i]
			name = get(ctx.guild.categories, name=name)
			number = name.id
			await q.delete()
			await ctx.send(
			    f"Catégorie : {mot} ✅ \n > Vous pouvez continuer l'inscription des channels. ",
			    delete_after=30)
			return number
		else:
			await ctx.send(
			    "Il y a trop de correspondance ! Merci de recommencer la commande.",
			    delete_after=30)
			return

	@commands.has_permissions(administrator=True)
	@commands.command()
	async def ticket(self, ctx):
		def checkValid(reaction, user):
			return ctx.message.author == user and question.id == reaction.message.id and (
			    str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌")

		def checkRep(message):
			return message.author == ctx.message.author and ctx.message.channel == message.channel

		limit_content = 0
		mod_content = 0
		nb_dep_content = 0
		guild = ctx.message.guild
		await ctx.message.delete()
		db = sqlite3.connect("owlly.db", timeout=3000)
		c = db.cursor()
		question = await ctx.send(f"Quel est le titre de l'embed ?")
		titre = await self.bot.wait_for("message", timeout=300, check=checkRep)
		typeM = titre.content
		if typeM == "stop":
			await ctx.send("Annulation !", delete_after=10)
			await titre.delete()
			await question.delete()
			return
		await question.delete()
		question = await ctx.send(f"Quelle est sa description ?")
		desc = await self.bot.wait_for("message", timeout=300, check=checkRep)
		if desc.content == "stop":
			await ctx.send("Annulation !", delete_after=10)
			await desc.delete()
			await question.delete()
			return
		await question.delete()
		question = await ctx.send(
		    "Dans quel catégorie voulez-vous créer vos tickets ? Rappel : Seul un modérateur pourra les supprimer, car ce sont des tickets permanent.\n Vous pouvez utiliser le nom ou l'ID de la catégorie !"
		)
		ticket_chan = await self.bot.wait_for("message",
		                                      timeout=300,
		                                      check=checkRep)
		ticket_chan_content = ticket_chan.content
		cat_name = "none"
		if ticket_chan_content == "stop":
			await ctx.send("Annulation !", delete_after=10)
			await question.delete()
			await ticket_chan.delete()
			return
		else:
			if ticket_chan_content.isnumeric():
				ticket_chan_content = int(ticket_chan_content)
				cat_name = get(guild.categories, id=ticket_chan_content)
				if cat_name == "None":
					await ctx.send("Erreur : Cette catégorie n'existe pas !",
					               delete_after=30)
					return
			else:
				ticket_chan_content = await self.search_cat_name(
				    ctx, ticket_chan_content)
				cat_name = get(guild.categories, id=ticket_chan_content)
				if ticket_chan_content == 12:
					await ctx.send(
					    "Aucune catégorie portant un nom similaire existe, vérifier votre frappe.",
					    delete_after=30)
					return
				else:
					cat_name = get(guild.categories, id=ticket_chan_content)
		await question.delete()
		question = await ctx.send(f"Quelle couleur voulez vous utiliser ?")
		color = await self.bot.wait_for("message", timeout=300, check=checkRep)
		col = color.content
		if (col.find("#") == -1) and (col != "stop") and (col != "0"):
			await ctx.send(f"Erreur ! Vous avez oublié le # !",
			               delete_after=30)
			await question.delete()
			await color.delete()
			return
		elif col == "stop":
			await ctx.send("Annulation !", delete_after=10)
			await question.delete()
			await color.delete()
			return
		elif col == "0":
			await question.delete()
			col = "0xabb1b4"
			col = int(col, 16)
		else:
			await question.delete()
			col = col.replace("#", "0x")
			col = int(col, 16)
		question = await ctx.send("Voulez-vous ajouter une image ?")
		await question.add_reaction("✅")
		await question.add_reaction("❌")
		reaction, user = await self.bot.wait_for("reaction_add",
		                                         timeout=300,
		                                         check=checkValid)
		if reaction.emoji == "✅":
			await question.delete()
			question = await ctx.send(
			    "Merci d'envoyer l'image. \n**⚡ ATTENTION : LE MESSAGE EN REPONSE EST SUPPRIMÉ VOUS DEVEZ DONC UTILISER UN LIEN PERMANENT (hébergement sur un autre channel/serveur, imgur, lien google...)**"
			)
			img = await self.bot.wait_for("message",
			                              timeout=300,
			                              check=checkRep)
			img_content = img.content
			if img_content == "stop":
				await ctx.send("Annulation !", delete_after=10)
				await question.delete()
				await img.delete()
				return
			else:
				await question.delete()
				await img.delete()
		else:
			await question.delete()
			img_content = "none"
		question = await ctx.send("Voulez-vous fixer un nombre de départ ?")
		await question.add_reaction("✅")
		await question.add_reaction("❌")
		reaction, user = await self.bot.wait_for("reaction_add",
		                                         timeout=300,
		                                         check=checkValid)
		if reaction.emoji == "✅":
			await question.delete()
			question = await ctx.send("Merci d'indiquer le nombre de départ.")
			nb_dep = await self.bot.wait_for("message",
			                                 timeout=300,
			                                 check=checkRep)
			if nb_dep.content == "stop":
				await question.delete()
				await ctx.send("Annulation !", delete_after=10)
				await nb_dep.delete()
				return
			else:
				nb_dep_content = int(nb_dep.content)
				await question.delete()
		else:
			nb_dep_content = 0
			await question.delete()
		question = await ctx.send(
		    "Voulez-vous fixer une limite ? C'est à dire que le ticket va se reset après ce nombre."
		)
		await question.add_reaction("✅")
		await question.add_reaction("❌")
		reaction, user = await self.bot.wait_for("reaction_add",
		                                         timeout=300,
		                                         check=checkValid)
		if reaction.emoji == "✅":
			await question.delete()
			question = await ctx.send("Merci d'indiquer la limite.")
			limit = await self.bot.wait_for("message",
			                                timeout=300,
			                                check=checkRep)
			if limit.content == "stop":
				await ctx.send("Annulation !", delete_after=10)
				await question.delete()
				await limit.delete()
				return
			else:
				limit_content = int(limit.content)
				await limit.delete()
				mod_content = 0
				await question.delete()
				question = await ctx.send(
				    "Voulez-vous, après la limite, augmenter d'un certain nombre le numéro ?"
				)
				await question.add_reaction("✅")
				await question.add_reaction("❌")
				reaction, user = await self.bot.wait_for("reaction_add",
				                                         timeout=300,
				                                         check=checkValid)
				if reaction.emoji == "✅":
					await question.delete()
					question = await ctx.send("Quel est donc ce nombre ?")
					mod = await self.bot.wait_for("message",
					                              timeout=300,
					                              check=checkRep)
					if mod.content == "stop":
						await ctx.send("Annulation !", delete_after=10)
						await mod.delete()
						await question.delete()
						return
					else:
						mod_content = int(mod.content)
						await question.delete()
						await mod.delete()
				else:
					await question.delete()
		else:
			limit_content = 0
			mod_content = 0
			await question.delete()
		guild = ctx.message.guild
		question = await ctx.send(
		    f"Vos paramètres sont : \n Titre : {typeM} \n Numéro de départ : {nb_dep_content} \n Intervalle entre les nombres (on se comprend, j'espère) : {mod_content} (0 => Pas d'intervalle) \n Limite : {limit_content} (0 => Pas de limite) \n Catégorie : {cat_name}. \n\n Confirmez-vous ces paramètres ?"
		)
		await question.add_reaction("✅")
		await question.add_reaction("❌")
		reaction, user = await self.bot.wait_for("reaction_add",
		                                         timeout=300,
		                                         check=checkValid)
		if reaction.emoji == "✅":
			await question.delete()
			embed = discord.Embed(title=titre.content,
			                      description=desc.content,
			                      color=col)
			if img_content != "none":
				embed.set_image(url=img_content)
			question = await ctx.send(
			    "Vous pouvez choisir l'émoji de réaction en réagissant à ce message. Il sera sauvegardé et mis sur l'embed. Par défaut, l'émoji est : 🗒"
			)
			symb, user = await self.bot.wait_for("reaction_add", timeout=300)
			if symb.custom_emoji:
				if symb.emoji in guild.emojis:
					symbole = str(symb.emoji)
				else:
					symbole = "🗒"
			elif symb.emoji != "🗒":
				symbole = str(symb.emoji)
			else:
				symbole = "🗒"
			await question.delete()
			react = await ctx.send(embed=embed)
			await react.add_reaction(symbole)
			sql = "INSERT INTO TICKET (idM, channelM, channel, num, modulo, limitation, emote, idS) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
			id_serveur = ctx.message.guild.id
			id_message = react.id
			chanM = ctx.channel.id
			var = (id_message, chanM, ticket_chan_content, nb_dep_content,
			       mod_content, limit_content, symbole, id_serveur)
			await desc.delete()
			await titre.delete()
			await color.delete()
			await ticket_chan.delete()
			c.execute(sql, var)
			db.commit()
			c.close()
			db.close()
		else:
			await ctx.send("Annulation !", delete_after=30)
			await question.delete()
			await desc.delete()
			await titre.delete()
			await color.delete()
			await ticket_chan.delete()
			return

	@commands.has_permissions(administrator=True)
	@commands.command(aliases=['chan'])
	async def channel(self, ctx):
		def checkValid(reaction, user):
			return ctx.message.author == user and question.id == reaction.message.id and (
			    str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌")

		def checkRep(message):
			return message.author == ctx.message.author and ctx.message.channel == message.channel

		guild = ctx.message.guild
		await ctx.message.delete()
		db = sqlite3.connect("owlly.db", timeout=3000)
		c = db.cursor()
		question = await ctx.send(f"Quel est le titre de l'embed ?")
		titre = await self.bot.wait_for("message", timeout=300, check=checkRep)
		typeM = titre.content
		if typeM == "stop":
			await ctx.send("Annulation !", delete_after=10)
			await titre.delete()
			await question.delete()
			return
		await question.delete()
		question = await ctx.send(f"Quelle est sa description ?")
		desc = await self.bot.wait_for("message", timeout=300, check=checkRep)
		if desc.content == "stop":
			await ctx.send("Annulation !", delete_after=10)
			await desc.delete()
			await question.delete()
			return
		await question.delete()
		question = await ctx.send(
		    "Dans quel catégorie voulez-vous créer vos channels ? Rappel : Seul un modérateur pourra les supprimer, car ce sont des channels permanents.\n Vous pouvez utiliser le nom ou l'ID de la catégorie !"
		)
		ticket_chan = await self.bot.wait_for("message",
		                                      timeout=300,
		                                      check=checkRep)
		ticket_chan_content = ticket_chan.content
		cat_name = "none"
		if ticket_chan_content == "stop":
			await ctx.send("Annulation !", delete_after=10)
			await question.delete()
			await ticket_chan.delete()
			return
		else:
			if ticket_chan_content.isnumeric():
				ticket_chan_content = int(ticket_chan_content)
				cat_name = get(guild.categories, id=ticket_chan_content)
				if ticket_chan_content == "None":
					await ctx.send("Erreur : Cette catégorie n'existe pas !",
					               delete_after=30)
					return
			else:
				ticket_chan_content = await self.search_cat_name(
				    ctx, ticket_chan_content)
				if ticket_chan_content == 12:
					await ctx.send(
					    "Aucune catégorie portant un nom similaire existe, vérifier votre frappe.",
					    delete_after=30)
					return
				else:
					cat_name = get(guild.categories, id=ticket_chan_content)
		await question.delete()
		question = await ctx.send(f"Quelle couleur voulez vous utiliser ?")
		color = await self.bot.wait_for("message", timeout=300, check=checkRep)
		col = color.content
		if (col.find("#") == -1) and (col != "stop") and (col != "0"):
			await ctx.send(f"Erreur ! Vous avez oublié le # !",
			               delete_after=30)
			await question.delete()
			await color.delete()
			return
		elif col == "stop":
			await ctx.send("Annulation !", delete_after=10)
			await question.delete()
			await color.delete()
			return
		elif col == "0":
			await question.delete()
			col = "0xabb1b4"
			col = int(col, 16)
		else:
			await question.delete()
			col = col.replace("#", "0x")
			col = int(col, 16)
		question = await ctx.send("Voulez-vous ajouter une image ?")
		await question.add_reaction("✅")
		await question.add_reaction("❌")
		reaction, user = await self.bot.wait_for("reaction_add",
		                                         timeout=300,
		                                         check=checkValid)
		if reaction.emoji == "✅":
			await question.delete()
			question = await ctx.send(
			    "Merci d'envoyer l'image. \n**⚡ ATTENTION : LE MESSAGE EN REPONSE EST SUPPRIMÉ VOUS DEVEZ DONC UTILISER UN LIEN PERMANENT (hébergement sur un autre channel/serveur, imgur, lien google...)**"
			)
			img = await self.bot.wait_for("message",
			                              timeout=300,
			                              check=checkRep)
			img_content = img.content
			if img_content == "stop":
				await ctx.send("Annulation !", delete_after=10)
				await question.delete()
				await img.delete()
				return
			else:
				await question.delete()
				await img.delete()
		else:
			await question.delete()
			img_content = "none"
		guild = ctx.message.guild
		question = await ctx.send(
		    f"Vos paramètres sont : \n Titre : {typeM} \n Catégorie : {cat_name}. \n\n Confirmez-vous ces paramètres ?"
		)
		await question.add_reaction("✅")
		await question.add_reaction("❌")
		reaction, user = await self.bot.wait_for("reaction_add",
		                                         timeout=300,
		                                         check=checkValid)
		if reaction.emoji == "✅":
			await question.delete()
			embed = discord.Embed(title=titre.content,
			                      description=desc.content,
			                      color=col)
			if img_content != "none":
				embed.set_image(url=img_content)
			question = await ctx.send(
			    "Vous pouvez choisir l'émoji de réaction en réagissant à ce message. Il sera sauvegardé et mis sur l'embed. Par défaut, l'émoji est : 🗒"
			)
			symb, user = await self.bot.wait_for("reaction_add", timeout=300)
			if symb.custom_emoji:
				if symb.emoji in guild.emojis:
					symbole = str(symb.emoji)
				else:
					symbole = "🗒"
			elif symb.emoji != "🗒":
				symbole = str(symb.emoji)
			else:
				symbole = "🗒"
			await question.delete()
			react = await ctx.send(embed=embed)
			await react.add_reaction(symbole)
			sql = "INSERT INTO SOLO_CATEGORY (idM, channelM, category, idS, emote) VALUES (?, ?, ?, ?, ?)"
			id_serveur = ctx.message.guild.id
			id_message = react.id
			chanM = ctx.channel.id
			var = (id_message, chanM, ticket_chan_content, id_serveur, symbole)
			await desc.delete()
			await titre.delete()
			await color.delete()
			await ticket_chan.delete()
			c.execute(sql, var)
			db.commit()
			c.close()
			db.close()
		else:
			await ctx.send("Annulation !", delete_after=30)
			await question.delete()
			await desc.delete()
			await titre.delete()
			await color.delete()
			await ticket_chan.delete()
			return

	@commands.has_permissions(administrator=True)
	@commands.command()
	async def category(self, ctx):
		def checkValid(reaction, user):
			return ctx.message.author == user and question.id == reaction.message.id and (
			    str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌")

		def checkRep(message):
			return message.author == ctx.message.author and ctx.message.channel == message.channel

		emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
		db = sqlite3.connect("owlly.db", timeout=3000)
		c = db.cursor()
		chan = []
		question = await ctx.send(
		    "Merci d'envoyer l'ID des catégories (ou leurs noms) que vous souhaitez utiliser pour cette configuration. \n Utiliser `stop` pour valider la saisie et `cancel` pour annuler la commande. "
		)
		while True:
			channels = await self.bot.wait_for("message",
			                                   timeout=300,
			                                   check=checkRep)
			await channels.add_reaction("✅")
			if channels.content.lower() == 'stop':
				await channels.delete(delay=10)
				await ctx.send("Validation en cours !", delete_after=10)
				await question.delete()
				break
			elif channels.content.lower() == 'cancel':
				await channels.delete()
				await ctx.send("Annulation !", delete_after=10)
				await question.delete()
				return
			else:
				chan_search = channels.content
				if chan_search.isnumeric():
					chan_search = int(chan_search)
				else:
					chan_search = await self.search_cat_name(ctx, chan_search)
			chan.append(str(chan_search))
			await channels.delete(delay=10)
		if len(chan) >= 10:
			await ctx.send(
			    "Erreur ! Vous ne pouvez pas mettre plus de 9 catégories !",
			    delete_after=30)
			return
		namelist = []
		guild = ctx.message.guild
		for i in range(0, len(chan)):
			number = int(chan[i])
			cat = get(guild.categories, id=number)
			if cat == "None":
				ctx.send("Erreur : Cette catégorie n'existe pas !",
				         delete_after=30)
				return
			phrase = f"{emoji[i]} : {cat}"
			namelist.append(phrase)
		msg = "\n".join(namelist)
		parameters = await ctx.send(
		    f"Votre channel sera donc créé dans une des catégories suivantes :\n {msg} \n\n Le choix final de la catégories se fait lors des réactions. "
		)
		parameters_save = parameters.content
		await parameters.delete()
		question = await ctx.send(f"Quel est le titre de l'embed ?")
		titre = await self.bot.wait_for("message", timeout=300, check=checkRep)
		if titre.content == "stop":
			await ctx.send("Annulation !", delete_after=30)
			await question.delete()
			await titre.delete()
			return
		else:
			await question.delete()
			await titre.add_reaction("✅")
			await titre.delete(delay=30)
		question = await ctx.send(f"Quelle couleur voulez vous utiliser ?")
		color = await self.bot.wait_for("message", timeout=300, check=checkRep)
		col = color.content
		if (col.find("#") == -1) and (col != "stop") and (col != "0"):
			await ctx.send(f"Erreur ! Vous avez oublié le # !",
			               delete_after=30)
			await color.delete()
			await question.delete()
			return
		elif col == "stop":
			await ctx.send("Annulation !", delete_after=10)
			await color.delete()
			await question.delete()
			return
		elif col == "0":
			col = "0xabb1b4"
			col = int(col, 16)
			await question.delete()
			await color.add_reaction("✅")
			await color.delete(delay=30)
		else:
			await question.delete()
			col = col.replace("#", "0x")
			col = int(col, 16)
			await color.add_reaction("✅")
			await color.delete(delay=30)
		question = await ctx.send("Voulez-vous utiliser une image ?")
		await question.add_reaction("✅")
		await question.add_reaction("❌")
		reaction, user = await self.bot.wait_for("reaction_add",
		                                         timeout=300,
		                                         check=checkValid)
		if reaction.emoji == "✅":
			await question.delete()
			question = await ctx.send(
			    "Merci d'envoyer l'image. \n**⚡ ATTENTION : LE MESSAGE EN REPONSE EST SUPPRIMÉ VOUS DEVEZ DONC UTILISER UN LIEN PERMANENT (hébergement sur un autre channel/serveur, imgur, lien google...)**"
			)
			img = await self.bot.wait_for("message",
			                              timeout=300,
			                              check=checkRep)
			img_content = img.content
			if img_content == "stop":
				await ctx.send("Annulation !", delete_after=10)
				await question.delete()
				await img.delete()
				return
			else:
				await question.delete()
				await img.delete()
		else:
			await question.delete()
			img_content = "none"
		embed = discord.Embed(title=titre.content, description=msg, color=col)
		if img_content != "none":
			embed.set_image(url=img_content)
		question = await ctx.send(
		    f"Les catégories dans lequel vous pourrez créer des canaux seront : {parameters_save} \n Validez-vous ses paramètres ?"
		)
		await question.add_reaction("✅")
		await question.add_reaction("❌")
		reaction, user = await self.bot.wait_for("reaction_add",
		                                         timeout=300,
		                                         check=checkValid)
		if reaction.emoji == "✅":
			react = await ctx.send(embed=embed)
			for i in range(0, len(chan)):
				await react.add_reaction(emoji[i])
			category_list_str = ",".join(chan)
			sql = "INSERT INTO CATEGORY (idM, channelM, category_list, idS) VALUES (?,?,?,?)"
			id_serveur = ctx.message.guild.id
			id_message = react.id
			chanM = ctx.channel.id
			var = (id_message, chanM, category_list_str, id_serveur)
			c.execute(sql, var)
			db.commit()
			c.close()
			db.close()
		else:
			await ctx.send("Annulation !", delete_after=10)
			c.close()
			db.close()
			return
		await question.delete()
		await ctx.delete()

	@commands.has_permissions(administrator=True)
	@commands.command(aliases=["count", "edit_count"])
	async def recount(self, ctx, arg, ticket_id):
		db = sqlite3.connect("owlly.db", timeout=3000)
		c = db.cursor()
		search_db = "SELECT num FROM TICKET WHERE idM=?"
		sql = "UPDATE TICKET SET num = ? WHERE idM=?"
		search_regex_arg = re.search(
		    '(?:(?P<channel_id>[0-9]{15,21})-)?(?P<message_id>[0-9]{15,21})$',
		    str(arg))
		if search_regex_arg is None:
			search_regex_arg = re.search(
			    '(?:(?P<channel_id>[0-9]{15,21})-)?(?P<message_id>[0-9]{15,21})$',
			    str(ticket_id))
			if search_regex_arg is None:
				await ctx.send(
				    "Aucun de vos arguments ne correspond à l'ID du message du créateur de ticket...",
				    delete_after=30)
				await ctx.delete()
				c.close()
				db.close()
				return
			else:
				arg = int(arg)
				ticket_id = int(ticket_id)
		else:
			silent = int(ticket_id)
			ticket_id = int(arg)
			arg = silent
		c.execute(search_db, (ticket_id, ))
		search = c.fetchone()
		if search is None:
			await ctx.send("Aucun ne ticket ne possède ce numéro.")
			await ctx.delete()
			c.close()
			db.close()
			return
		else:
			var = (arg, (ticket_id))
			c.execute(sql, var)
			db.commit()
			c.close()
			db.close()
			await ctx.send(f"Le compte a été fixé à : {arg}")
			await ctx.delete()


def setup(bot):
	bot.add_cog(config(bot))
