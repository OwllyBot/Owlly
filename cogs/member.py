import discord
from discord.ext import commands, tasks
from discord.utils import get
from discord import CategoryChannel
from discord import NotFound
import os
import sqlite3
intents = discord.Intents(messages=True, guilds=True,
                          reactions=True, members=True)


class memberAssign(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.has_permissions(administrator=True)
	@commands.command()
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
  
	@commands.command()
	async def member(self, ctx, user: discord.Member, *role: str):
		addRole = []
		infoNew = []
		db = sqlite3.connect("owlly.db", timeout=3000)
		c = db.cursor()
		sql = "SELECT roliste FROM SERVEUR WHERE idS=?"
		c.execute(sql, (ctx.guild.id,))
		defaut=c.fetchone()
		for i in defaut:
			print(i)
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
					i=get(ctx.guild.roles, id=i)
				else:
					i=get(ctx.guild.roles,name=i)
				addRole.append(i)
		roleInfo = []
		for plus in addRole:
			await user.add_roles(plus)
			roleInfo.append(plus.name)
		roleInfo = ", ".join(roleInfo)
		if (len(infoNew)) > 0:
			infoNew = "\n ◽".join(infoNew)
			roleInfo = roleInfo + " " + infoNew
		await ctx.send(f"{user.display_name} est devenu un membre du serveur ! Il a donc reçu les rôles : {roleInfo}. ")


def setup(bot):
	bot.add_cog(memberAssign(bot))

