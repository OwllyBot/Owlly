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

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True)

class Personnage(object):
	def __init__(self, champ):
		self.champ=champ
	def __str__(self):
		return str(self.champ)

class memberUtils(commands.Cog, name="Membre", description="Des commandes gérants les membres."):

	def __init__(self, bot):
		self.bot = bot
	
	async def search_chan(self, ctx, chan):
		try:
			chan = await commands.TextChannelConverter().convert(ctx, chan)
			return chan
		except CommandError:
			chan = "Error"
			return chan

	async def forme(member: discord.Member, chartype, idS):
		f = open(f"fiche/{chartype}_{member.name}_{idS}.txt", "r", encoding="utf-8")
		data = f.readlines()
		f.close()
		msg = "error"
		if (len(data) > 0):
			data = "".join(data)
			data = data.replace("\'", "\"")
			perso = json.loads(data)
			db = sqlite3.connect("owlly.db", timeout=3000)
			c = db.cursor()
			sql="SELECT champ_physique, champ_general FROM SERVEUR WHERE idS=?"
			c.execute(sql, (idS,))
			champ=c.fetchone()
			general=champ[0].split(",")
			physique=champ[1].split(",")
			general_info={}
			physique_info={}
			for k, v in perso.items():
				for i in general:
					for j in physique:
						if i == k:
							general_info.update({k:v})
						elif i == j:
							physique_info.update({k:v})
			general_msg = "─────༺ Présentation ༻─────\n"
			physique_msg = "──────༺Physique༻──────\n "
			img=""
			for k, v in general_info:
				if v.startswith("http"):
					img=v
				else:
					general_msg = general_msg+f"**__{k}__** : {v}\n"
			for k, v in physique_info:
				if v.startswith("http"):
					img=v
				else:
					physique_msg=physique_msg+f"**__{k}__** : {v}\n"
			msg = general_msg+"\n\n"+physique_msg+"\n\n"+f"⋆⋅⋅⋅⊱∘──────∘⊰⋅⋅⋅⋆\n *Auteur* : {member.mention}"
		return msg, img

	async def validation(self, ctx, msg, img, chartype, member: discord.Member):
		idS=ctx.guild.id
		if msg != "error":
			db = sqlite3.connect("owlly.db", timeout=3000)
			c = db.cursor()
			SQL = "SELECT fiche_pj, fiche_pnj, fiche_validation FROM SERVEUR WHERE idS=?"
			c.execute(SQL, (ctx.guild.id))
			channel = c.fetchone()
			def checkValid(reaction, user):
				return ctx.message.author == user and q.id == reaction.message.id and (str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌")
			if (channel[0] is not None) and (channel[1] is not None) and (channel[0] != 0) and (channel[1] != 0):
				chan = await self.search_chan(ctx, channel[2])
				q = await chan.send(f"Il y a une présentation à valider ! Son contenu est :\n {msg}\n\n Validez-vous la fiche ? ")
				q.add_reaction("✅")
				q.add_reaction("❌")
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
		physique=general.split(",")
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
				data = data.replace("\'", "\"")
				perso = json.loads(data)
			else:
				perso = {}
		f = open(f"fiche/{chartype}_{member.name}_{idS}.txt", "w", encoding="utf-8")
		while last not in perso.keys():
			for t in template.keys():
				if t not in perso.keys():
					champ = t.capitalize()
					q = await member.send(f"{champ} ?\n Si votre perso n'en a pas, merci de mettre `/` ou `NA`.")
					rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
					try:
						if rep.content.lower() == "stop":
							await member.send("Mise en pause. Vous pourrez reprendre plus tard avec la commande `fiche -reprise`")
							f.write(str(perso))
							f.close()
							return "NOTdone"
						elif rep.content.lower() == "cancel":
							await member.send("Annulation de la présentation.")
							f.close()
							os.remove(f"fiche/{chartype}_{member.name}_{idS}.txt")
							await q.delete()
							await rep.delete()
							return "delete"
						else:
							perso.update({t: rep.content})
					except asyncio.TimeoutError:
						await member.send("Timeout ! Enregistrement des modifications.")
						f.write(str(perso))
						f.close()
						return "NOTdone"
		f.write(str(perso))
		f.close()
		msg, img = await self.forme(member, chartype, idS)
		if img != "":
			msg = msg+"\n\n"+img
		if msg != "error":
			await q.edit(content="Votre présentation est donc : \n {msg},. Validez-vous ses paramètres ?")
			await q.add_reaction("✅")
			await q.add_reaction("❌")
			reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
			if reaction.emoji == "✅":
				await q.edit(content="Fin de la présentation ! Merci de votre coopération.")
				await q.clear_reactions()
				return "done"
			else:
				await q.clear_reactions()
				await q.edit(content="Vous êtes insatisfait. Si vous souhaitez annuler et supprimer votre présentation, faites `{ctx.prefix}presentation -delete` sur le serveur. \n Si vous souhaitez éditer un champ, faite `{ctx.prefix}presentation -edition [champ à éditer]")
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

	@commands.command(usage="@mention", brief="Lance la création d'une fiche", help="Permet à un joueur ayant sa fiche valider de faire sa présentation.", aliases=["add_pres"])
	@commands.has_permissions(administrator=True)
	async def add_presentation(self, ctx, member: discord.Member, chartype="pj"):
		pres=await self.start_presentation(ctx, member, chartype)
		if pres == "done":
			fiche, img=await self.forme(member, chartype, idS=ctx.guild.id)
			await self.validation(ctx, fiche, img, chartype, member)

	@commands.command(usage="@mention (pnj?) -(delete|edit champs)", brief="Permet d'éditer une présentation non validé ou en cours.", help="Permet à un administrateur de modifier ou supprimer une fiche en cours de validation, ou en cours d'écriture.")
	@commands.has_permissions(administrator=True):
	async def admin_edit(self, ctx, member:discord.Member, chartype="pj", arg="0", value="0"):
		idS=ctx.guild.id
		def checkRep(message): 
			return message.author == member and ctx.message.channel == message.channel
		if os.path.isfile(f"fiche/{chartype}_{member.name}_{idS}.txt"):
			if arg.lower() == "-edit" and value != "0":
				f = open(f"fiche/{chartype}_{member.name}_{idS}.txt", "r", encoding="utf-8")
				data = f.readlines()
				f.close()
				f = open(f"fiche/{chartype}_{member.name}_{idS}.txt","w", encoding="utf-8")
				if (len(data) > 0):
					data = "".join(data)
					data = data.replace("\'", "\"")
					perso = json.loads(data)
					for k in perso.keys():
						if unidecode.unidecode(k.lower()) == unidecode.unidecode(value.lower()):
							q=await ctx.send(f"Par quoi voulez-vous modifier {value.capitalize()} ? \n Actuellement, sa valeur est {perso.get(unidecode.unidecode(k.lower()))}")
							rep = self.bot.wait_for("message", timeout=300, check=checkRep)
							if rep.content.lower()=="stop":
								await ctx.send("Annulation", delete_after=30)
								await q.delete()
								await rep.delete()
								return
							else:
								perso[k]=rep.content
								f.write(str(perso))
				f.close()
			elif arg.lower() == "-delete":
				os.remove("fiche/{chartype}_{member.name}_{idS}.txt")
				await ctx.send(f"La présentation de {member.name} a été supprimé.")

	@commands.command(aliases=["pres"], brief="Commandes pour modifier une présentation en cours.", usage="fiche (pnj?) -(reprise|delete|edit champs)", help="`fiche -delete` permet de supprimer la présentation en cours. \n `fiche -edit champs` permet d'éditer un champ d'une présentation en cours. \n `fiche -reprise` permet de reprendre l'écriture d'une présentation en cours. \n Par défaut, les fiches sont des fiches de PJ, donc si vous faites un PNJ, n'oublier pas de le préciser après le nom de la commande !")
	async def fiche(self, ctx, chartype="pj"):
		member = ctx.message.author
		idS=ctx.guild.id
		emoji= ["1️⃣", "2️⃣", "3️⃣", "❌"]
		def checkValid(reaction, user):
			return ctx.message.author == user and q.id == reaction.message.id and str(reaction.emoji) in emoji
		def checkRep(message):
			return message.author == member and isinstance(message.channel, discord.DMChannel)
		db = sqlite3.connect("owlly.db", timeout=3000)
		c = db.cursor()
		SQL = "SELECT fiche_pj, fiche_pnj, fiche_validation FROM SERVEUR WHERE idS=?"
		c.execute(SQL, (ctx.guild.id,))
		channel = c.fetchone()
		if (channel[0] is not None) and (channel[1] is not None) and (channel[0] != 0) and (channel[1] != 0):
			if os.path.isfile(f"fiche/{chartype}_{member.name}_{idS}.txt"):
				#tructructruc
				if arg.lower() == "-edit" and value != "0":
					f = open(f"fiche/{chartype}_{member.name}_{idS}.txt", "r", encoding="utf-8")
					data = f.readlines()
					f.close()
					f = open(f"fiche/{chartype}_{member.name}_{idS}.txt", "w", encoding="utf-8")
					if (len(data) > 0):
						data = "".join(data)
						data = data.replace("\'", "\"")
						perso = json.loads(data)
						for k in perso.keys():
							if k == unidecode.unidecode(value.lower()):
								await ctx.send("Regardez vos DM ! 📨 !")
								q = await member.send(f"Par quoi voulez-vous modifier {value.capitalize()} ?\n Actuellement, elle a pour valeur {perso.get(unidecode.unidecode(value.lower()))}.")
								rep = self.bot.wait_for("message", timeout=300, check=checkRep)
								if rep.content.lower() == "stop":
									await q.delete()
									await member.send("Annulation")
									await rep.delete()
									return
								perso[k] = rep.content
								f.write(str(perso))
								q = await q.edit(content="{value.capitalize()} a bien été modifié !")
					f.close()
				elif arg.lower() == "-delete":
					os.remove("fiche/{chartype}_{member.name}_{idS}.txt")
					await ctx.send("Votre présentation a été supprimé.")
				elif arg.lower() == "-reprise":
					await ctx.send("Regardez vos DM 📨 !")
					step = await self.start_presentation(ctx, member, chartype)
					if step == "done":
						msg, img = self.forme(chartype, idS)
						await self.validation(ctx, msg, img, chartype, member)
			else:
				await ctx.send("Vous n'avez pas de présentation en cours !")
		else:
			await ctx.send("Impossible de faire une présentation : Les channels ne sont pas configuré !")


def setup(bot):
	bot.add_cog(memberUtils(bot))

