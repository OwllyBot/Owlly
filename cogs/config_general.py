import discord
from discord.ext import commands, tasks
import sqlite3
import re
from typing import Optional
from discord.ext.commands import CommandError
import unidecode

class CogAdmins(commands.Cog, name="Configuration générale", description="Permet d'enregistrer quelques paramètres pour le bot."):
	def __init__(self, bot):
		self.bot = bot

	async def search_chan(self, ctx, chan):
		try:
			chan = await commands.TextChannelConverter().convert(ctx, chan)
			return chan
		except CommandError:
			chan = "Error"
			return chan 

	@commands.command(name="set_prefix", help="Permet de changer le prefix du bot.", brief="Changement du prefix.")
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

	@commands.command(aliases=['lexique_config'], help="Permet de configurer le channel dans lequel la commande `search` va faire ses recherches.", brief="Configuration de la recherche de message dans un channel.")
	@commands.has_permissions(administrator=True)
	async def notes_config(self, ctx, chan: discord.TextChannel):
		server = ctx.guild.id
		db = sqlite3.connect("owlly.db", timeout=3000)
		c = db.cursor()
		sql = "UPDATE SERVEUR SET notes=? WHERE idS=?"
		chanID = chan.id
		var = (chanID, server)
		c.execute(sql, var)
		db.commit()
		c.close()
		db.close()
		await ctx.send(f"Le channels des notes est donc {chan}", delete_after=30)
		await ctx.message.delete()

	@commands.has_permissions(administrator=True)
	@commands.command(name="Roliste", help="Assignation des rôles assignés par défaut par la commande `member`.", brief="Enregistrement de rôles pour la commande member.", usage="@mention/ID des rôles à enregistrer", aliases=['role_config', 'roliste_config', 'assign'])
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

	@commands.has_permissions(administrator=True)
	@commands.command(aliases=["fiche_chan"], help="Permet de configurer le channel dans lequel sera envoyé les présentations des personnages.", brief="Insertion d'un channel pour envoyer les présentations validées.", usage="channel")
	async def chan_fiche(self, ctx):
		def checkRep(message):
			return message.author == ctx.message.author and ctx.message.channel == message.channel
		def checkValid(reaction, user):
			return ctx.message.author == user and q.id == reaction.message.id and (str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌")
		cl=ctx.guild.id
		db = sqlite3.connect("owlly.db", timeout=3000)
		c = db.cursor()
		await ctx.message.delete()
		q= await ctx.send("Dans quel channel voulez-vous que soit envoyé les fiches à valider ?")
		rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
		if rep.content.lower() == "stop":
			await q.delete()
			await rep.delete()
			await ctx.send("Annulation", delete_after=30)
			return
		fiche_validation = await self.search_chan(ctx, rep.content)
		if fiche_validation == "Error":
			await ctx.send("Erreur dans le channel.", delete_after=30)
			await q.delete()
			await rep.delete()
			return
		await rep.delete()
		await q.edit(content="Dans quel channel voulez-vous envoyer la présentation des PJ validés ?")
		rep=await self.bot.wait_for("message", timeout=300, check=checkRep)
		if rep.content.lower()=="stop":
			await q.delete()
			await rep.delete()
			await ctx.send("Annulation", delete_after=30)
			return
		fiche_pj = await self.search_chan(ctx, rep.content)
		if fiche_pj == "Error":
			await ctx.send("Erreur dans le channel.", delete_after=30)
			await q.delete()
			await rep.delete()
			return
		await rep.delete()
		await q.edit(content="Voulez-vous configurer le channel des PNJ ?")
		await q.add_reaction("✅")
		await q.add_reaction("❌")
		reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
		if reaction.emoji == "✅":
			await q.clear_reactions()
			await q.edit(content="Dans quel channel voulez-vous que soit envoyé les fiches des PNJ ?")
			rep=await self.bot.wait_for("message", timeout=300, check=checkRep)
			fiche_pnj = await self.search_chan(ctx, rep.content)
			fiche_pnj=fiche_pnj.id
			if fiche_pnj=="Error":
				await ctx.send("Erreur dans le channel.", delete_after=30)
				await q.delete()
				await rep.delete()
				return
		else:
			fiche_pnj=0
		await q.edit(content="Validation des modification....")
		sql = "UPDATE SERVEUR SET fiche_validation=?, fiche_pj = ?, fiche_pnj=? WHERE idS=?"
		var=(fiche_validation.id, fiche_pj.id,fiche_pnj, cl)
		c.execute(sql, var)
		db.commit()
		c.close()
		db.close()
		await q.edit(content="Modification validée !")

	@commands.command(brief="Permet de choisir les champs de la présentation des personnages.", help="Cette commande permet de choisir les champs de présentation générale et du physique, de les éditer, supprimer mais aussi en ajouter.")
	@commands.has_permissions(administrator=True)
	async def admin_fiche (self, ctx):
		emoji=["1️⃣","2️⃣","3️⃣", "4️⃣", "❌", "✅"]
		def checkValid(reaction, user):
			return ctx.message.author == user and q.id == reaction.message.id and str(reaction.emoji) in emoji
		def checkRep(message):
			return message.author == ctx.message.author and ctx.message.channel == message.channel
		cl = ctx.guild.id
		db = sqlite3.connect("owlly.db", timeout=3000)
		c = db.cursor()
		await ctx.message.delete()
		menu = discord.Embed(title="Menu de gestion des fiches",
		                     description="1️⃣ - Création \n 2️⃣ - Suppression \n 3️⃣ - Edition \n 4️⃣ - Ajout")
		menu.set_footer(text="❌ pour annuler.")
		q=await ctx.send(embed=menu)
		for i in emoji:
			if i != "✅":
				await q.add_reaction(i)
		reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
		if reaction.emoji=="1️⃣":
			await q.delete()
			sql="SELECT fiche_pj, fiche_validation, fiche_pnj FROM SERVEUR WHERE idS=?"
			c.execute(sql, (cl,))
			channels=c.fetchone()
			if channels[0] is None:
				await self.chan_fiche(ctx)
			q=await ctx.send("Merci de rentrer les champs que vous souhaitez pour la partie présentation **générale**.\n `cancel` pour annuler et `stop` pour valider.")
			general=[]
			while True:
				general_rep=await self.bot.wait_for("message", timeout=300, check=checkRep)
				general_champ=general_rep.content 
				if general_champ.lower()=='stop':
					await ctx.send("Validation en cours !", delete_after=5)
					await general_rep.delete()
					break
				elif general_champ.lower()=="cancel":
					await general_rep.delete()
					await ctx.send("Annulation !", delete_after=30)
					await q.delete()
					return
				else:
					await general_rep.add_reaction("✅")
					general.append(general_champ.capitalize())
				await general_rep.delete(delay=10)
			general=",".join(general)
			await q.delete()
			q=await ctx.send("Maintenant, rentrer les champs pour la description physique.\n `stop` pour valider, `cancel` pour annuler.")
			physique=[]
			while True:
				physique_rep=await self.bot.wait_for("message", timeout=300, check=checkRep)
				physique_champ=physique_rep.content
				if physique_champ.lower() == "stop":
					await ctx.send("Validation en cours !", delete_after=5)
					await physique_rep.delete()
					break
				elif physique_champ.lower()=="cancel":
					await physique_rep.delete()
					await ctx.send("Annulation !", delete_after=30)
					await q.delete()
					return
				else:
					await physique_rep.add_reaction("✅")
					physique.append(physique_champ.capitalize())
				await physique_rep.delete(delay=10)
			physique=",".join(physique)
			await q.delete()
			q=await ctx.send(f"Vos champs sont donc :\n __GÉNÉRAL__ :\n {general} \n\n __PHYSIQUE__ : {physique}\n\n Validez-vous ses paramètres ?")
			await q.add_reaction("✅")
			await q.add_reaction("❌")
			reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
			if reaction.emoji == "✅":
				sql="UPDATE SERVEUR SET champ_general = ?, champ_physique = ? WHERE idS=?"
				var=(general, physique, cl)
				c.execute(sql, var)
				db.commit()
				await ctx.send("Enregistré !")
				await q.delete()
				return
			else:
				await q.delete()
				await ctx.send("Annulation", delete_after=30)
				return
		elif reaction.emoji =="2️⃣":
			await q.delete()
			q=await ctx.send("Quel champ voulez-vous supprimer ?")
			rep=await self.bot.wait_for("message", timeout=300, check=checkRep)
			if rep.content.lower() == "stop":
				await q.delete()
				await rep.delete()
				await ctx.send("Annulation", delete_after=30)
				return
			else:
				champ=unidecode.unidecode(rep.content.lower())
			sql="SELECT champ_general, champ_physique FROM SERVEUR WHERE idS=?"
			c.execute(sql, (cl,))
			champs=c.fetchone()
			if champs[0] is not None:
				champ_general=champs[0].split(",")
				champ_physique=champs[1].split(",")
			else:
				await ctx.send("Vous n'avez pas de fiche configurée. Vous devez d'abord en créer une.", delete_after=30)
				await q.delete()
				await rep.delete()
				return
			if champ in [unidecode.unidecode(i.lower()) for i in champ_general]:
				champ_general=list(filter(lambda w: unidecode.unidecode(w.lower()) not in champ, champ_general))
			elif champ in [unidecode.unidecode(i.lower()) for i in champ_physique]:
				champ_physique = list(
					filter(lambda w: unidecode.unidecode(w.lower()) not in champ, champ_physique))
			else:
				await ctx.send("Ce champ n'existe pas !", delete_after=30)
				return
			champ_general=",".join(champ_general)
			champ_physique=",".join(champ_physique)
			sql="UPDATE SERVEUR SET champ_general = ?, champ_physique = ? WHERE idS=?"
			var=(champ_general,champ_physique, cl)
			c.execute(sql, var)
			db.commit()
			await rep.delete()
			await q.delete()
			await ctx.send(f"Le Champ : {champ} a bien été supprimé !")
		elif reaction.emoji == "3️⃣": 
			await q.delete()
			q = await ctx.send("Quel champ voulez-vous éditer ?")
			rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
			if rep.content.lower() == "stop":
				await q.delete()
				await rep.delete()
				await ctx.send("Annulation", delete_after=30)
				return
			else:
				champ = unidecode.unidecode(rep.content.lower())
			sql = "SELECT champ_general, champ_physique FROM SERVEUR WHERE idS=?"
			c.execute(sql, (cl,))
			champs = c.fetchone()
			if champs[0] is not None:
				champ_general = champs[0].split(",")
				champ_physique = champs[1].split(",")
			else:
				await ctx.send("Vous n'avez pas de fiche configurée. Vous devez d'abord en créer une.", delete_after=30)
				return
			if champ in [unidecode.unidecode(i.lower()) for i in champ_general]:
				await rep.delete()
				await q.edit(content=f"Par quoi voulez-vous modifier {champ} ?")
				rep=await self.bot.wait_for("message", timeout=300, check=checkRep)
				save=rep.content
				if rep.content.lower() =="stop":
					await q.delete()
					await rep.delete()
					await ctx.send("Annulation", delete_after=30)
					return
				champ_general=[rep.content.capitalize() if champ == unidecode.unidecode(x.lower()) else x for x in champ_general]
			elif champ in [unidecode.unidecode(i.lower()) for i in champ_physique]:
				if rep.content.lower() == "stop":
					await q.delete()
					await rep.delete()
					await ctx.send("Annulation", delete_after=30)
					return
				champ_physique=[rep.content.capitalize() if champ == unidecode.unidecode(x.lower()) else x for x in champ_physique]
			else:
				await q.delete()
				await rep.delete()
				await ctx.send("Erreur ! Ce champ n'existe pas.", delete_after=30)
				return
			champ_general=",".join(champ_general)
			champ_physique=",".join(champ_physique)
			sql="UPDATE SERVEUR SET champ_general = ?, champ_physique = ? WHERE idS=?"
			var=(champ_general,champ_physique, cl)
			c.execute(sql, var)
			db.commit()
			c.close()
			db.close()
			await q.delete()
			await rep.delete()
			await ctx.send("Le champ : {champ} a bien été édité par {save}.")
			return
		elif reaction.emoji == "4️⃣":
			await q.delete()
			q=await ctx.send("Dans quel partie voulez-vous ajouter votre champ ? \n 1️⃣ : GÉNÉRALE \n 2️⃣: PHYSIQUE")
			await q.add_reaction("1️⃣")
			await q.add_reaction("2️⃣")
			await q.add_reaction("❌")
			reaction, user=await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
			if reaction.emoji == "1️⃣":
				sql="SELECT champ_general FROM SERVEUR WHERE idS=?"
				c.execute(sql, (cl,))
				champ_general = c.fetchone()[0]
				if champ_general is None:
					await ctx.send("Vous n'avez pas de fiche configurée. Vous devez d'abord en créer une.", delete_after=30)
					return
				champ_general=champ_general.split(",")
				await q.delete()
				q=await ctx.send("Quel est le champ à ajouter ?")
				rep=await self.bot.wait_for("message", timeout=300, check=checkRep)
				if rep.content.lower() == "stop":
					await q.delete()
					await rep.delete()
					await ctx.send("Annulation", delete_after=30)
					return
				new=rep.content.capitalize()
				if new not in champ_general:
					champ_general.append(new)
				else:
					await q.delete()
					await rep.delete()
					await ctx.send("Ce champ existe déjà !", delete_after=30)
					return
				champ_general=",".join(champ_general)
				sql="UPDATE SERVEUR SET champ_general = ? WHERE idS=?"
				var=(champ_general, cl)
				c.execute(sql, var)
				db.commit()
				c.close()
				db.close()
				await ctx.send(f"Le champ {new} a bien été ajouté !")
				await q.delete()
				await rep.delete()
				return
			elif reaction.emoji == "2️⃣":
				sql="SELECT champ_physique FROM SERVEUR WHERE idS=?"
				c.execute(sql,(cl,))
				champ_physique=c.fetchone()[0]
				if champ_physique is None:
					await ctx.send("Vous n'avez pas de fiche configurée. Vous devez d'abord en créer une.", delete_after=30)
					return
				champ_physique=champ_physique.split(",")
				await q.delete()
				q = await ctx.send("Quel est le champ à ajouter ?")
				rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
				if rep.content.lower() == "stop":
					await q.delete()
					await rep.delete()
					await ctx.send("Annulation", delete_after=30)
					return
				new = rep.content.capitalize()
				if new not in champ_physique:
					champ_physique.append(new)
				else:
					await q.delete()
					await rep.delete()
					await ctx.send("Ce champ existe déjà !", delete_after=30)
					return
				champ_physique = ",".join(champ_physique)
				sql = "UPDATE SERVEUR SET champ_physique = ? WHERE idS=?"
				var = (champ_physique, cl)
				c.execute(sql, var)
				db.commit()
				c.close()
				db.close()
				await rep.delete()
				await q.delete()
				await ctx.send(f"Le champ {new} a bien été ajouté !")
				return
			else:
				await q.delete()
				await ctx.send("Annulation", delete_after=30)
				c.close()
				db.close()
				return
		else:
			await q.delete()
			await ctx.send("Annulation", delete_after=30)
			c.close()
			db.close()
			return
		c.close()
		db.close()


	@commands.has_permissions(administrator=True)
	@commands.command(aliases=["count", "edit_count"], brief="Permet de changer le compteur des ticket", help="Permet de reset, ou changer manuellement le numéro d'un créateur de ticket.", usage="nombre id_message_createur")
	async def recount(self, ctx, arg, ticket_id):
		await ctx.message.delete()
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


def setup(bot):
  bot.add_cog(CogAdmins(bot))
