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

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True)
def get_prefix (bot, message):
    db = sqlite3.connect("owlly_test.db", timeout=3000)
    c = db.cursor()
    prefix = "SELECT prefix FROM SERVEUR WHERE idS = ?"
    c.execute(prefix, (int(message.guild.id),))
    prefix = c.fetchone()
    if prefix is None :
        prefix = "?"
        sql="INSERT INTO SERVEUR (prefix, idS) VALUES (?,?)"
        var = ("?", message.guild.id)
        c.execute(sql, var)
        db.commit()
    c.close()
    db.close()
    return prefix

initial_extensions = ['cogs.clean_db']
bot = commands.Bot(command_prefix=get_prefix, intents=intents,help_command=None)
token = os.environ.get('DISCORD_BOT_TOKEN_TESTING')
if __name__ == '__main__':
    for extension in initial_extensions:    
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(e)

async def search_cat_name(name, ctx):
    emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    def checkValid(reaction, user):
        return ctx.message.author == user and q.id == reaction.message.id and str(reaction.emoji) in emoji
    cat_list=[]
    for cat in ctx.guild.categories:
        cat_list.append(cat.name)
    search=[w for w in cat_list if name in w]
    search_list=[]
    lg=len(search)
    if lg == 0:
        await ctx.send ("Aucune catégorie portant un nom similaire existe, vérifier votre frappe.", delete_after=30)
        return
    elif lg == 1:
        name = search[0]
        name=get(ctx.guild.categories, name=name)
        number = name.id
        return number
    elif lg > 1 and lg < 10:
        for i in range (0, lg):
            phrase=f"{emoji[i]} : {search[i]}"
            search_list.append(phrase)
        search_question = "\n".join(search_list)
        q= await ctx.send(f"Plusieurs catégories correspondent à ce nom. Pour choisir celle que vous souhaitez, cliquez sur le numéro correspondant :\n {search_question}")
        for i in range(0,lg):
            await q.add_reaction(emoji[i])
        select, user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
        for i in range (0, lg):
            if str(select) == str(emoji[i]):
                name=search[i]
                mot=search[i]
        name=get(ctx.guild.categories, name=name)
        number=name.id
        q.delete()
        await ctx.send(f"Catégorie : {mot} ✅ \n >Vous pouvez continuer l'inscription des channels. ")
        return number
    else:
        await ctx.send("Il y a trop de correspondance ! Merci de recommencer la commande.", delete_after=30)
        return
@bot.event
async def on_ready():
    print("[LOGS] ONLINE")
    await bot.change_presence(activity=discord.Game("ouvrir des portes !"))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send("Commande inconnue ! \n Pour avoir la liste des commandes utilisables, utilise `!help` ou `!command`")

@bot.event
async def on_guild_join(guild):
    db = sqlite3.connect("owlly_test.db", timeout=3000)
    c = db.cursor()
    sql="INSERT INTO SERVEUR (prefix, idS) VALUES (?,?)"
    var = ("?", guild.id)
    c.execute(sql, var)
    db.commit()
    c.close()
    db.close()

@bot.event
async def on_message(message):
    channel=message.channel
    db = sqlite3.connect("owlly_test.db", timeout=3000)
    c = db.cursor()
    prefix = "SELECT prefix FROM SERVEUR WHERE idS = ?"
    c.execute(prefix, (int(message.guild.id),))
    prefix = c.fetchone()
    if bot.user.mentioned_in(message) and 'prefix' in message.content:
        await channel.send(f'Mon prefix est {prefix}')
    await bot.process_commands(message)

@bot.command()
@commands.has_permissions(administrator=True)
async def set_prefix(ctx, prefix):
    db = sqlite3.connect("owlly_test.db", timeout=3000)
    c = db.cursor()
    sql="UPDATE SERVEUR SET prefix = ? WHERE idS = ?"
    var = (prefix, ctx.guild.id)
    c.execute(sql, var)
    await ctx.send(f"Prefix changé pour {prefix}")
    db.commit()
    c.close()
    db.close()

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong with {str(round(bot.latency, 2))}")
@bot.command(name="whoami")
async def whoami(ctx):
    await ctx.send(f"You are {ctx.message.author.name}")

@bot.command()
async def serv(ctx):
    await ctx.send(f"{ctx.message.guild.id}")

@bot.command()
async def clear(ctx, amount=3):
    await ctx.channel.purge(limit=amount)

