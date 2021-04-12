import discord
from discord.ext import commands
from discord.utils import get
import unicodedata
import os
import sqlite3
from discord.ext.commands import TextChannelConverter as tcc
from discord.ext.commands import CommandError
import sqlite3
import os.path
import json
import asyncio
import unidecode
import re

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True)

class Personnage(object):
	def __init__(self, champ):
		self.champ=champ
	def __str__(self):
		return str(self.champ)

class memberUtils(commands.Cog, name="Membre", description="Des commandes gérants les membres."):

	def __init__(self, bot):
		self.bot = bot
	
	async def search_chan(self, ctx, chan: str):
		chan=str(chan)
		try:
			chan = await commands.TextChannelConverter().convert(ctx, chan)
			return chan
		except CommandError:
			chan = "Error"
			return chan

	async def forme(self, ctx, member: discord.Member, chartype, idS):
		f = open(f"fiche/{chartype}_{member.name}_{idS}.txt", "r", encoding="utf-8")
		data = f.readlines()
		f.close()
		msg = "error"
		if (len(data) > 0):
			data = "".join(data)
			p = re.compile('(?<!\\\\)\'')
			data=p.sub('\"', data)
			perso = json.loads(data)
			db = sqlite3.connect("owlly.db", timeout=3000)
			c = db.cursor()
			sql="SELECT champ_physique, champ_general FROM SERVEUR WHERE idS=?"
			c.execute(sql, (idS,))
			champ=c.fetchone()
			general=champ[1].split(",")
			physique=champ[0].split(",")
			general_info={}
			physique_info={}
			for k, v in perso.items():
				for gen in general:
					for phys in physique:
						if k == gen:
							general_info.update({k:v})
						elif k == phys:
							physique_info.update({k:v})
			general_msg = "─────༺ Présentation ༻─────\n"
			physique_msg = "──────༺Physique༻──────\n "
			img=""
			for k, v in general_info.items():
				if v.endswith("png") or v.endswith("jpg") or v.endswith("gif") or v.endswith("jpeg"):
					img=v
				else:
					general_msg = general_msg+f"**__{k}__** : {v}\n"
			for l, m in physique_info.items():
				if m.endswith("png") or m.endswith("jpg") or m.endswith("gif") or m.endswith("jpeg"):
					img=m
				else:
					physique_msg=physique_msg+f"**__{l}__** : {m}\n"
			msg = general_msg+"\n\n"+physique_msg+"\n\n"+f"⋆⋅⋅⋅⊱∘──────∘⊰⋅⋅⋅⋆\n *Auteur* : {member.mention}"
		return msg, img

	async def validation(self, ctx, msg, img, chartype, member: discord.Member):
		idS=ctx.guild.id
		if msg != "error":
			db = sqlite3.connect("owlly.db", timeout=3000)
			c = db.cursor()
			SQL = "SELECT fiche_pj, fiche_pnj, fiche_validation FROM SERVEUR WHERE idS=?"
			c.execute(SQL, (ctx.guild.id,))
			channel = c.fetchone()
			def checkValid(reaction, user):
				return ctx.message.author == user and q.id == reaction.message.id and (str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌")
			if (channel[0] is not None) and (channel[1] is not None) and (channel[0] != 0) and (channel[1] != 0):
				chan = await self.search_chan(ctx, channel[2])
				q = await chan.send(f"Il y a une présentation à valider ! Son contenu est :\n {msg}\n\n Validez-vous la fiche ? ")
				await q.add_reaction("✅")
				await q.add_reaction("❌")
				reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
				if reaction.emoji == "✅":
					if chartype.lower() == "pnj":
						if channel[1] != 0:
							chan_send = await self.search_chan(ctx, channel[1])
						else:
							chan_send = await self.search_chan(ctx, channel[0])
					else:
						chan_send = await self.search_chan(ctx, channel[0])
					if img!="":
						embed=discord.Embed()
						embed.set_image(url=img)
						await chan_send.send(content=msg, embed=embed)
					else:
						await chan_send.send(msg)
					os.remove(f"fiche/{chartype}_{member.name}_{idS}.txt")
				else:
					await member.send("Il y a un soucis avec votre fiche ! Rapprochez-vous des modérateurs pour voir le soucis.")
			else:
				await member.send("Huh, il y a eu un soucis avec l'envoie. Il semblerait que les channels ne soient pas configurés ! Rapproche toi du staff pour le prévenir. \n Note : Ce genre de chose n'est pas sensé arrivé, donc contacte aussi @Mara#3000 et fait un rapport de bug. ")

	async def start_presentation(self, ctx, member: discord.Member, chartype):
		db = sqlite3.connect("owlly.db", timeout=3000)
		c = db.cursor()
		idS=ctx.guild.id
		sql="SELECT champ_general, champ_physique FROM SERVEUR WHERE idS=?"
		c.execute(sql, (idS,))
		champ_map=c.fetchone()
		general=champ_map[0]
		physique=champ_map[1]
		if general is None or physique is None:
			return "ERROR"
		general=general.split(",")
		physique=physique.split(",")
		champ=general+physique
		template={i:str(Personnage(i)) for i in champ}
		last=list(template)[-1]
		def checkRep(message):
			return message.author == member and isinstance(message.channel, discord.DMChannel)
		emoji = ["✅", "❌"]
		def checkValid(reaction, user):
			return ctx.message.author == user and q.id == reaction.message.id and str(reaction.emoji) in emoji
		if not os.path.isfile(f'fiche/{chartype}_{member.name}_{idS}.txt'):
			perso = {}
		else:
			f = open(f"fiche/{chartype}_{member.name}_{idS}.txt", "r", encoding="utf-8")
			data = f.readlines()
			f.close()
			if (len(data) > 0):
				data = "".join(data)
				p = re.compile('(?<!\\\\)\'')
				data = p.sub('\"', data)
				perso = json.loads(data)
			else:
				perso = {}
		f = open(f"fiche/{chartype}_{member.name}_{idS}.txt", "w", encoding="utf-8")
		if last not in perso.keys():
			for t in template.keys():
				if t not in perso.keys():
					champ = t.capitalize()
					await member.send(f"{champ} ?\n Si votre perso n'en a pas, merci de mettre `/` ou `NA`.")
					champ = champ.replace("\'", "\\'")
					rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
					try:
						if rep.content.lower() == "stop":
							await member.send(f"Mise en pause. Vous pourrez reprendre plus tard avec la commande `{ctx.prefix}fiche`")
							f.write(str(perso))
							f.close()
							return "NOTdone"
						elif rep.content.lower() == "cancel":
							await member.send("Annulation de la présentation.")
							f.close()
							os.remove(f"fiche/{chartype}_{member.name}_{idS}.txt")
							return "delete"
						else:
							reponse= rep.content 
							reponse=reponse.replace("\'", "\\'")
							perso.update({champ.lower(): rep.content})
					except asyncio.TimeoutError:
						await member.send(f"Timeout ! Enregistrement des modifications. Vous pourrez la reprendre plus tard avec la commande `{ctx.prefix}fiche`")
						f.write(str(perso))
						f.close()
						return "NOTdone"
			f.write(str(perso))
			f.close()
		msg, img = await self.forme(ctx, member, chartype, idS)
		if img != "":
			msg = msg+"\n\n"+img
		if msg != "error":
			q=await member.send(f"Votre présentation est donc : \n {msg}.\n Validez-vous ses paramètres ?")
			await q.add_reaction("✅")
			await q.add_reaction("❌")
			reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
			if reaction.emoji == "✅":
				await q.edit(content=f"Fin de la présentation ! Merci de votre coopération.")
				return "done"
			else:
				await q.edit(content=f"Vous êtes insatisfait. La commande `{ctx.prefix}fiche` vous permettra d'édite ou supprimer votre fiche.")
				return "NOTdone"
		return "ERROR"

	@commands.Cog.listener()
	async def on_member_join(self, Member):
		name=Member.name
		normal_name = unicodedata.normalize('NFKD', name)
		await Member.edit(nick=normal_name)
  
	@commands.command(usage="@mention (pnj?) *role", brief="Donne divers rôles.", help="Permet de donner des rôles à un membre, ainsi que les rôles qui ont été inscrits dans la base. Si les rôles n'existent pas, le bot les crée avant.")
	@commands.has_permissions(administrator=True)
	async def member(self, ctx, user: discord.Member, chartype="pj", *role: str):
		addRole = []
		infoNew = []
		db = sqlite3.connect("owlly.db", timeout=3000)
		c = db.cursor()
		sql = "SELECT roliste FROM SERVEUR WHERE idS=?"
		c.execute(sql, (ctx.guild.id,))
		defaut = c.fetchone()
		rolelist = []
		defaut = ','.join(defaut)
		defaut = defaut.split(',')
		for i in defaut:
			i = get(ctx.guild.roles, id=int(i))
			await user.add_roles(i)
		for i in role:
			i = i.replace("<", "")
			i = i.replace(">", "")
			i = i.replace("@", "")
			i = i.replace("&", "")
			if i.isnumeric():
				i = int(i)
				roleCheck = get(ctx.guild.roles, id=i)
			else:
				roleCheck = get(ctx.guild.roles, name=i)
			if roleCheck is None:
				NewRole = await ctx.guild.create_role(name=i, mentionable=True)
				await NewRole.edit(position=14)
				addRole.append(NewRole)
				infoNew.append(NewRole.name)
			else:
				if str(i).isnumeric():
					i = get(ctx.guild.roles, id=i)
				else:
					i = get(ctx.guild.roles, name=i)
				addRole.append(i)
		roleInfo = []
		for plus in addRole:
			await user.add_roles(plus)
			roleInfo.append(plus.name)
		roleInfo = ", ".join(roleInfo)
		if (len(infoNew)) > 0:
			infoNew = "\n ◽".join(infoNew)
			roleInfo = roleInfo + " " + infoNew
		await ctx.send(f"{user.Mention} est devenu un membre du serveur ! Il·Elle a donc reçu les rôles : {roleInfo}. ", delete_after=60)
		await ctx.message.delete()
		pres = await self.start_presentation(ctx, user, chartype)
		if pres == "done":
			fiche, img = await self.forme(user, chartype, idS=ctx.guild.id)
			await self.validation(ctx, fiche, img, chartype, user)

	@commands.command(usage="@mention (pnj?)", brief="Lance la création d'une fiche", help="Permet à un joueur ayant sa fiche valider de faire sa présentation.", aliases=["add_pres"])
	@commands.has_permissions(administrator=True)
	async def add_presentation(self, ctx, member: discord.Member, chartype="pj"):
		pres=await self.start_presentation(ctx, member, chartype)
		if pres == "done":
			fiche, img=await self.forme(ctx, member, chartype, idS=ctx.guild.id)
			await self.validation(ctx, fiche, img, chartype, member)

	@commands.command(usage="@mention (pnj?) -(delete|edit champs)", brief="Permet d'éditer une présentation non validé ou en cours.", help="Permet à un administrateur de modifier ou supprimer une fiche en cours de validation, ou en cours d'écriture.")
	@commands.has_permissions(administrator=True)
	async def admin_edit(self, ctx, member:discord.Member):
		idS=ctx.guild.id
		emoji = ["1️⃣", "2️⃣", "3️⃣", "❌"]
		def checkRep(message): 
			return message.author == member and ctx.message.channel == message.channel
		def checkValid(reaction, user):
			return ctx.message.author == user and q.id == reaction.message.id and str(reaction.emoji) in emoji
		if os.path.isfile(f"fiche/pj_{member.name}_{idS}.txt") and os.path.isfile(f"fiche/pnj_{member.name}_{idS}.txt"):
			q = await ctx.send("Voulez-vous modifier la fiche du PNJ ou PJ ?\n 1️⃣ : PJ\n 2️⃣ : PNJ")
			await q.add_reaction("1️⃣")
			await q.add_reaction("2️⃣")
			await q.add_reaction("❌")
			reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
			if reaction.emoji == "1️⃣":
				chartype = "pj"
			elif reaction.emoji == "2️⃣":
				chartype = "pnj"
			else:
				await q.delete()
				await ctx.send("Annulation", delete_after=30)
				return
		elif os.path.isfile(f"fiche/pnj_{member.name}_{idS}.txt"):
			chartype = "pnj"
		elif os.path.isfile(f"fiche/pj_{member.name}_{idS}.txt"):
			chartype = "pj"
		else:
			chartype = "ERROR"
		if chartype != "ERROR":
			menu=discord.Embed(title=f"MENU {chartype} EDITION ADMIN", description="1️⃣ - EDITION\n 2️⃣ - SUPPRESSION \n 3️⃣ - VOIR LA FICHE")
			q=await ctx.send(embed=menu)
			for i in emoji:
				q.add_reaction(i)
			reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
			if reaction.user=="1️⃣":
				await q.delete()
				f = open(f"fiche/{chartype}_{member.name}_{idS}.txt", "r", encoding="utf-8")
				data = f.readlines()
				f.close()
				if (len(data) > 0):
					data = "".join(data)
					p = re.compile('(?<!\\\\)\'')
					data = p.sub('\"', data)
					perso = json.loads(data)
					msg, img=await self.forme(ctx, member, chartype, idS)
					q = await ctx.send(f"Actuellement, la fiche ressemble à ça : {msg} \n Quel champ voulez-vous éditer ?")
					rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
					if rep.content.lower() == "stop":
						await q.delete()
						await rep.delete()
						await ctx.send("Annulation", delete_after=30)
						return
					value = rep.content
					await rep.delete()
					found="not"
					for k in perso.keys():
						if unidecode.unidecode(k.lower()) == unidecode.unidecode(value.lower()):
							q=await ctx.send(f"Par quoi voulez-vous modifier {value.capitalize()} ? \n Actuellement, sa valeur est {perso.get(k)}")
							rep = self.bot.wait_for("message", timeout=300, check=checkRep)
							if rep.content.lower()=="stop":
								await ctx.send("Annulation", delete_after=30)
								await q.delete()
								await rep.delete()
								return
							perso[k]=rep.content
							f = open(f"fiche/{chartype}_{member.name}_{idS}.txt","w", encoding="utf-8")
							f.write(str(perso))
							f.close()
							q=await q.edit(content=f"{value.capitalize()} a bien été modifié !")
							found="yes"
							break
					if found =="not":
						await ctx.send("Erreur ! {value} n'a pas été trouvé...")
						await q.delete()
						return
			elif reaction.emoji == "2️⃣":
				await q.delete()
				os.remove("fiche/{chartype}_{member.name}_{idS}.txt")
				await ctx.send(f"La présentation de {member.name} a été supprimé.")
			elif reaction.emoji == "3️⃣":
				msg, img=await self.forme(ctx, member, chartype, idS)
				await ctx.send(f"{msg} \n {img}")
			else:
				await q.delete()
				await ctx.send(f"Annulation", delete_after=30)
				return
		else:
			await ctx.send("{member.name} n'a pas de présentation en cours...")
			return

	@commands.command(aliases=["pres"], brief="Commandes pour modifier une présentation en cours.", help="Le champ PNJ est à indiquer pour les fiches lorsque celles-ci sont pour les PNJ. Autrement, par défaut, les fiches PJ sont sélectionnées. \n Cette commande permet la reprise, modification ou suppression d'une présentation.")
	async def fiche(self, ctx):
		member = ctx.message.author
		idS = ctx.guild.id
		emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "❌"]
		def checkValid(reaction, user):
			return ctx.message.author == user and q.id == reaction.message.id and str(reaction.emoji) in emoji
		if os.path.isfile(f"fiche/pj_{member.name}_{idS}.txt") and os.path.isfile(f"fiche/pnj_{member.name}_{idS}.txt"):
			q=await ctx.send("Voulez-vous modifier la fiche de votre PNJ ou PJ ?\n 1️⃣ : PJ\n 2️⃣ : PNJ")
			await q.add_reaction("1️⃣")
			await q.add_reaction("2️⃣")
			await q.add_reaction("❌")
			reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
			if reaction.emoji == "1️⃣":
				chartype="pj"
			elif reaction.emoji == "2️⃣":
				chartype="pnj"
			else:
				await q.delete()
				await ctx.send("Annulation", delete_after=30)
				return
		elif os.path.isfile(f"fiche/pnj_{member.name}_{idS}.txt"):
			chartype="pnj"
		elif os.path.isfile(f"fiche/pj_{member.name}_{idS}.txt"):
			chartype="pj"
		else:
			chartype="ERROR"
		def checkRep(message):
			return message.author == member and isinstance(message.channel, discord.DMChannel)
		def checkRepChan(message):
			return message.author == member and ctx.message.channel == message.channel
		db = sqlite3.connect("owlly.db", timeout=3000)
		c = db.cursor()
		SQL = "SELECT fiche_pj, fiche_pnj, fiche_validation FROM SERVEUR WHERE idS=?"
		c.execute(SQL, (ctx.guild.id,))
		channel = c.fetchone()
		if (channel[0] is not None) and (channel[1] is not None) and (channel[0] != 0) and (channel[1] != 0):
			if chartype != "ERROR":
				menu=discord.Embed(title=f"Menu ({chartype})", description="1️⃣ - Edition\n 2️⃣ - Suppression\n 3️⃣ - Reprise \n 4️⃣ - Voir la fiche en cours")
				q=await ctx.send(embed=menu)
				for i in emoji:
					await q.add_reaction(i)
				reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
				if reaction.emoji=="1️⃣":
					await q.delete()
					await ctx.send("Regardez vos DM ! 📨")
					f = open(f"fiche/{chartype}_{member.name}_{idS}.txt", "r", encoding="utf-8")
					data = f.readlines()
					f.close()
					if (len(data) > 0):
						data = "".join(data)
						p = re.compile('(?<!\\\\)\'')
						data = p.sub('\"', data)
						perso = json.loads(data)
						msg, img= await self.forme(ctx, member, chartype, idS)
						await member.send(f"Actuellement, votre fiche ressemble à ceci :\n {msg}")
						q=await member.send("Quel est le champ que vous voulez modifier ?")
						rep=await self.bot.wait_for("message", timeout=300, check=checkRep)
						print(rep.content)
						if rep.content.lower() == "stop":
							await q.delete()
							await rep.delete()
							await ctx.send("Annulation", delete_after=30)
							return
						value=rep.content
						found="not"
						for k in perso.keys():
							if unidecode.unidecode(k.lower()) == unidecode.unidecode(value.lower()):
								q = await member.send(f"Par quoi voulez-vous modifier {value.capitalize()} ?\n Actuellement, elle a pour valeur {perso.get(k)}.")
								rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
								if rep.content.lower() == "stop":
									await q.delete()
									await member.send("Annulation")
									await rep.delete()
									return
								perso[k] = rep.content
								f = open(f"fiche/{chartype}_{member.name}_{idS}.txt", "w", encoding="utf-8")
								f.write(str(perso))
								f.close()
								q = await q.edit(content=f"{value.capitalize()} a bien été modifié !")
								found="yes"
								break
						if found == "not":
							await ctx.send(f"{value} n'a pas été trouvé dans votre fiche...")
							return	
					else:
						await ctx.send("Erreur ! Votre présentation n'existe pas.")
						await q.delete()
						return
					f.close()
				elif reaction.emoji == "2️⃣":
					os.remove(f"fiche/{chartype}_{member.name}_{idS}.txt")
					await ctx.send("Votre présentation a été supprimé.")
				elif reaction.emoji == "3️⃣":
					await ctx.send("Regardez vos DM 📨 !")
					step = await self.start_presentation(ctx, member, chartype)
					if step == "done":
						msg, img = self.forme(ctx, member, chartype, idS)
						await self.validation(ctx, msg, img, chartype, member)
				elif reaction.emoji == "4️⃣":
					msg, img = await self.forme(ctx, member, chartype, idS)
					await member.send(f"{msg} \n {img}")
			else:
				await ctx.send("Vous n'avez pas de présentation en cours !")
		else:
			await ctx.send("Impossible de faire une présentation : Les channels ne sont pas configuré !")


def setup(bot):
	bot.add_cog(memberUtils(bot))

