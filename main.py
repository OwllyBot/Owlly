from typing import ContextManager
import discord
from discord.ext import commands, tasks
from discord.ext.commands.core import check
from discord.ext.commands.help import HelpCommand
from discord.utils import get
import os
import sqlite3
import sys
import traceback
import keep_alive
from pretty_help import PrettyHelp
from discord.ext.commands.help import HelpCommand
from pygit2 import Repository
intents = discord.Intents(messages=True, guilds=True,
                          reactions=True, members=True)

# ▬▬▬▬▬▬▬▬▬▬▬ PREFIX ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬


def getprefix(bot, message):
	db = sqlite3.connect("owlly.db", timeout=3000)
	c = db.cursor()
	prefix = "SELECT prefix FROM SERVEUR WHERE idS = ?"
	c.execute(prefix, (int(message.guild.id), ))
	prefix = c.fetchone()
	if prefix is None:
		prefix = "?"
		sql = "INSERT INTO SERVEUR (prefix, idS) VALUES (?,?)"
		var = ("?", message.guild.id)
		c.execute(sql, var)
		db.commit()
	else:
		prefix = prefix[0]
	c.close()
	db.close()
	return prefix

# ▬▬▬▬▬▬▬▬▬▬▬ COGS ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬


initial_extensions = ['cogs.clean_db', 'cogs.utils', 'cogs.config_creators',
    'cogs.author_cmd', 'cogs.member', 'cogs.config_general']
repo_name = Repository('.').head.shorthand
if repo_name == "main":
    	token = os.environ.get('DISCORD_BOT_TOKEN')
else:
    token = os.environ.get('DISCORD_BOT_TOKEN_TESTING')
prefix = "x"
bot = commands.Bot(command_prefix=getprefix, intents=intents)
if __name__ == '__main__':
	for extension in initial_extensions:
		try:
			bot.load_extension(extension)
		except Exception as e:
			print(e)


@bot.event
async def on_command_error(ctx, error):
  if hasattr(ctx.command, 'on_error'):
    return
  cog = ctx.cog
  if cog:
    if cog._get_overridden_method(cog.cog_command_error) is not None:
      return
    ignored = (commands.CommandNotFound,)
    error = getattr(error, 'original', error)
  if isinstance(error, commands.CommandNotFound,):
    return
  if isinstance(error, commands.DisabledCommand):
    await ctx.send(f'{ctx.command} has been disabled.')
  elif isinstance(error, commands.NoPrivateMessage):
    try:
      await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
    except discord.HTTPException:
      pass
  # For this error example we check to see where it came from...
  elif isinstance(error, commands.BadArgument):
    if ctx.command.qualified_name == 'tag list':  # Check if the command being invoked is 'tag list'
      await ctx.send('I could not find that member. Please try again.')
  else:
      # All other Errors not returned come here. And we can just print the default TraceBack.
    print('Ignoring exception in command {}:'.format(
        ctx.command), file=sys.stderr)
    traceback.print_exception(
        type(error), error, error.__traceback__, file=sys.stderr)

color = discord.Color.blurple()
ending = "Si vous trouverez un bug, contactez @Mara#3000 !"
bot.help_command = PrettyHelp(
    color=color, index_title="Owlly - Aide", ending_note=ending, active_time=300)