@commands.has_permissions(administrator=True)
@bot.command()
async def ticket(ctx):
    def checkValid(reaction, user):
        return ctx.message.author == user and question.id == reaction.message.id and (str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌")
    def checkRep(message):
        return message.author == ctx.message.author and ctx.message.channel == message.channel
    limit_content = 0
    mod_content = 0
    nb_dep_content=0
    guild=ctx.message.guild
    await ctx.message.delete()
    db = sqlite3.connect("owlly_test.db", timeout=3000)
    c = db.cursor()
    question = await ctx.send (f"Quel est le titre de l'embed ?")
    titre = await bot.wait_for("message", timeout = 300, check = checkRep)
    typeM = titre.content
    if typeM == "stop":
        await ctx.send ("Annulation !", delete_after=10)
        await titre.delete()
        await question.delete()
        return
    await question.delete()
    question = await ctx.send (f"Quelle est sa description ?")
    desc = await bot.wait_for("message", timeout=300, check=checkRep)
    if desc.content == "stop":
        await ctx.send ("Annulation !", delete_after=10)
        await desc.delete()
        await question.delete()
        return
    await question.delete()
    question = await ctx.send ("Dans quel catégorie voulez-vous créer vos tickets ? Rappel : Seul un modérateur pourra les supprimer, car ce sont des tickets permanent.\n Vous pouvez utiliser le nom ou l'ID de la catégorie !")
    ticket_chan=await bot.wait_for("message", timeout=300, check=checkRep)
    ticket_chan_content=ticket_chan.content
    cat_name = "none"
    if ticket_chan_content == "stop":
        await ctx.send ("Annulation !", delete_after=10)
        await question.delete()
        await ticket_chan.delete()
        return
    else:
        if ticket_chan_content.isnumeric():
            ticket_chan_content=int(ticket_chan_content)
            cat_name = get(guild.categories, id=ticket_chan_content)
            if ticket_chan_content == "None" :
                ctx.send("Erreur : Cette catégorie n'existe pas !", delete_after=30)
                return
        else:
            ticket_chan_content=await search_cat_name(ticket_chan_content, ctx)
            cat_name = get(guild.categories, id=ticket_chan_content)
    await question.delete()
    question = await ctx.send (f"Quelle couleur voulez vous utiliser ?")
    color = await bot.wait_for("message", timeout=300, check=checkRep)
    col = color.content
    if (col.find ("#") == -1) and (col != "stop") and (col != "0"):
        await ctx.send (f"Erreur ! Vous avez oublié le # !", delete_after=30)
        await question.delete()
        await color.delete()
        return
    elif col == "stop":
        await ctx.send ("Annulation !", delete_after=10)
        await question.delete()
        await color.delete()
        return
    elif col == "0":
        await question.delete()
        col = "0xabb1b4"
        col = int (col, 16)
    else:
        await question.delete()
        col = col.replace("#", "0x")
        col = int(col, 16)
    question = await ctx.send ("Voulez-vous ajouter une image ?")
    await question.add_reaction("✅")
    await question.add_reaction("❌")
    reaction,user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
    if reaction.emoji =="✅":
        await question.delete()
        question = await ctx.send ("Merci d'envoyer l'image. \n**⚡ ATTENTION : LE MESSAGE EN REPONSE EST SUPPRIMÉ VOUS DEVEZ DONC UTILISER UN LIEN PERMANENT (hébergement sur un autre channel/serveur, imgur, lien google...)**")
        img = await bot.wait_for("message", timeout=300, check=checkRep)
        img_content = img.content
        if img_content == "stop":
            await ctx.send ("Annulation !", delete_after=10)
            await question.delete()
            await img.delete()
            return
        else:
            await question.delete()
            await img.delete()
    else:
        await question.delete()
        img_content = "none"
    question = await ctx.send ("Voulez-vous fixer un nombre de départ ?")
    await question.add_reaction("✅")
    await question.add_reaction("❌")
    reaction,user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
    if reaction.emoji == "✅":
        await question.delete()
        question = await ctx.send ("Merci d'indiquer le nombre de départ.")
        nb_dep = await bot.wait_for("message", timeout=300, check=checkRep)
        if nb_dep.content == "stop":
            await question.delete()
            await ctx.send ("Annulation !", delete_after=10)
            await nb_dep.delete()
            return
        else:
            nb_dep_content=int(nb_dep.content)
            await question.delete()
    else:
        nb_dep_content=0
        await question.delete()
    question = await ctx.send ("Voulez-vous fixer une limite ? C'est à dire que le ticket va se reset après ce nombre.")
    await question.add_reaction("✅")
    await question.add_reaction("❌")
    reaction,user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
    if reaction.emoji == "✅":
        await question.delete()
        question = await ctx.send ("Merci d'indiquer la limite.")
        limit = await bot.wait_for("message", timeout=300, check=checkRep)
        if limit.content == "stop":
            await ctx.send ("Annulation !", delete_after=10)
            await question.delete()
            await limit.delete()
            return
        else:
            limit_content=int(limit.content)
            await limit.delete()
            mod_content = 0
            await question.delete()
            question = await ctx.send("Voulez-vous, après la limite, augmenter d'un certain nombre le numéro ?")
            await question.add_reaction("✅")
            await question.add_reaction("❌")
            reaction,user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
            if reaction.emoji == "✅":
                await question.delete()
                question = await ctx.send("Quel est donc ce nombre ?")
                mod = await bot.wait_for("message", timeout=300, check=checkRep)
                if mod.content == "stop":
                    await ctx.send ("Annulation !", delete_after=10)
                    await mod.delete()
                    await question.delete()
                    return
                else:
                    mod_content= int(mod.content)
                    await question.delete()
                    await mod.delete()
            else:
                await question.delete()
    else:
        limit_content = 0
        mod_content = 0
        await question.delete()
    guild= ctx.message.guild
    question = await ctx.send (f"Vos paramètres sont : \n Titre : {typeM} \n Numéro de départ : {nb_dep_content} \n Intervalle entre les nombres (on se comprend, j'espère) : {mod_content} (0 => Pas d'intervalle) \n Limite : {limit_content} (0 => Pas de limite) \n Catégorie : {cat_name}. \n\n Confirmez-vous ces paramètres ?")
    await question.add_reaction("✅")
    await question.add_reaction("❌")
    reaction,user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
    if reaction.emoji == "✅":
        await question.delete()
        embed = discord.Embed(title=titre.content, description=desc.content, color=col)
        if img_content != "none":
            embed.set_image(url=img_content)
        question = await ctx.send ("Vous pouvez choisir l'émoji de réaction en réagissant à ce message. Il sera sauvegardé et mis sur l'embed. Par défaut, l'émoji est : 🗒")
        symb,user = await bot.wait_for("reaction_add", timeout=300)
        if symb.custom_emoji :
            if symb.emoji in guild.emojis:
                symbole = str (symb.emoji)	
            else:
                symbole = "🗒"
        elif symb.emoji != "🗒":
            symbole=str(symb.emoji)
        else:
            symbole = "🗒"
        await question.delete()
        react = await ctx.send(embed=embed)
        await react.add_reaction(symbole)
        sql = "INSERT INTO TICKET (idM, channelM, channel, num, modulo, limitation, emote, idS) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        id_serveur = ctx.message.guild.id
        id_message = react.id
        chanM = ctx.channel.id
        var = (id_message, chanM, ticket_chan_content, nb_dep_content, mod_content, limit_content, symbole, id_serveur)
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
@bot.command()
async def category(ctx):
    def checkValid(reaction, user):
        return ctx.message.author == user and question.id == reaction.message.id and (str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌")
    def checkRep(message):
        return message.author == ctx.message.author and ctx.message.channel == message.channel
    print("here")
    emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    db = sqlite3.connect("owlly_test.db", timeout=3000)
    c = db.cursor()
    chan = []
    question = await ctx.send("Merci d'envoyer l'ID des catégories (ou leurs noms) que vous souhaitez utiliser pour cette configuration. \n Utiliser `stop` pour valider la saisie et `cancel` pour annuler la commande. ")
    while True:
        channels = await bot.wait_for("message", timeout=300, check = checkRep)
        await channels.add_reaction("✅")
        if channels.content.lower() == 'stop':
            await channels.delete(delay=10)
            await ctx.send("Validation en cours !", delete_after=10)
            break
        elif channels.content.lower() == 'cancel':
            await channels.delete()
            await ctx.send("Annulation !", delete_after=10)
            return
        else:
            chan_search=channels.content
            if chan_search.isnumeric():
                chan_search = int(chan_search)
            else:
                chan_search=await search_cat_name(chan_search, ctx)
        chan.append(chan_search)
        await channels.delete(delay=10)
    if len(chan) >= 10 :
        await ctx.send ("Erreur ! Vous ne pouvez pas mettre plus de 9 catégories !", delete_after=30)
        return
    namelist=[]
    guild= ctx.message.guild
    for i in range(0,len(chan)):
        number=int(chan[i])
        cat = get(guild.categories, id=number)
        if cat == "None" :
            ctx.send("Erreur : Cette catégorie n'existe pas !", delete_after=30)
            return
        phrase = f"{emoji[i]} : {cat}"
        namelist.append(phrase)
    msg = "\n".join(namelist)
    parameters = await ctx.send (f"Votre channel sera donc créer dans une des catégories suivantes :\n {msg} \n\n Le choix final de la catégories se fait lors des réactions. ")
    parameters_save = parameters.content
    await parameters.delete(delay=10)
    await question.delete()
    question = await ctx.send (f"Quel est le titre de l'embed ?")
    titre = await bot.wait_for("message", timeout = 300, check = checkRep)
    if titre.content == "stop" :
        await ctx.send("Annulation !", delete_after=30)
        await question.delete()
        await titre.delete()
        return
    else:
        await question.delete()
        titre_content = titre.content
    question = await ctx.send (f"Quelle couleur voulez vous utiliser ?")
    color = await bot.wait_for("message", timeout=300, check=checkRep)
    col = color.content
    if (col.find ("#") == -1) and (col != "stop") and (col != "0"):
        await ctx.send (f"Erreur ! Vous avez oublié le # !", delete_after=30)
        await color.delete()
        await question.delete()
        return
    elif col == "stop":
        await ctx.send ("Annulation !", delete_after=10)
        await color.delete()
        await question.delete()
        return
    elif col == "0":
        col = "0xabb1b4"
        col = int(col, 16)
        await question.delete()
    else:
        await question.delete()
        col = col.replace("#", "0x")
        col = int(col, 16)
    question = await ctx.send ("Voulez-vous utiliser une image ?")
    await question.add_reaction("✅")
    await question.add_reaction("❌")
    reaction,user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
    if reaction.emoji =="✅":
        await question.delete()
        question = await ctx.send ("Merci d'envoyer l'image. \n**⚡ ATTENTION : LE MESSAGE EN REPONSE EST SUPPRIMÉ VOUS DEVEZ DONC UTILISER UN LIEN PERMANENT (hébergement sur un autre channel/serveur, imgur, lien google...)**")
        img = await bot.wait_for("message", timeout=300, check=checkRep)
        img_content = img.content
        if img_content == "stop":
            await ctx.send ("Annulation !", delete_after=10)
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
    question = await ctx.send (f"Les catégories dans lequel vous pourrez créer des canaux seront : {parameters_save} \n Validez-vous ses paramètres ?")
    await question.add_reaction("✅")
    await question.add_reaction("❌")
    reaction,user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
    if reaction.emoji == "✅":
        react = await ctx.send(embed=embed)
        for i in range(0,len(chan)):
            await react.add_reaction(emoji[i])
        category_list_str = ",".join(chan)
        sql = ("INSERT INTO CATEGORY (idM, channelM, category_list, idS) VALUES (?,?,?,?)")
        id_serveur = ctx.message.guild.id
        id_message = react.id
        chanM = ctx.channel.id
        var = (id_message, chanM, category_list_str, id_serveur)
        c.execute(sql, var)
        db.commit()
        c.close()
        db.close()
        await titre.delete()
        await color.delete()
        await question.delete()
    else:
        await ctx.send ("Annulation !", delete_after=10)
        await question.delete()
        await titre.delete()
        await color.delete()
        return 

@bot.event
async def on_raw_reaction_add(payload):
    def checkRep(message):
        return message.author == payload.message.author and payload.message.channel == message.channel
    db = sqlite3.connect("owlly_test.db", timeout=3000)
    c = db.cursor()
    c.execute("SELECT idS FROM TICKET")
    serv_ticket = c.fetchall()
    serv_ticket=list(sum(serv_ticket, ()))
    c.execute("SELECT idS FROM CATEGORY")
    serv_cat = c.fetchall()
    serv_cat=list(sum(serv_cat,()))
    serv_here = payload.guild_id
    mid = payload.message_id
    channel= bot.get_channel(payload.channel_id)
    msg = await channel.fetch_message(mid)
    user = bot.get_user(payload.user_id)
    if (len (msg.embeds) != 0) and (user.bot is False):
        if (serv_here in serv_ticket) or (serv_here in serv_cat):
            emoji_cat = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
            sql = "SELECT emote FROM TICKET WHERE idS = ?"
            c.execute(sql, (serv_here,))
            emoji_ticket=c.fetchall()
            emoji_ticket=list(sum(emoji_ticket,()))
            sql = "SELECT idM, channel FROM TICKET WHERE idS = ?"
            c.execute(sql, (serv_here,))
            appart=c.fetchall()
            appartDict={}
            action = str(payload.emoji.name)
            await msg.remove_reaction(action,user)
            user = bot.get_user(payload.user_id)
            for i in range(0, len(emoji_cat)):
                if str(emoji_cat[i]) == action :
                    choice = i
                    break
            typecreation = "stop"
            chan_create = "stop"
            for i in range (0, len(appart)):
                extra={appart[i][0] : appart[i][1]}
                appartDict.update(extra)
            sql = "SELECT * FROM CATEGORY WHERE idS = ?"
            c.execute(sql, (serv_here,))
            room = c.fetchall()
            roomDict={}
            for i in range (0, len(room)):
                cate = room[i][3].split(',')
                extra={room[i][0] : cate}
                roomDict.update(extra)
            if action in emoji_ticket:
                for k, v in appartDict.items():
                    if k == mid:
                        chan_create = int(v)
                        typecreation = "True"
            else:
                for k, v in roomDict.items():
                    if k == mid:
                        chan_create=int(v[choice])
                        typecreation = "False"
            if typecreation == "True":
                # Création d'un ticket
                sql = "SELECT num, modulo, limitation FROM TICKET WHERE idM= ?"
                c.execute(sql, (mid,))
                limitation_options = c.fetchall()
                limitation_options=list(sum(limitation_options,()))
                for i in range(0, len(limitation_options)):
                    nb = limitation_options[0]
                    mod = limitation_options[1]
                    limit = limitation_options[2]
                nb +=1
                if limit > 0:
                    if mod > 0:
                        if (nb % mod) > limit:
                            nb = (nb + mod) - limit
                    else:
                        if nb > limit:
                            nb = 0
                perso = payload.member.nick
                chan_name = f"{nb} {perso}"
                category = bot.get_channel(chan_create)
                new_chan = await category.create_text_channel(chan_name)
                sql = "UPDATE TICKET SET num = ? WHERE idM = ?"
                var = (nb, mid)
                c.execute(sql, var)
                sql = "INSERT INTO AUTHOR (channel_id, userID, idS, created_by) VALUES (?,?,?,?)"
                var = (new_chan.id, payload.user_id, serv_here, mid)
                c.execute(sql, var)
                db.commit()
                c.close()
                db.close()

            elif typecreation == "False" : #Category et pièce
                category_name = bot.get_channel(chan_create)
                question = await channel.send(f"Catégorie {category_name} sélectionnée. Merci d'indiquer le nom du channel.")
                chan_rep = await bot.wait_for("message", timeout=300, check=checkRep)
                await question.delete()
                chan_name = chan_rep.content
                if chan_name == "stop":
                    channel.send("Annulation de la création.", delete_after=10)
                    await chan_rep.delete()
                    return
                await channel.send(f"Création du channel {chan_name} dans {category_name}.", delete_after=30)
                await chan_rep.delete()
                category = bot.get_channel(chan_create)
                new_chan = await category.create_text_channel(chan_name)
                sql = "INSERT INTO AUTHOR (channel_id, userID, idS, created_by) VALUES (?,?,?,?)"
                var = (new_chan.id, payload.user_id,serv_here, payload.message_id)
                c.execute(sql, var)
                db.commit()
                c.close()
                db.close()

@bot.event
async def on_raw_message_delete(payload):
    mid = payload.message_id
    serv= payload.guild_id
    db = sqlite3.connect("owlly_test.db", timeout=3000)
    c = db.cursor()
    sql="SELECT idM FROM TICKET WHERE idS=?"
    c.execute(sql,(serv,))
    ticket_list=c.fetchall()
    ticket_list=list(sum(ticket_list,()))
    sql="SELECT idM FROM CATEGORY WHERE idS = ?"
    c.execute(sql, (serv,))
    cat_list=c.fetchall()
    cat_list=list(sum(cat_list,()))
    for i in ticket_list:
        if i == mid:
            sql="DELETE FROM TICKET WHERE idS=?"
            c.execute(sql, (serv,))
    for i in cat_list:
        if i == mid:
            sql="DELETE FROM CATEGORY WHERE idS = ?"
            c.execute(sql,(serv,))

@bot.command(name="description", aliases=['desc', 'edit_desc'])
async def description ( ctx, arg):
    channel_here = ctx.channel.id
    channel = bot.get_channel(channel_here)
    db = sqlite3.connect("owlly_test.db", timeout=3000)
    c = db.cursor()
    sql = "SELECT channel_id FROM AUTHOR WHERE (userID = ? AND idS = ?)"
    var = (ctx.author.id, ctx.guild.id)
    c.execute(sql, var)
    list_chan=c.fetchall()
    list_chan = list(sum(list_chan,()))
    if channel_here in list_chan:
        await channel.edit(topic=arg)
        await ctx.send ("Changé !", delete_after=10)
        await ctx.delete()
    else:
        ctx.send("Erreur, vous n'êtes pas l'auteur de ce channel !", delete_after=30)
        await ctx.delete()
    c.close()
    db.close()

@bot.command(aliases=['pin'])
async def pins(ctx, id_message):
    channel_here = ctx.channel.id
    channel = bot.get_channel(channel_here)
    db = sqlite3.connect("owlly_test.db", timeout=3000)
    c = db.cursor()
    sql = "SELECT channel_id FROM AUTHOR WHERE (userID = ? AND idS = ?)"
    var = (ctx.author.id, ctx.guild.id)
    c.execute(sql, var)
    list_chan=c.fetchall()
    list_chan = list(sum(list_chan,()))
    if channel_here in list_chan:
        message = await channel.fetch_message(id_message)
        await message.pin()
        await ctx.delete()
    else:
        await ctx.send("Vous n'êtes pas l'auteur de ce channel !", delete_after=10)
        await ctx.delete()
    c.close()
    db.close()


@bot.command()
async def unpin(ctx, id_message):
    channel_here = ctx.channel.id
    channel = bot.get_channel(channel_here)
    db = sqlite3.connect("owlly_test.db", timeout=3000)
    c = db.cursor()
    sql = "SELECT channel_id FROM AUTHOR WHERE (userID = ? AND idS = ?)"
    var = (ctx.author.id, ctx.guild.id)
    c.execute(sql, var)
    list_chan=c.fetchall()
    list_chan = list(sum(list_chan,()))
    if channel_here in list_chan:
        message = await channel.fetch_message(id_message)
        await message.unpin()
        await ctx.delete()
    else:
        await ctx.send("Vous n'êtes pas l'auteur de ce channel !", delete_after=10)
        await ctx.delete()
    c.close()
    db.close()

@bot.command(aliases=['name'])
async def rename (ctx, arg):
    channel_here = ctx.channel.id
    channel = bot.get_channel(channel_here)
    db = sqlite3.connect("owlly_test.db", timeout=3000)
    c = db.cursor()
    sql = "SELECT channel_id FROM AUTHOR WHERE (userID = ? AND idS = ?)"
    var = (ctx.author.id, ctx.guild.id)
    c.execute(sql, var)
    list_chan=c.fetchall()
    list_chan = list(sum(list_chan,()))
    if channel_here in list_chan:
        await channel.edit(name=arg)
        await ctx.send ("Changé !", delete_after=10)
        await ctx.delete()
    else:
        ctx.send("Erreur, vous n'êtes pas l'auteur de ce channel !", delete_after=30)
        await ctx.delete()
    c.close()
    db.close()

@commands.has_permissions(administrator=True)
@bot.command(aliases=["count", "edit_count"])
async def recount(ctx, arg, ticket_id):
    db = sqlite3.connect("owlly_test.db", timeout=3000)
    c = db.cursor() 
    search_db="SELECT num FROM TICKET WHERE idM=?"
    sql="UPDATE TICKET SET num = ? WHERE idM=?"
    search_regex_arg=re.search('(?:(?P<channel_id>[0-9]{15,21})-)?(?P<message_id>[0-9]{15,21})$', str(arg))
    if search_regex_arg is None:
        search_regex_arg=re.search('(?:(?P<channel_id>[0-9]{15,21})-)?(?P<message_id>[0-9]{15,21})$', str(ticket_id))
        if search_regex_arg is None: 
            await ctx.send("Aucun de vos arguments ne correspond à l'ID du message du créateur de ticket...", delete_after=30)
            await ctx.delete()
            c.close()
            db.close()
            return
        else:
            arg=int(arg)
            ticket_id=int(ticket_id)
    else:
        silent=int(ticket_id)
        ticket_id=int(arg)
        arg=silent
    c.execute(search_db, (ticket_id,))
    search=c.fetchone()
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

@bot.event
async def on_guild_channel_delete (channel):
    db = sqlite3.connect("owlly_test.db", timeout=3000)
    c = db.cursor()
    delete=channel.id
    sql="SELECT created_by FROM AUTHOR WHERE channel_id=?"
    c.execute(sql, (delete,))
    verif_ticket=c.fetchone()
    sql="SELECT num FROM TICKET WHERE idM = ?"
    c.execute(sql, verif_ticket)
    count=c.fetchone()
    count = int(count[0])-1
    sql="UPDATE TICKET SET num = ? WHERE idM = ?"
    var=(count, (int(verif_ticket[0])))
    c.execute(sql, var)
    sql="DELETE FROM AUTHOR WHERE channel_id = ?"
    c.execute(sql, (delete,))
    db.commit()
    c.close()
    db.close()

@bot.event
async def on_member_remove(member):
    dep = int(member.id)
    db = sqlite3.connect("owlly_test.db", timeout=3000)
    c = db.cursor()
    sql="DELETE FROM AUTHOR WHERE UserID = ?"
    c.execute(sql, (dep,))
    db.commit()
    c.close()
    db.close()

@bot.event
async def on_guild_remove(guild):
    server = guild.id
    db = sqlite3.connect("owlly_test.db", timeout=3000)
    c = db.cursor()
    sql1="DELETE FROM AUTHOR WHERE idS = ?"
    sql2 = "DELETE FROM TICKET WHERE idS = ?"
    sql3 = "DELETE FROM CATEGORY WHERE idS = ?"
    c.execute(sql1, (server,))
    c.execute(sql2, (server,))
    c.execute(sql3, (server,))
    sql="DELETE FROM SERVEUR WHERE idS = ?"
    var = guild.id
    c.execute(sql, var)
    db.commit()
    c.close()
    db.close()

@bot.command()
async def prefix(ctx):
    server = ctx.guild.id
    db = sqlite3.connect("owlly_test.db", timeout=3000)
    c = db.cursor()
    prefix = "SELECT prefix FROM SERVEUR WHERE idS = ?"
    c.execute(prefix, (server,))
    prefix = c.fetchone()
    message = await ctx.send(f"Mon préfix est {prefix}")
    return commands.when_mentioned_or(prefix)(bot, message)

@bot.command(aliases=['command','commands','owlly'])
async def help(ctx):
    db = sqlite3.connect("owlly_test.db", timeout=3000)
    c = db.cursor()
    serv = ctx.guild.id
    sql="SELECT prefix FROM SERVEUR WHERE idS = ?"
    c.execute(sql, (serv,))
    p = c.fetchone()
    p=p[0]
    embed = discord.Embed(title="Liste des commandes", description="", color=0xaac0cc)
    embed.add_field(name=f"Configurer les créateurs (administrateur)", value=f":white_small_square: Ticket : `{p}ticket`\n :white_small_square: Catégories : `{p}category`", inline=False)
    embed.add_field(name="Fonction sur les channels", value=f"Vous devez être l'auteur original du channel et utiliser ses commandes sur le channel voulu !\n :white_small_square: Editer la description : `{p}desc description` ou `{p}description`\n :white_small_square: Pin un message : `{p}pins <idmessage>` \n :white_small_square: Unpin un message : `{p}unpin <idmessage>` \n :white_small_square: Changer le nom du channel : `{p}rename nom`", inline=False)
    embed.add_field(name="Administration", value=f":white_small_square: Prefix : `{p}prefix` \n :white_small_square: Changer le prefix (administrateur) : `{p}set_prefix` \n :white_small_square: Changer le compteur des tickets (administrateur): `{p}recount nb`", inline=False)
    await ctx.send(embed=embed)
#keep_alive.keep_alive()
bot.run(token)
