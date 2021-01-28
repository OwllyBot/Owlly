import discord
from discord.ext import commands
from discord.utils import get
from discord import CategoryChannel
import os
import sqlite3
intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True)

bot = commands.Bot(command_prefix="!", intents=intents)
token = os.environ.get('DISCORD_BOT_TOKEN')

@bot.event
async def on_ready():
    print("[LOGS] ONLINE")
    await bot.change_presence(activity=discord.Game("ouvrir des portes !"))

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

@bot.command()
async def ticket(ctx):
    limit_content = 0
    mod_content = 0
    nb_dep_content=0
    guild=ctx.message.guild
    def checkValid(reaction, user):
        return ctx.message.author == user and question.id == reaction.message.id and (str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌")
    def checkRep(message):
        return message.author == ctx.message.author and ctx.message.channel == message.channel
    await ctx.message.delete()
    db = sqlite3.connect("owlly.db", timeout=3000)
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
    question = await ctx.send ("Dans quel catégorie voulez-vous créer vos tickets ? Rappel : Seul un modérateur pourra les supprimer, car ce sont des tickets permanent.\n Vous devez indiquer un ID de catégorie !")
    ticket_chan=await bot.wait_for("message", timeout=300, check=checkRep)
    ticket_chan_content=ticket_chan.content
    cat_name = "none"
    if ticket_chan_content == "stop":
        await ctx.send ("Annulation !", delete_after=10)
        await question.delete()
        await ticket_chan.delete()
        return
    else:
        ticket_chan_content=int(ticket_chan_content)
        cat_name = get(guild.categories, id=ticket_chan_content)
        if cat_name == "None" or cat_name == "none":
            ctx.send("Erreur ! Cette catégorie n'existe pas.", delete_after=30)
            await question.delete()
            await ticket_chan.delete()
            return
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
        sql = "INSERT INTO TICKET (idM, type, channel, num, modulo, limitation, emote, idS) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        id_serveur = ctx.message.guild.id
        id_message = react.id
        var = (id_message, typeM, ticket_chan_content, nb_dep_content, mod_content, limit_content, symbole, id_serveur)
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

@bot.command()
async def category(ctx):
    def checkValid(reaction, user):
        return ctx.message.author == user and question.id == reaction.message.id and (str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌")
    def checkRep(message):
        return message.author == ctx.message.author and ctx.message.channel == message.channel
    emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    chan = []
    question = await ctx.send("Merci d'envoyer l'ID des catégories que vous souhaitez utiliser pour cette configuration. \n Utiliser `stop` pour valider la saisie et `cancel` pour annuler la commande. ")
    while True:
        channels = await bot.wait_for("message", timeout=300, check = checkRep)
        await channels.add_reaction("✅")
        if channels.content.lower() == 'stop':
            await channels.delete(delay=10)
            break
        elif channels.content.lower() == 'cancel':
            await channels.delete(delay=10)
            return
        chan.append(channels.content)
        await channels.delete(delay=10)
    if len(chan) >= 10 :
        await ctx.send ("Erreur ! Vous ne pouvez pas mettre plus de 9 catégories !", delete_after=30)
        return
    namelist=[]
    for i in range(0,len(chan)):
        number=int(chan[i])
        guild= ctx.message.guild
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
        await question.delete()
        await titre.delete()
        return
    else:
        await question.delete()
        titre_content = titre.content
    question = await ctx.send (f"Quelle couleur voulez vous utiliser ?")
    color = await bot.wait_for("message", timeout=300, check=checkRep)
    col = color.content
    if (col.find ("#") == -1) and (col != "stop") and (col != 0):
        await ctx.send (f"Erreur ! Vous avez oublié le # !", delete_after=30)
        await color.delete()
        await question.delete()
        return
    elif col == "stop":
        await ctx.send ("Annulation !", delete_after=10)
        await color.delete()
        await question.delete()
        return
    elif col == 0:
        col = 0xabb1b4
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
        sql = ("INSERT INTO CATEGORY (idM ,titre, category_list, idS) VALUES (?,?,?,?)")
        id_serveur = ctx.message.guild.id
        id_message = react.id
        var = (id_message,titre_content, category_list_str, id_serveur)
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
    db = sqlite3.connect("owlly.db", timeout=3000)
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
    def checkRep(message):
        return msg.author == payload.user_id and payload.message.channel_id == msg.channel
    if (len (msg.embeds) != 0):
        titre = msg.embeds[0].title
        if (serv_here in serv_ticket) or (serv_here in serv_cat):
            emoji_cat = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
            sql = "SELECT emote FROM TICKET WHERE idS = ?"
            c.execute(sql, (serv_here,))
            emoji_ticket=c.fetchall()
            emoji_ticket=list(sum(emoji_ticket,()))
            sql = "SELECT type, channel FROM TICKET WHERE idS = ?"
            c.execute(sql, (serv_here,))
            appart=c.fetchall()
            appartDict={}
            action = str(payload.emoji.name)
            typecreation = "stop"
            chan_create = "stop"
            user = bot.get_user(payload.user_id)
            if not user.bot :
                await msg.remove_reaction(action,user)
            for i in range (0, len(appart)):
                extra={appart[i][0] : appart[i][1]}
                appartDict.update(extra)
            sql = "SELECT * FROM CATEGORY WHERE idS = ?"
            c.execute(sql, (serv_here,))
            room = c.fetchall()
            roomDict={}
            for i in range (0, len(room)):
                extra={room[i][0] : room[i][1]}
                roomDict.update(extra)
            if action in emoji_ticket:
                for k, v in appartDict.items():
                    if k == titre:
                        chan_create = int(v)
                        typecreation = "True"
            else:
                for k, v in roomDict.items():
                    if k == titre:
                        for i in range(0,(len(emoji_cat))):
                            chan_create=int(v[i])
                            typecreation = "False"
            if typecreation == "True":
                # Création d'un ticket
                sql = "SELECT num, modulo, limitation FROM TICKET WHERE (idS = ? AND type = ?)"
                c.execute(sql, (serv_here,titre,))
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
                sql = "UPDATE TICKET SET num = ? WHERE (idS = ? AND type = ?)"
                var = (nb, serv_here, titre)
                c.execute(sql, var)
                sql = "INSERT INTO AUTHOR (channel_id, userID, idS) VALUES (?,?,?)"
                var = (new_chan.id, payload.user_id, serv_here)
                c.execute(sql, var)
                db.commit()
                c.close()
                db.close()

            elif typecreation == "False" :
                question = channel.send(f"Catégorie {chan_create} sélectionnée. Merci d'indiquer le nom du channel.")
                chan_rep = await bot.wait_for("message", timeout=300, check=checkRep)
                await question.delete()
                chan_name = chan_rep.content
                if chan_name == "stop":
                    channel.send("Annulation de la création.", delete_after=10)
                    await chan_rep.delete()
                    return
                channel.send(f"Création du channel {chan_name} dans {chan_create}.", delete_after=30)
                await chan_rep.delete()
                category = bot.get_channel(chan_create)
                await category.create_text_channel(chan_name)

bot.run(token)
