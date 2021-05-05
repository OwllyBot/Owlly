import discord
from discord import role
from discord.ext import commands, tasks
import sqlite3
import re
from typing import Optional
from discord.ext.commands import CommandError
from discord.ext.commands.errors import RoleNotFound
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

	async def roliste_init(self, ctx, role, type_db):
		db = sqlite3.connect("owlly.db", timeout=3000)
		c = db.cursor()
		sql = f"UPDATE SERVEUR SET {type_db} = ? WHERE idS = ?"
		role_list=[]
		if (len(role)) > 1:
			for i in role :
				try:
					roles=await commands.RoleConverter().convert(ctx,i)
					role_list.append(str(roles.id))
				except RoleNotFound:
					pass
		else:
			try:
				role_str = await commands.RoleConverter().convert(ctx, role[0])
				role_str=str(role_str.id)
			except RoleNotFound:
				pass
		phrase=[]
		for i in role:
			try:
				roles = await commands.RoleConverter().convert(ctx, i)
				phrase.append(roles.name)
			except RoleNotFound:
				pass
		phrase=", ".join(phrase)
		if (len(phrase)) == "0":
			await ctx.send("Erreur ! Aucun rôle n'a été reconnu.")
			return
		await ctx.send(f"Les rôles {phrase} ont bien été enregistré dans la base de données")
		role_str = ",".join((role_list))
		var = (role_str, ctx.guild.id)
		c.execute(sql, var)
		db.commit()
		c.close()
		db.close()

	@commands.has_permissions(administrator=True)
	@commands.command(help="Permet d'enregistrer / réenregistrer la liste des rôles données par la commandes member, sans passer par le menu de configuration.", brief="Enregistrement de rôles pour la commande member, sans passer par le menu.", usage="@mention/ID des rôles à enregistrer", aliases=['init_role', 'assign_init'])
	async def role_init(self, ctx, *role: discord.Role):
		db = sqlite3.connect("owlly.db", timeout=3000)
		c = db.cursor()
		sql = "UPDATE SERVEUR SET roliste = ? WHERE idS = ?"
		role_list = []
		if (len(role)) > 1:
			for i in role:
				role_list.append(str(i.id))
		else:
		  role_str = str(role[0].id)
		role_str = ",".join((role_list))
		var = (role_str, ctx.guild.id)
		c.execute(sql, var)
		phrase = []
		for i in role:
			phrase.append(i.name)
		phrase = ", ".join(phrase)
		await ctx.send(f"Les rôles {phrase} ont bien été enregistré dans la base de données")
		db.commit()
		c.close()
		db.close()

	@commands.has_permissions(administrator=True)
	@commands.command(help="Permet d'enregistrer / réenregistrer la liste des rôles retirés par la commandes member, sans passer par le menu de configuration.", brief="Enregistrement de rôles pour la commande member, sans passer par le menu.", usage="@mention/ID des rôles à enregistrer", aliases=['init_rm', 'assign_rm'], usage="*role")
	async def init_role_rm(self, ctx, *role: discord.Role):
		db = sqlite3.connect("owlly.db", timeout=3000)
		c = db.cursor()
		sql = "UPDATE SERVEUR SET rolerm = ? WHERE idS = ?"
		role_list = []
		if (len(role)) > 1:
			for i in role:
				role_list.append(str(i.id))
		else:
		  role_str = str(role[0].id)
		role_str = ",".join((role_list))
		var = (role_str, ctx.guild.id)
		c.execute(sql, var)
		phrase = []
		for i in role:
			phrase.append(i.name)
		phrase = ", ".join(phrase)
		await ctx.send(f"Les rôles {phrase} ont bien été enregistré dans la base de données")
		db.commit()
		c.close()
		db.close()
	
	async def inscription_role(self, ctx, type_db):
		db = sqlite3.connect("owlly.db", timeout=3000)
		c = db.cursor()
		if type_db == "rm":
			sql = "SELECT rolerm FROM SERVEUR WHERE idS =?"
			type_db="rolerm"
		else:
			sql = "SELECT roliste FROM SERVEUR WHERE idS=?"
			type_db="roliste"
		c.execute(sql, (ctx.guild.id,))
		role_list = c.fetchone()
		def checkValid(reaction, user):
			return ctx.message.author == user and q.id == reaction.message.id and (str(reaction.emoji) in emoji)
		def checkRep(message):
			return message.author == ctx.message.author and ctx.message.channel == message.channel
		emoji = ["1️⃣", "2️⃣", "3️⃣", "✅", "❌"]
		if role_list is not None:
			role_list = role_list[0].split(",")
			role_phrase = ""
			for i in role_list:
				try:
					role_phrase = str(await commands.RoleConverter().convert(ctx, i))+" / "+role_phrase
				except RoleNotFound:
					pass
			q = await ctx.send(f"Vous avez actuellement des rôles enregistrés : {role_phrase}\n Voulez-vous :\n 1️⃣ - Rajouter un rôle \n 2️⃣ - Supprimer un rôle \n 3️⃣ - Recommencer votre inscription \n ❌ - Annuler. ")
			for i in emoji:
				while i != "✅":
					await q.add_reaction(i)
			reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
			if reaction.emoji == "1️⃣":
				await q.clear_reactions()
				await q.edit(content="Quel est le rôle que vous voulez rajouter ?")
				rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
				if rep.content.lower() == "stop":
					await ctx.send("Annulation")
					await q.delete()
				else:
					try:
						add_role = await commands.RoleConverter().convert(ctx, rep.content.lower())
					except RoleNotFound:
						await ctx.send("Erreur ! Ce rôle n'existe pas.")
						await q.delete()
						await rep.delete()
						return
					if str(add_role.id) not in role_list:
						role_list.append(str(add_role.id))
						print(role_list)
						role_list_str = ",".join(role_list)
						sql = f"UPDATE SERVEUR SET {type_db} = ? WHERE idS = ?"
						var = (role_list_str, ctx.guild.id)
						c.execute(sql, var)
						await q.edit(content="La liste a été mise à jour !")
						await rep.delete()
						db.commit()
						c.close()
						return
					else:
						await ctx.send("Ce rôle est déjà dans la liste !")
						await q.delete()
						await rep.delete()
						return
			elif reaction.emoji == "2️⃣":
				await q.clear_reactions()
				await q.edit(content="Quel est le rôle que vous voulez supprimer ?")
				rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
				if rep.content.lower() == "stop":
					await ctx.send("Annulation")
					await q.delete()
				else:
					try:
						rm_role = await commands.RoleConverter().convert(ctx, rep.content.lower())
					except RoleNotFound:
						await ctx.send("Erreur ! Ce rôle n'existe pas.")
						await q.delete()
						await rep.delete()
						return
					if str(rm_role.id) in role_list:
						role_list.remove(str(rm_role.id))
						role_list_str = ",".join(role_list)
						sql = f"UPDATE SERVEUR SET {type_db} = ? WHERE idS = ?"
						var = (role_list_str, ctx.guild.id)
						c.execute(sql, var)
						await q.edit(content="La liste a été mise à jour !")
						await rep.delete()
						db.commit()
						c.close()
						return
					else:
						await q.delete()
						await ctx.send("Ce rôle n'est pas enregistré.")
						await rep.delete()
						return
			elif reaction.emoji == "3️⃣":
				await q.clear_reactions()
				await q.edit(content="Merci d'envoyer les rôles que vous voulez rajouter.")
				rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
				roliste = rep.content.split(" ")
				await self.roliste_init(ctx, roliste, type_db)
			else:
				await q.delete()
				await ctx.send("Annulation", delete_after=30)
				return

	@commands.has_permissions(administrator=True)
	@commands.command(help="Permet d'inscrire des rôles à retirer lorsqu'un membre est validé.", brief="Enregistrement de rôle pour les faire retirer.", aliases=["rm_role", "role_remove", "remover_member"])
	async def role_rm(self, ctx):
		await self.inscription_role(ctx, "rm")

	@commands.has_permissions(administrator=True)
	@commands.command(help="Assignation des rôles par la commande `member`.", brief="Enregistrement de rôles pour la commande member.", aliases=['role_config', 'roliste_config', 'assign'])
	async def roliste(self, ctx):
		await self.inscription_role(ctx, "roliste")
		

			


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
		sql = "UPDATE FICHE SET fiche_validation=?, fiche_pj = ?, fiche_pnj=? WHERE idS=?"
		var=(fiche_validation.id, fiche_pj.id,fiche_pnj, cl)
		c.execute(sql, var)
		db.commit()
		c.close()
		db.close()
		await q.edit(content="Modification validée !")

	@commands.command(brief="Permet de choisir les champs de la présentation des personnages.", help="Cette commande permet de choisir les champs de présentation générale et du physique, de les éditer, supprimer mais aussi en ajouter.")
	@commands.has_permissions(administrator=True)
	async def admin_fiche (self, ctx):
		emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "👀", "❌", "✅", ]
		def checkValid(reaction, user):
			return ctx.message.author == user and q.id == reaction.message.id and str(reaction.emoji) in emoji
		def checkRep(message):
			return message.author == ctx.message.author and ctx.message.channel == message.channel
		cl = ctx.guild.id
		db = sqlite3.connect("owlly.db", timeout=3000)
		c = db.cursor()
		menu = discord.Embed(title="Menu de gestion des fiches",
		                     description="1️⃣ | Création \n 2️⃣ | Suppression \n 3️⃣ | Edition \n 4️⃣ | Ajout \n 👀 | Affichage")
		menu.set_footer(text="❌ pour annuler.")
		q=await ctx.send(embed=menu)
		for i in emoji:
			if i != "✅":
				await q.add_reaction(i)
		reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
		if reaction.emoji=="1️⃣":
			await q.delete()
			sql="SELECT fiche_pj, fiche_validation, fiche_pnj FROM FICHE WHERE idS=?"
			c.execute(sql, (cl,))
			channels=c.fetchone()
			if channels[0] is None:
				await self.chan_fiche(ctx)
			q=await ctx.send("Merci de rentrer les champs que vous souhaitez pour la partie présentation **générale**.\n `cancel` pour annuler et `stop` pour valider.\n Utiliser le symbole `*` pour marquer l'obligation du champ.")
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
					general_champ=general_champ.replace("\'", "\\'")
					general.append(general_champ.capitalize())
				await general_rep.delete(delay=10)
			general=",".join(general)
			await q.delete()
			q=await ctx.send("Maintenant, rentrer les champs pour la description physique.\n `stop` pour valider, `cancel` pour annuler.\n Utiliser `*` pour marquer les champs obligatoires, `$` si cela doit être un lien, et `&` si cela doit être une image.")
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
					physique_champ=physique_champ.replace("\'", "\\'")
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
				sql="UPDATE FICHE SET champ_general = ?, champ_physique = ? WHERE idS=?"
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
			sql="SELECT champ_general, champ_physique FROM FICHE WHERE idS=?"
			c.execute(sql,(cl,))
			champs = c.fetchone()
			gen_msg="".join(champs[0]).split(",")
			gen_msg=", ".join(gen_msg)
			phys_msg="".join(champs[1]).split(",")
			phys_msg=", ".join(phys_msg)
			msg_full=f"**Général** : \n {gen_msg} \n\n **Physique** : \n {phys_msg}\n"
			q=await ctx.send(f"{msg_full} Quel champ voulez-vous supprimer ?")
			rep=await self.bot.wait_for("message", timeout=300, check=checkRep)
			if rep.content.lower() == "stop":
				await q.delete()
				await rep.delete()
				await ctx.send("Annulation", delete_after=30)
				return
			else:
				champ=unidecode.unidecode(rep.content.lower())
			
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
			sql="UPDATE FICHE SET champ_general = ?, champ_physique = ? WHERE idS=?"
			var=(champ_general,champ_physique, cl)
			c.execute(sql, var)
			db.commit()
			await rep.delete()
			await q.delete()
			await ctx.send(f"Le Champ : {champ} a bien été supprimé !")
		elif reaction.emoji == "3️⃣": 
			save=""
			await q.delete()
			sql = "SELECT champ_general, champ_physique FROM FICHE WHERE idS=?"
			c.execute(sql, (cl,))
			champs = c.fetchone()
			if champs is None:
				await ctx.send("Vous n'avez pas de fiche configurée. Vous devez d'abord en créer une.", delete_after=30)
				return
			gen_msg = "".join(champs[0]).split(",")
			gen_msg = ", ".join(gen_msg)
			phys_msg = "".join(champs[1]).split(",")
			phys_msg = ", ".join(phys_msg)
			msg_full = f"**Général** : \n {gen_msg} \n\n **Physique** : \n {phys_msg}\n"
			q = await ctx.send(f"{msg_full} Quel champ voulez-vous éditer ?")
			rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
			if rep.content.lower() == "stop":
				await q.delete()
				await rep.delete()
				await ctx.send("Annulation", delete_after=30)
				return
			else:
				champ = unidecode.unidecode(rep.content.lower())
			
			champ_general = champs[0].split(",")
			champ_general = [unidecode.unidecode(i.lower()) for i in champ_general]
			champ_physique = champs[1].split(",")
			champ_physique = [unidecode.unidecode(i.lower()) for i in champ_physique]

			if champ in champ_general:
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
			elif champ in champ_physique:
				await q.edit(content=f"Par quoi voulez-vous modifier {champ} ?")
				rep=await self.bot.wait_for("message", timeout=300, check=checkRep)
				save=rep.content
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
			sql="UPDATE FICHE SET champ_general = ?, champ_physique = ? WHERE idS=?"
			var=(champ_general,champ_physique, cl)
			c.execute(sql, var)
			db.commit()
			c.close()
			db.close()
			await q.delete()
			await rep.delete()
			await ctx.send(f"Le champ : {champ} a bien été édité par {save}.")
			return
		elif reaction.emoji == "4️⃣":
			await q.delete()
			sql = "SELECT champ_general, champ_physique FROM FICHE WHERE idS=?"
			c.execute(sql, (cl,))
			champs = c.fetchone()
			gen_msg = "".join(champs[0]).split(",")
			gen_msg = ", ".join(gen_msg)
			phys_msg = "".join(champs[1]).split(",")
			phys_msg = ", ".join(phys_msg)
			msg_full = f"**Général** : \n {gen_msg} \n\n **Physique** : \n {phys_msg}\n"
			q=await ctx.send(f"__**Fiche actuelle**__ :\n {msg_full}\n Dans quelle partie voulez-vous ajouter votre champ ? \n 1️⃣ : GÉNÉRALE \n 2️⃣: PHYSIQUE")
			await q.add_reaction("1️⃣")
			await q.add_reaction("2️⃣")
			await q.add_reaction("❌")
			reaction, user=await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
			if reaction.emoji == "1️⃣":
				sql="SELECT champ_general FROM FICHE WHERE idS=?"
				c.execute(sql, (cl,))
				champ_general = c.fetchone()[0]
				if champ_general is None:
					await ctx.send("Vous n'avez pas de fiche configurée. Vous devez d'abord en créer une.", delete_after=30)
					return
				champ_general=champ_general.split(",")
				await q.delete()
				q=await ctx.send("Quel est le champ à ajouter ?\n Utiliser `*` pour marquer l'obligation.")
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
				sql="UPDATE FICHE SET champ_general = ? WHERE idS=?"
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
				sql="SELECT champ_physique FROM FICHE WHERE idS=?"
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
				sql = "UPDATE FICHE SET champ_physique = ? WHERE idS=?"
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
		elif reaction.emoji=="👀":
			sql = "SELECT champ_general, champ_physique FROM FICHE WHERE idS=?"
			c.execute(sql,(cl,))
			champs = c.fetchone()
			gen_msg="".join(champs[0]).split(",")
			gen_msg=", ".join(gen_msg)
			phys_msg="".join(champs[1]).split(",")
			phys_msg=", ".join(phys_msg)
			msg_full=f"**Général** : \n {gen_msg} \n\n **Physique** : \n {phys_msg}\n"
			await q.delete()
			await ctx.send(f"Fiche actuelle : \n {msg_full}")
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
