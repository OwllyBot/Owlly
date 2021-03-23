import discord
from discord.ext import commands, tasks
import sqlite3
import re
from discord.ext.commands import TextChannelConverter as tcc
from discord.ext.commands.errors import CommandError



class CogAdmins(commands.Cog, name="Configuration générale", description="Permet d'enregistrer quelques paramètres pour le bot."):
	def __init__(self, bot):
		self.bot = bot

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
  	@commands.command(aliases=["chan_presentation", "validation", "fiche"], help="Permet de configurer le channel dans lequel sera envoyé les présentations des personnages.", brief="Insertion d'un channel pour envoyer les présentations validées.", usage="channel")
  	async def chan_fiche(self, ctx):
		def checkRep(message):
			return message.author == ctx.message.author and ctx.message.channel == message.channel
		def checkValid(reaction, user):
			return ctx.message.author == user and q.id == reaction.message.id and (str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌")
		cl=ctx.guild.id
		await ctx.message.delete()
		q= await ctx.send("Dans quel channel voulez-vous envoyer la présentation des personnages validés ?")
		rep=await self.bot.wait_for("message", timeout=300, check=checkRep)
		db = sqlite3.connect("owlly.db", timeout=3000)
		c = db.cursor()
		if rep.content.lower()=="stop":
			await q.delete()
			await rep.delete()
			await ctx.send("Annulation", delete_after=30)
			return
		try:
			fiche_pj=await tcc.convert(self, ctx, rep.content)
		except CommandError:
			fiche_pj="Error"
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
			try:
				fiche_pnj=tcc.convert(self, ctx, rep.content)
				fiche_pnj=fiche_pnj.id
			except CommandError:
				fiche_pnj="Error"
			if fiche_pnj=="Error":
				await ctx.send("Erreur dans le channel.", delete_after=30)
				await q.delete()
				await rep.delete()
				return
		else:
			fiche_pnj=0
		await q.edit(content="Validation des modification....")
		sql = "UPDATE SERVEUR SET fiche_pj = ? WHERE idS=?"
		var=(fiche_pj.id, cl)
		c.execute(sql, var)
		sql="UPDATE SERVER SET fiche_pnj =? WHERE idS=?"
		var=(fiche_pnj, cl)
		c.execute(sql, var)
		db.commit()
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
