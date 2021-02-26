import discord
from discord.ext import commands, tasks
from discord.utils import get
import unicodedata
import os
import sqlite3
intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True)


class memberAssign(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_member_join(self, Member):
		name=Member.name
		normal_name = unicodedata.normalize('NFKD', name)
		await Member.edit(nick=normal_name)
  
	@commands.command()
	async def member(self, ctx, user: discord.Member, *role: str):
		addRole = []
		infoNew = []
		db = sqlite3.connect("owlly.db", timeout=3000)
		c = db.cursor()
		sql = "SELECT roliste FROM SERVEUR WHERE idS=?"
		c.execute(sql, (ctx.guild.id,))
		defaut=c.fetchone()
		rolelist=[]
		defaut=','.join(defaut)
		defaut=defaut.split(',')
		for i in defaut:
			i=get(ctx.guild.roles, id=int(i))
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
		await ctx.send(f"{user.Mention} est devenu un membre du serveur ! Il•Elle a donc reçu les rôles : {roleInfo}. ", delete_after=60)
		await ctx.message.delete()


def setup(bot):
	bot.add_cog(memberAssign(bot))

