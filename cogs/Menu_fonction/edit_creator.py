import discord
from discord import NotFound
from discord.ext import commands, tasks
from discord.utils import get
import sqlite3
import re
from discord import Colour
from discord.ext.commands import ColourConverter
import unidecode as uni


async def search_cat_name(ctx, name,bot):
    emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

    def checkValid(reaction, user):
        return ctx.message.author == user and q.id == reaction.message.id and str(reaction.emoji) in emoji
    cat_list = []
    cat_uni=[]
    for cat in ctx.message.guild.categories:
        cat_list.append(cat.name)
        cat_uni.append(uni.unidecode(cat.name))
    w = re.compile(f".*{uni.unidecode(name)}|{name}.*", flags=re.IGNORECASE)
    search = list(filter(w.match, cat_uni))
    search_list = []
    lg = len(search)
    if lg == 0:
        return 12
    elif lg == 1:
        name = search[0]
        for cat in cat_list:
            if name == uni.unidecode(cat):
                name=cat
        name = get(ctx.message.guild.categories, name=name)
        number = name.id
        return number
    elif lg > 1 and lg < 10:
        search_name=[]
        for i in range(0, lg):
            for cat in cat_list:
                if search[i] == uni.unidecode(cat):
                    search_name.append(cat)
                else:
                    search_name.append(search[i])
            phrase = f"{emoji[i]} : {search_name[i]}"
            search_list.append(phrase)
        search_question = "\n".join(search_list)
        q = await ctx.send(f"Plusieurs catégories correspondent à ce nom. Pour choisir celle que vous souhaitez, cliquez sur le numéro correspondant :\n {search_question}")
        for i in range(0, lg):
            await q.add_reaction(emoji[i])
        select, user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
        for i in range(0, lg):
            if str(select) == str(emoji[i]):
                name = search_name[i]
                mot = search_name[i]
        name = get(ctx.message.guild.categories, name=name)
        number = name.id
        await q.delete()
        await ctx.send(f"Catégorie : {mot} ✅ \n > Vous pouvez continuer l'inscription des channels. ", delete_after=30)
        return number
    else:
        await ctx.send("Il y a trop de correspondance ! Merci de recommencer la commande.", delete_after=30)
        return

async def editEmbed(ctx, bot, channel: discord.TextChannel, idM):
    emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    for channel in bot.get_all_channels():
        try:
            msg = await channel.get_message(idM)
        except NotFound:
            return "Error"
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    sql="SELECT category_list FROM CATEGORY WHERE idM=?"
    c.execute(sql,(idM,))
    cat_list=c.fetchone()[0]
    if cat_list is None:
        return "Error"
    cat=cat_list.split(",")
    namelist=[]
    for i in range(0,len(cat)):
        number = int(cat[i])
        cat = get(ctx.message.guild.categories, id=number)
        phrase = f"{emoji[i]} : {cat}"
        namelist.append(phrase)
    name_str = "\n".join(namelist)
    embed=discord.Embed(description=name_str)
    await msg.edit(embed=embed)
        