@bot.event
async def on_raw_reaction_add(payload):
	emoji_cat = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
	db = sqlite3.connect("owlly.db", timeout=3000)
	c = db.cursor()
	c.execute("SELECT idS FROM TICKET")
	serv_ticket = c.fetchall()
	serv_ticket = list(sum(serv_ticket, ()))

	c.execute("SELECT idS FROM CATEGORY")
	serv_cat = c.fetchall()
	serv_cat = list(sum(serv_cat, ()))

	serv_here = payload.guild_id
	mid = payload.message_id
	channel = bot.get_channel(payload.channel_id)
	msg = await channel.fetch_message(mid)
	user = bot.get_user(payload.user_id)

	def checkRep(message):
		return message.author == user and channel == message.channel

	if (len(msg.embeds) != 0) and (user.bot is False):
		if (serv_here in serv_ticket) or (serv_here in serv_cat) :
			action = str(payload.emoji.name)
			print(action)
			print(emoji_cat)
			choice =""
			await msg.remove_reaction(action, user)
			typecreation = "stop"
			chan_create = "stop"
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬SELECT  TICKET ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
			sql = "SELECT emote FROM TICKET WHERE idS = ?"
			c.execute(sql, (serv_here, ))
			emoji_ticket = c.fetchall()
			emoji_ticket = list(sum(emoji_ticket, ()))
			sql = "SELECT idM, channel FROM TICKET WHERE idS = ?"
			c.execute(sql, (serv_here, ))
			appart = c.fetchall()
			appartDict = {}
			for i in range(0, len(appart)):
				extra = {appart[i][0]: appart[i][1]}
				appartDict.update(extra)
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬SELECT CATEGORY ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
			try:
				choice = emoji_cat.index(action)
			except ValueError:
				await channel.send("Il y a eu une erreur ! Merci de contacter le créateur du bot.", delete_after=60)
				return
			sql = "SELECT idM, category_list FROM CATEGORY WHERE idS = ?"
			c.execute(sql, (serv_here, ))
			room = c.fetchall()
			roomDict = {}
			for i in range(0, len(room)):
				cate = room[i][1].split(',')
				extra = {room[i][0]: cate}
				roomDict.update(extra)
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬SWITCH BETWEEN OPTION ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
			if action in emoji_ticket:
				for k, v in appartDict.items():
					if k == mid:
						chan_create = int(v)
						typecreation = "Ticket"
			else:
				for k, v in roomDict.items():
					if k == mid:
						chan_create = int(v[choice])
						typecreation = "Category"
						sql = "SELECT config_name FROM CATEGORY WHERE (idM = ? AND idS = ?)"
						var = (mid, serv_here,)
						c.execute(sql, var)
						name_creat = c.fetchone()
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬CREATE : TICKET ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
			if typecreation == "Ticket":
				sql="SELECT num FROM TICKET WHERE idM=?"
				c.execute(sql,(mid,))
				nb=c.fetchone()[0]
				if nb != "Aucun" and nb.isnumeric():
					nb = int(nb)	
					sql = "SELECT modulo, limitation FROM TICKET WHERE idM= ?"
					c.execute(sql, (mid, ))
					limitation_options = c.fetchall()
					limitation_options = list(sum(limitation_options, ()))
					for i in range(0, len(limitation_options)):
						mod = limitation_options[0]
						limit = limitation_options[1]
					nb += 1
					if limit > 0:
						if mod > 0:
							if (nb % mod) > limit:
								nb = (nb + mod) - limit
						else:
							if nb > limit:
								nb = 0
				sql = "SELECT name_auto FROM TICKET WHERE idM=?"
				c.execute(sql, (mid,))
				para_name = c.fetchone()[0]
				if para_name == "1":
					q = await channel.send("Merci d'indiquer le nom de la pièce")
					chan_rep = await bot.wait_for("message", timeout=300, check=checkRep)
					await q.delete()
					chan_name = chan_rep.content
					if chan_name == "stop":
						await channel.send("Annulation de la création.", delete_after=30)
						await chan_rep.delete()
					else:
						chan_name = f"{chan_name}"
				elif para_name == "2":
					perso = payload.member.nick
					if nb.isnumeric():
						chan_name = f"{nb}{perso}"
					else:
						chan_name=f"{perso}"
				else:
					perso = payload.member.nick
					if nb.ismeric():
						chan_name=f"{nb}{para_name}{perso}"
					else:
						chan_name=f"{para_name}{perso}"
				if nb.isnumeric():
					sql = "UPDATE TICKET SET num = ? WHERE idM = ?"
					var = (nb, mid)
					c.execute(sql, var)
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬SELECT : CATEGORY  ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
			elif typecreation == "Category":
				guild_id=payload.guild_id
				guild = discord.utils.find(lambda g: g.id == guild_id, bot.guilds)
				category_name=get(guild.categories, id=chan_create)
				if name_creat == 1:
					question = await channel.send(f"Catégorie {category_name} sélectionnée. \n Merci d'indiquer le nom de la pièce")
					chan_rep = await bot.wait_for("message",timeout=300,check=checkRep)
					await question.delete()
					chan_name = chan_rep.content
					if chan_name == "stop":
						channel.send("Annulation de la création.", delete_after=10)
						await chan_rep.delete()
						return
					chan_name = f"{chan_name}"
					chan_name = chan_name.replace(" ", "")
				else:
					chan_name=f"{payload.member.nick}"
				await channel.send(f"Création du channel {chan_name} dans {category_name}.", delete_after=30)

# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬CREATION▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
			category = bot.get_channel(chan_create)
			new_chan = await category.create_text_channel(chan_name)
			sql = "INSERT INTO AUTHOR (channel_id, userID, idS, created_by) VALUES (?,?,?,?)"
			var = (new_chan.id, payload.user_id, serv_here, payload.message_id)
			c.execute(sql, var)
			db.commit()
			c.close()
			db.close()


@bot.event
async def on_raw_message_delete(payload):
	mid = payload.message_id
	serv = payload.guild_id
	db = sqlite3.connect("owlly.db", timeout=3000)
	c = db.cursor()
	sql = "SELECT idM FROM TICKET WHERE idS=?"
	c.execute(sql, (serv, ))
	ticket_list = c.fetchall()
	ticket_list = list(sum(ticket_list, ()))
	sql = "SELECT idM FROM CATEGORY WHERE idS = ?"
	c.execute(sql, (serv, ))
	cat_list = c.fetchall()
	cat_list = list(sum(cat_list, ()))
	
	for i in ticket_list:
		if i == mid:
			sql = "DELETE FROM TICKET WHERE idS=?"
			c.execute(sql, (serv, ))
	for i in cat_list:
		if i == mid:
			sql = "DELETE FROM CATEGORY WHERE idS = ?"
			c.execute(sql, (serv, ))
	
	db.commit()
	c.close()
	db.close()


@bot.event
async def on_guild_channel_delete(channel):
	db = sqlite3.connect("owlly.db", timeout=3000)
	c = db.cursor()
	delete = channel.id
	sql = "SELECT created_by FROM AUTHOR WHERE created_by =?"
	c.execute(sql, (delete, ))
	verif_ticket = c.fetchone()
	if verif_ticket != None :
		sql = "SELECT num FROM TICKET WHERE idM = ?"
		c.execute(sql, verif_ticket)
		count = c.fetchone()
		if count > 0:
			count = int(count[0]) - 1
		else:
			count = 0
		sql = "UPDATE TICKET SET num = ? WHERE idM = ?"
		var = (count, (int(verif_ticket[0])))
		c.execute(sql, var)
	sql = "DELETE FROM AUTHOR WHERE channel_id = ?"
	c.execute(sql, (delete, ))
	db.commit()
	c.close()
	db.close()


@bot.event
async def on_member_remove(member):
	dep = int(member.id)
	db = sqlite3.connect("owlly.db", timeout=3000)
	c = db.cursor()
	sql = "DELETE FROM AUTHOR WHERE UserID = ?"
	c.execute(sql, (dep, ))
	db.commit()
	c.close()
	db.close()


@bot.event
async def on_guild_remove(guild):
	server = guild.id
	db = sqlite3.connect("owlly.db", timeout=3000)
	c = db.cursor()
	sql1 = "DELETE FROM AUTHOR WHERE idS = ?"
	sql2 = "DELETE FROM TICKET WHERE idS = ?"
	sql3 = "DELETE FROM CATEGORY WHERE idS = ?"
	c.execute(sql1, (server, ))
	c.execute(sql2, (server, ))
	c.execute(sql3, (server, ))
	sql = "DELETE FROM SERVEUR WHERE idS = ?"
	var = guild.id
	c.execute(sql, (var, ))
	db.commit()
	c.close()
	db.close()

if repo_name=="main":
	token = os.environ.get('DISCORD_BOT_TOKEN')
	keep_alive.keep_alive()
else:
    token = os.environ.get('DISCORD_BOT_TOKEN_TESTING')
bot.run(token)

