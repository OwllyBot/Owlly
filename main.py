import emoji
import discord
from discord.ext import commands, tasks
from discord.utils import get
from discord import CategoryChannel
import os
import sqlite3
import sys
import traceback
import keep_alive
import re
import random
from emoji import unicode_codes
from discord import Color
from discord import NotFound
intents = discord.Intents(messages=True,
                          guilds=True,
                          reactions=True,
                          members=True)


# ▬▬▬▬▬▬▬▬▬▬▬ EMOJI ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
def emojis_random():
	all_emojis = unicode_codes.EMOJI_UNICODE["en"]
	all_emojis_key = list(all_emojis.values())
	decodation = []
	for i in range(0, len(all_emojis_key)):
		d = (all_emojis_key[i])
		decodation.append(d)
	rand_emoji = random.sample(decodation, 1)
	rand_emoji = rand_emoji[0]
	return rand_emoji


# ▬▬▬▬▬▬▬▬▬▬▬ PREFIX ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

def get_prefix(bot, message):
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
	c.close()
	db.close()
	return prefix

# ▬▬▬▬▬▬▬▬▬▬▬ COGS ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
initial_extensions = [
    'cogs.clean_db', 'cogs.utils', 'cogs.config', 'cogs.controller', 'cogs.member']
bot = commands.Bot(command_prefix=get_prefix,
                   intents=intents,
                   help_command=None)
token = os.environ.get('DISCORD_BOT_TOKEN_TESTING')
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
  cog=ctx.cog
  if cog:
    if cog._get_overridden_method(cog.cog_command_error) is not None:
      return
    ignored=(commands.CommandNotFound,)
    error=getattr(error,'original',error)
  if isinstance(error,ignored):
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
    print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


@bot.event
async def on_raw_reaction_add(payload):
	print("hey")
	emoji_cat = ["1⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
	db = sqlite3.connect("owlly.db", timeout=3000)
	c = db.cursor()
	c.execute("SELECT idS FROM TICKET")
	serv_ticket = c.fetchall()
	serv_ticket = list(sum(serv_ticket, ()))
	c.execute("SELECT idS FROM CATEGORY")
	serv_cat = c.fetchall()
	serv_cat = list(sum(serv_cat, ()))
	c.execute("SELECT idS FROM SOLO_CATEGORY")
	serv_chan = c.fetchall()
	serv_chan = list(sum(serv_chan, ()))
	serv_here = payload.guild_id
	mid = payload.message_id
	channel = bot.get_channel(payload.channel_id)
	msg = await channel.fetch_message(mid)
	user = bot.get_user(payload.user_id)

	def checkRep(message):
		return message.author == user and channel == message.channel

	if (len(msg.embeds) != 0) and (user.bot is False):
		if (serv_here in serv_ticket) or (serv_here in serv_cat) or (serv_here in serv_chan):
			action = str(payload.emoji.name)
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
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬SELECT : SOLO CATEGORY ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
			sql = "SELECT emote FROM SOLO_CATEGORY WHERE idS=?"
			c.execute(sql, (serv_here, ))
			emoji_chan = c.fetchall()
			emoji_chan = list(sum(emoji_chan, ()))
			sql = "SELECT idM, category FROM SOLO_CATEGORY WHERE idS = ?"
			c.execute(sql, (serv_here, ))
			mono = c.fetchall()
			monoDict = {}
			for i in range(0, (len(mono))):
				extra = {mono[i][0]: mono[i][1]}
				monoDict.update(extra)
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬SELECT CATEGORY ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
			for i in range(0, len(emoji_cat)):
				if str(emoji_cat[i]) == action:
					choice = i
			sql = "SELECT * FROM CATEGORY WHERE idS = ?"
			c.execute(sql, (serv_here, ))
			room = c.fetchall()
			roomDict = {}
			for i in range(0, len(room)):
				cate = room[i][3].split(',')
				extra = {room[i][0]: cate}
				roomDict.update(extra)
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬SWITCH BETWEEN OPTION ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
			if action in emoji_ticket:
				for k, v in appartDict.items():
					if k == mid:
						chan_create = int(v)
						typecreation = "Ticket"
			elif action in emoji_chan:
				for k, v in monoDict.items():
					if k == mid:
						print("here")
						chan_create = int(v)
						typecreation = "Channel"
			else:
				for k, v in roomDict.items():
					if k == mid:
						chan_create = int(v[choice])
						typecreation = "Category"
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬CREATE : TICKET ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
			if typecreation == "Ticket":
				sql = "SELECT num, modulo, limitation FROM TICKET WHERE idM= ?"
				c.execute(sql, (mid, ))
				limitation_options = c.fetchall()
				limitation_options = list(sum(limitation_options, ()))
				for i in range(0, len(limitation_options)):
					nb = limitation_options[0]
					mod = limitation_options[1]
					limit = limitation_options[2]
				nb += 1
				if limit > 0:
					if mod > 0:
						if (nb % mod) > limit:
							nb = (nb + mod) - limit
					else:
						if nb > limit:
							nb = 0
				perso = payload.member.nick
				chan_name = f"{nb} {perso}"
				sql = "UPDATE TICKET SET num = ? WHERE idM = ?"
				var = (nb, mid)
				c.execute(sql, var)
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬CREATE : CHANNEL▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
			elif typecreation == "Channel":
				question = await channel.send(
				    f"Merci d'indiquer le nom de la pièce.")
				chan_rep = await bot.wait_for("message", timeout=300,check=checkRep)
				await question.delete()
				chan_name = chan_rep.content
				if chan_name == "stop":
					channel.send("Annulation de la création.", delete_after=10)
					await chan_rep.delete()
					return
				chan_name = f"{chan_name}"
				await channel.send(f"Création du channel {chan_name}",delete_after=30)
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬SELECT : CATEGORY  ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
			elif typecreation == "Category":
				category_name=get(payload.guild.categories, id=chan_create)
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
	sql = "SELECT idM FROM SOLO_CATEGORY WHERE idS = ?"
	c.execute(sql, (serv, ))
	solo_list = c.fetchall()
	solo_list = list(sum(solo_list, ()))
	for i in ticket_list:
		if i == mid:
			sql = "DELETE FROM TICKET WHERE idS=?"
			c.execute(sql, (serv, ))
	for i in cat_list:
		if i == mid:
			sql = "DELETE FROM CATEGORY WHERE idS = ?"
			c.execute(sql, (serv, ))
	for i in solo_list:
		if i == mid:
			sql = "DELETE FROM SOLO_CATEGORY WHERE idS=?"
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
	print(verif_ticket)
	if verif_ticket == None:
	  print("coucou")
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


#keep_alive.keep_alive()

bot.run(token)