async def edit_ticket(ctx, idM, bot):
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    emoji = ["1️⃣", "2️⃣", "3️⃣", "✅", "❌"]

    def checkValid(reaction, user):
        return ctx.message.author == user and q.id == reaction.message.id and str(reaction.emoji) in emoji
    def checkRep(message):
        return message.author == ctx.message.author and ctx.message.channel == message.channel
    
    q = await ctx.send("Merci de choisir le paramètre à éditer :\n 1️⃣ : Nom du channel \n 2️⃣ : Numéros, modulo, limitation\n3️⃣: Catégorie de création.\n ❌ : Annulation")
    await q.add_reaction("1️⃣")
    await q.add_reaction("2️⃣")
    await q.add_reaction("3️⃣")
    await q.add_reaction("❌")
    reaction, user=await bot.wait_for("reaction_add", timeout=300, check=checkValid)
    if reaction.emoji == "2️⃣":
        await q.clear_reactions()
        sql = "SELECT name_auto FROM TICKET WHERE idM=?"
        c.execute(sql, (int(idM),))
        name = c.fetchone()[0]
        if name == "1":
            msg="\n⚠ Le nom est actuellement libre. En modifiant la numérotation, vous allez changer aussi la possibilité de nommer le channel à la création ! Le nom prendra la construction par défaut : [Numéro] [Nom du créateur]"
        else:
            msg=""
        await q.edit(content=f"Merci de choisir le paramètre à éditer : 1️⃣ : Numéro de départ, ou en cours.\n2️⃣ : Augmentation après la limite. \n3️⃣: Limite{msg}")
        await q.add_reaction("1️⃣")
        await q.add_reaction("2️⃣")
        await q.add_reaction("3️⃣")
        reaction, user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
        if reaction.emoji == "1️⃣":
            await q.clear_reactions()
            sql="SELECT num FROM TICKET WHERE idM=?"
            c.execute(sql, (int(idM),))
            num=c.fetchone()[0]
            if num == "Aucun":
                msg = "Actuellement, il n'y a pas de nombre de départ. Par-quoi voulez-vous le changer ?\n `0`: Aucun changement."
            else:
                msg = f"Actuellement, le numéro est {num}.  Par-quoi voulez-vous le changer ?\n `0`: Suppression de la numérotation."
            await q.edit(content=msg)
            rep=await bot.wait_for("message", timeout=300, check=checkRep)
            if rep.content.lower() == "stop":
                await ctx.send("Annulation !", delete_after=30)
                await q.delete()
                await rep.delete()
                return
            else:
                if rep.content == "0":
                    num = "Aucun"
                else:
                    num = str(rep.content)
                await rep.add_reaction('✅')
                await rep.delete(delay=30)
                sql="UPDATE TICKET SET num=? WHERE idM=?"
                var=(num, idM)
                c.execute(sql, var)
                if name == "1":
                    sql="UPDATE TICKET SET name_auto=? WHERE idM=?"
                    name="2"
                    var=(name, idM)
                    c.execute(sql, var)
                await q.edit(content="Paramètre changé.", delete_after=30)
        elif reaction.emoji=="2️⃣":
            await q.clear_reactions()
            sql = "SELECT modulo FROM TICKET WHERE idM=?"
            c.execute(sql, (int(idM),))
            modulo = c.fetchone()[0]
            if modulo == 0:
                msg = "Actuellement, le comptage n'est pas augmenté après la limite. Par-quoi voulez-vous changer ce paramètre ?\n `0` : Aucun changement.\n En cas de fixation de modulo, une limite sera fixée à 100."
            else:
                msg = f"Actuellement, l'augmentation est de : {modulo}.Par-quoi voulez-vous changer ce paramètre ? \n `0` : Suppression."
            rep = await bot.wait_for("message", timeout=300, check=checkRep)
            if rep.content.lower()=="stop":
                await ctx.send("Annulation !", delete_after=30)
                await q.delete()
                await rep.delete()
                return
            elif rep.content.isnumeric():
                modulo = int(rep.content)
                await rep.add_reaction('✅')
                await rep.delete(delay=30)
                sql = "UPDATE TICKET SET modulo=? WHERE idM=?"
                var = (modulo, idM)
                c.execute(sql, var)
                sql="SELECT num FROM TICKET WHERE idM=?"
                c.execute(sql,(idM,))
                nb=c.fetchone()[0]
                if not nb.isnumeric():
                    nb="0"
                    sql="UPDATE TICKET SET num=? WHERE idM=?"
                    var=(nb, idM)
                    c.execute(sql,var)
                sql="SELECT limitation FROM TICKET WHERE idM=?"
                c.execute(sql,(idM,))
                limit=c.fetchone()[0]
                if int(limit) == 0 and modulo != 0:
                    limit=100
                    sql="UPDATE TICKET SET limitation=? WHERE idM=?"
                    var=(limit, idM)
                    c.execute(sql,var)
                if name == "1":
                    sql="UPDATE TICKET SET name_auto=? WHERE idM=?"
                    name="2"
                    var=(name, idM)
                    c.execute(sql, var)
                await q.edit(content="Paramètre changé.", delete_after=30)
            else:
                await ctx.send("Ce n'est pas un nombre !\nAnnulation", delete_after=30)
                await q.delete()
                await rep.delete()
                return
        elif reaction.emoji=="3️⃣":
            await q.clear_reactions()
            sql = "SELECT limitation FROM TICKET WHERE idM=?"
            c.execute(sql, (int(idM),))
            limitation = c.fetchone()[0]
            if limitation == 0:
                msg = "Actuellement, il n'y a pas de limite. Par-quoi voulez-vous la changer ?\n `0`: Aucun changement."
            else:
                msg = f"Actuellement, la limite est : {limitation}.  Par-quoi voulez-vous la changer ?\n `0`: Suppression de la limite."
            await q.edit(content=msg)
            rep = await bot.wait_for("message", timeout=300, check=checkRep)
            if rep.content.lower() == "stop":
                await ctx.send("Annulation !", delete_after=30)
                await q.delete()
                await rep.delete()
                return
            elif rep.content.islimitationeric():
                limitation = int(rep.content)
                await rep.add_reaction('✅')
                await rep.delete(delay=30)
                sql = "UPDATE TICKET SET limitation=? WHERE idM=?"
                var = (limitation, idM)
                c.execute(sql, var)
                if name == "1":
                    sql="UPDATE TICKET SET name_auto=? WHERE idM=?"
                    name="2"
                    var=(name, idM)
                    c.execute(sql, var)
                await q.edit(content="Paramètre changé.", delete_after=30)
            else:
                await ctx.send("Ce n'est pas un nombre !\nAnnulation", delete_after=30)
                await q.delete()
                await rep.delete()
                return
    elif reaction.emoji == "1️⃣":
        await q.clear_reactions()
        sql="SELECT name_auto FROM TICKET WHERE idM=?"
        c.execute(sql, (int(idM),))
        name=c.fetchone()[0]
        if name == "1":
            msg="Actuellement, le nom est libre. Par-quoi voulez-vous changer ce paramètre ?\n `1`: Ne pas changer\n`2`: Nom du personnage."
        elif name=="2":
            msg="Actuellement, le nom est basé sur le nom du personnage.\n`1`:Nom libre\n`2`: Ne pas changer."
        else:
            msg="Actuellement, le nom est : {name}. Par-quoi voulez-vous changer ce paramètre ?\n`1`: Nom libre.\n`2`: Nom du personnage."
        await q.edit(content=msg)
        rep = await bot.wait_for("message", timeout=300, check=checkRep)
        if rep.lower() == "stop":
            await ctx.send("Annulation !", delete_after=30)
            await q.delete()
            await rep.delete()
            return
        else:
            name=rep.content
            sql="UPDATE TICKET SET name_auto=? WHERE idM=?"
            var=(name, idM)
            c.execute(sql, var)
            await q.edit(content="Paramètre changé.", delete_after=30)
    elif reaction.emoji == "3️⃣":
        await q.clear_reactions()
        await q.edit(content="De la même manière dont vous l'avez enregistré, vous pouvez indiquer un nom, ou un ID de catégorie.")
        rep=await bot.wait_for("message", timeout=300, check=checkRep)
        if rep.content.lower() == "stop":
            await q.delete()
            await rep.delete()
            await ctx.send("Annulation.", delete_after=30)
            return
        else:
            ticket=rep.content
            await rep.delete()
            if ticket.isnumeric():
                ticket=int(ticket)
                cat_name=get(ctx.message.guild.categories, id=ticket)
                if cat_name is None :
                    await ctx.send("Erreur ! Cette catégorie n'existe pas.", delete_after=30)
                    await q.delete()
                    return
            else:
                ticket=rep.content
                ticket=await search_cat_name(ctx, ticket, bot)
                if ticket == 12:
                    await ctx.send("Aucune catégorie portant un nom similaire existe, vérifier votre frappe.", delete_after=30)
                    await q.delete()
                    return
                else:
                    cat_name = get(ctx.message.guild.categories, id=ticket)
        await q.edit(content=f"La catégorie est maintenant {cat_name}.")
        sql="UPDATE TICKET SET channel = ? WHERE idM=?"
        var=(int(ticket), idM)
        c.execute(sql, var)
    else:
        await q.delete()
        await ctx.send("Annulation", delete_after=30)
        return
    db.commit()
    c.close()
    db.close()
    return

async def edit_category (ctx, idM, bot):
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    emoji = ["1️⃣", "2️⃣", "3️⃣", "✅", "❌"]

    def checkValid(reaction, user):
        return ctx.message.author == user and q.id == reaction.message.id and str(reaction.emoji) in emoji
    def checkRep(message):
        return message.author == ctx.message.author and ctx.message.channel == message.channel
    q = await ctx.send("Merci de choisir le paramètre à éditer :\n 1️⃣ : Nom du Channel \n 2️⃣ : Liste des catégories \n ❌ : Annulation")
    await q.add_reaction("1️⃣")
    await q.add_reaction("2️⃣")
    await q.add_reaction("❌")
    reaction, user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
    if reaction.emoji == "1️⃣":
        await q.clear_reactions()
        sql="SELECT config_name FROM CATEGORY WHERE idM=?"
        c.execute(sql,(idM,))
        config=c.fetchone()[0]
        if config == 1:
            await q.edit(content="Actuellement, vous permettez le nommage libre du channel. Voulez-vous changer ce paramètre ?")
            await q.add_reaction("✅")
            await q.add_reaction("❌")
            reaction, user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
            if reaction.emoji == "✅":
                await q.clear_reactions()
                config=0
            else:
                await q.clear_reactions()
                config=1
        elif reaction.emoji == "2️⃣":
            await q.clear_reactions()
            await q.edit (content="Actuellement, le nom des channel est donné par le nom du personnage. Voulez-vous changer ce paramètre ?")
            await q.add_reaction("✅")
            await q.add_reaction("❌")
            reaction, user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
            if reaction.emoji =="✅":
                config=1
                await q.clear_reactions()
            else:
                config=0
                await q.clear_reactions()
        sql="UPDATE CATEGORY SET config_name = ? WHERE idM=?"
        var=(config, idM)
        c.execute(sql, var)
    elif reaction.emoji=="2️⃣":
        await q.clear_reactions()
        sql="SELECT category_list FROM CATEGORY WHERE idM=?"
        c.execute(sql,(idM,))
        cat=c.fetchone()[0]
        cat=cat.split(",")
        cat_list=[]
        for i in cat:
            name=get(ctx.message.guild.categories, id=i)
            cat_list.append(name)
        cat_str="\n ◽".join(cat_list)
        await q.edit(content="Actuellement, la liste des catégories est : \n {cat_str}.\n\n 1️⃣ : Supprimer une catégorie \n 2️⃣ : Ajouter une catégorie\n 3️⃣: Recommencer l'enregistrement complet. \n ❌: Annulation")
        await q.add_reaction("1️⃣")
        await q.add_reaction("2️⃣")
        await q.add_reaction("3️⃣")
        await q.add_reaction("❌")
        reaction, user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
        if reaction.emoji == "1️⃣":
            await q.clear_reactions()
            await q.edit(content="Merci de donner l'ID ou le nom de la catégorie que vous voulez modifier.")
            rep = await bot.wait_for("message", timeout=300, check=checkRep)
            if rep.content.lower() == "stop":
                await q.delete()
                await rep.delete()
                await ctx.send("Annulation !", delete_after=30)
                return
            else:
                if rep.content.isnumeric():
                    chan=int(rep.content)
                    cat_name=get(ctx.message.guild.categories, id=chan)
                    if cat_name is None or cat_name == "None":
                        await ctx.send("Erreur ! Cette catégorie n'existe pas.", delete_after=30)
                        await q.delete()
                        await rep.delete()
                        return
                else:
                    chan=await search_cat_name(ctx, rep.content, bot)
                    if chan == 12:
                        await ctx.send("Aucune catégorie portant un nom similaire existe, vérifier votre frappe.", delete_after=30)
                        await q.delete()
                        await rep.delete()
                        return
                    else:
                        cat_name=get(ctx.message.guild.categories, id=chan)
            await rep.delete()
            await q.edit(content="{cat_name} sera ajouté à la liste.")
            cat.append(chan)
            cat_sql=",".join(cat)
            sql="UPDATE CATEGORY SET category_list = ? WHERE idM=?"
            var=(cat_sql,idM)
            c.execute(sql,var)
        elif reaction.emoji == "2️⃣":
            await q.clear_reactions()
            await q.edit(content="Merci de joindre l'ID ou le nom de la catégorie que vous voulez supprimer.")
            rep=await bot.wait_for("message", timeout=300, check=checkRep)
            if rep.content.lower() =="stop":
                await q.delete()
                await rep.delete()
                await ctx.send("Annulation", delete_after=30)
            else:
                chan=rep.content
                if chan.isnumeric():
                    chan=int(chan)
                    cat_name = get(ctx.message.guild.categories, id=chan)
                    if cat_name is None or cat_name=="None":
                        await ctx.send("Erreur ! Cette catégorie n'existe pas.", delete_after=30)
                        await q.delete()
                        await rep.delete()
                        return
                else:
                    chan = await search_cat_name(ctx, chan, bot)
                    if chan == 12:
                        await ctx.send("Aucune catégorie portant un nom similaire existe, vérifier votre frappe.", delete_after=30)
                        await q.delete()
                        await rep.delete()
                        return
                    else:
                        cat_name = get(ctx.message.guild.categories, id=chan)
            await rep.delete()
            try:
                cat.remove(chan)
            except ValueError:
                await ctx.send("Cette catégorie n'existe pas dans la liste.", delete_after=30)
                await q.delete()
                return
            await q.edit(content="La catégorie {cat_name} a été supprimé de la liste.")
            cat_sql=",".join(cat)
            sql="UPDATE CATEGORY SET category_list = ? WHERE idM=?"
            var=(cat_sql,idM)
            c.execute(sql,var)    
        elif reaction.emoji=="3️⃣":
            chan=[]
            await q.edit(content="Début de l'enregistrement des channels. Vous pouvez joindre un ID ou un nom de catégorie.")
            while True:
                channels = await bot.wait_for("message", timeout=300, check=checkRep)
                chan_search = channels.content
                if chan_search.lower() == 'stop':
                    await ctx.send("Validation en cours !", delete_after=5)
                    break
                elif chan_search.lower() == 'cancel':
                    await channels.delete()
                    await ctx.send("Annulation !", delete_after=30)
                    await q.delete()
                    return
                else:
                    await channels.add_reaction("✅")
                    if chan_search.isnumeric():
                        chan_search = int(chan_search)
                        check_id = get(ctx.message.guild.categories, id=chan_search)
                        if check_id is None or check_id == "None":
                            await ctx.send("Erreur : Cette catégorie n'existe pas !", delete_after=30)
                            await q.delete()
                            await channels.delete()
                        else:
                            chan.append(str(chan_search))
                    else:
                        chan_search = await search_cat_name(ctx, chan_search, bot)
                        if chan_search == 12:
                            await ctx.send("Aucune catégorie portant un nom similaire existe, vérifier votre frappe.", delete_after=30)
                            await q.delete()
                            await channels.delete()
                            return
                        else:
                            chan.append(str(chan_search))
                await channels.delete(delay=10)
            if len(chan) >= 10:
                await ctx.send("Erreur ! Vous ne pouvez pas mettre plus de 9 catégories.", delete_after=30)
                await q.delete()
                return
            namelist=[]
            guild=ctx.message.guild
            for i in range(0, len(chan)):
                number = int(chan[i])
                cat = get(guild.categories, id=number)
                phrase = f"{emoji[i]} : {cat}"
                namelist.append(phrase)
            msg = "\n".join(namelist)
            await q.delete()
            parameters_save = f"Votre channel sera donc créé dans une des catégories suivantes:\n{msg}\n\nLe choix final de la catégories se fait lors des réactions."
            q = await ctx.send(f"Vos channels seront enregistré dans :{parameters_save}\n")
            chan=",".join(chan)
            sql="UPDATE CATEGORY SET category_list = ? WHERE idM=?"
            var=(chan,idM)
            c.execute(sql, var)
        else:
            await q.delete()
            await ctx.send("Annulation !", delete_after=30)
            return
    else:
        await q.delete()
        await ctx.send("Annulation !", delete_after=30)
        return
    db.commit()
    c.close()
    db.close()
