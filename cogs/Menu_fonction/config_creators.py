import discord
from discord.ext import commands, tasks
from discord.utils import get
from typing import Optional
import sqlite3
import re
from discord import Colour
from discord.ext.commands import ColourConverter,CommandError
import unidecode as uni

async def convertColor(ctx, color: Optional[discord.Color] = None):
    if color is None:
        return Colour.blurple()
    else:
        colur = await ColourConverter.convert(ctx, color)
        return colur

def checkImg(ctx, img):
    pattern = 'http(s?):\/\/www\.(.*)(png|jpg|jpeg|gif|gifv|)'
    result = re.match(pattern, img)
    if result:
        return (result.group(0))
    else:
        return "error"


async def search_cat_name(ctx, name, bot):
    emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    def checkValid(reaction, user):
        return ctx.message.author == user and info.id == reaction.message.id and str(reaction.emoji) in emoji
    cat_list = []
    cat_uni = []
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
                name = cat
        name = get(ctx.message.guild.categories, name=name)
        number = name.id
        return number
    elif lg > 1 and lg < 10:
        search_name = []
        for i in range(0, lg):
            for cat in cat_list:
                if search[i] == uni.unidecode(cat):
                    search_name.append(cat)
                else:
                    search_name.append(search[i])
            phrase = f"{emoji[i]} : {search_name[i]}"
            search_list.append(phrase)
        search_question = "\n".join(search_list)
        info = await ctx.send(f"Plusieurs catégories correspondent à ce nom. Pour choisir celle que vous souhaitez, cliquez sur le numéro correspondant :\n {search_question}")
        for i in range(0, lg):
            await info.add_reaction(emoji[i])
        select, user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
        for i in range(0, lg):
            if str(select) == str(emoji[i]):
                name = search_name[i]
                mot = search_name[i]
        name = get(ctx.message.guild.categories, name=name)
        number = name.id
        await info.delete()
        await ctx.send(f"Catégorie : {mot} ✅ \n > Vous pouvez continuer l'inscription des channels. ", delete_after=30)
        return number
    else:
        await ctx.send("Il y a trop de correspondance ! Merci de recommencer la commande.", delete_after=30)
        return


async def create_ticket(self,ctx, bot):
    def checkValid(reaction, user):
        return ctx.message.author == user and q.id == reaction.message.id and (
            str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌")

    def checkRep(message):
        return message.author == ctx.message.author and ctx.message.channel == message.channel
    
    guild = ctx.message.guild
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    q = await ctx.send(f"Quel est le titre de l'embed ?")
    rep = await bot.wait_for("message", timeout=300, check=checkRep)
    typeM = rep.content
    if typeM.lower() == "stop":
        await ctx.send("Annulation !", delete_after=10)
        await rep.delete()
        await q.delete()
        return
    else:
        await rep.delete()
    await q.edit(content=f"Quelle est sa description ?")
    rep = await bot.wait_for("message", timeout=300, check=checkRep)
    desc = rep.content
    if rep.content.lower() == "stop":
        await ctx.send("Annulation !", delete_after=30)
        await rep.delete()
        await q.delete()
        return
    await rep.delete()
    await q.edit(content="Dans quelle catégorie voulez-vous créer vos tickets ? Rappel : Seul un modérateur pourra les supprimer, car ce sont des tickets permanent.\n Vous pouvez utiliser le nom ou l'ID de la catégorie !")
    rep = await bot.wait_for("message", timeout=300, check=checkRep)
    ticket_chan_content = rep.content
    cat_name = "none"
    if ticket_chan_content.lower() == "stop":
        await ctx.send("Annulation !", delete_after=10)
        await q.delete()
        await rep.delete()
        return
    else:
        await rep.delete()
        if ticket_chan_content.isnumeric():
            ticket_chan_content = int(ticket_chan_content)
            cat_name = get(guild.categories, id=ticket_chan_content)
            if cat_name == "None" or cat_name is None:
                await ctx.send("Erreur : Cette catégorie n'existe pas !", delete_after=30)
                await q.delete()
                return
        else:
            ticket_chan_content = await search_cat_name(ctx, ticket_chan_content, bot)
            if ticket_chan_content == 12:
                await ctx.send("Aucune catégorie portant un nom similaire existe, vérifier votre frappe.", delete_after=30)
                await q.delete()
                return
            else:
                cat_name = get(guild.categories, id=ticket_chan_content)
    await q.edit(content=f"Votre ticket sera créée dans {cat_name}.\n\nQuelle couleur voulez vous utiliser ? \n 0 donne une couleur aléatoire.")
    rep = await bot.wait_for("message", timeout=300, check=checkRep)
    col = rep.content
    if col.lower() == "stop":
        await ctx.send("Annulation !", delete_after=30)
        await q.delete()
        await rep.delete()
        return
    elif col == "0":
        col = Colour.random()
    else:
        try:
            col = await ColourConverter.convert(self,ctx=ctx, argument=rep.content)
        except CommandError:
            col = Colour.blurple()
    await rep.delete()
    await q.edit(content="Voulez-vous ajouter une image ?")
    await q.add_reaction("✅")
    await q.add_reaction("❌")
    reaction, user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
    if reaction.emoji == "✅":
        await q.clear_reactions()
        await q.edit(content="Merci d'envoyer l'image. \n**⚡ ATTENTION : Le message sera supprimé après la configuration, vous devez donc utiliser un lien permanent (hébergement sur un autre channel/serveur, imgur, lien google...)**")
        rep = await bot.wait_for("message", timeout=300, check=checkRep)
        img_content = rep.content
        if img_content.lower() == "stop":
            await ctx.send("Annulation !", delete_after=10)
            await q.delete()
            await rep.delete()
            return
        else:
            img_content = checkImg(ctx, img_content)
            if img_content == "Error":
                await ctx.send("Erreur ! Votre lien n'est pas une image valide.", delete_after=60)
                await q.delete()
                await rep.delete()
                return
            else:
                await rep.delete()
    else:
        await q.clear_reactions()
        img_content = "none"
    await q.edit(content="Voulez-vous donner la possibilité de nommer librement les channels ?")
    await q.add_reaction("✅")
    await q.add_reaction("❌")
    reaction, user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
    if reaction.emoji == "✅":
        await q.clear_reactions()
        name_para = "1"
        phrase_para = "Nom libre"
        nb_dep_content="Aucun"
        limit_content=0
        mod_content=0
    else:
        name_para = "2"
        await q.clear_reactions()
        await q.edit(content="Dans ce cas, voulez-vous avoir une construction particulière du nom du channel ? Elle sera toujours suivi du nom du créateur.")
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
        if reaction.emoji == "✅":
            await q.clear_reactions()
            await q.edit(content="Quel est le nom que vous voulez utiliser ?")
            rep = await bot.wait_for("message", timeout=300, check=checkRep)
            name_para = rep.content
            phrase_para = name_para
        else:
            phrase_para = "Nom du personnage"
        await q.edit(content="Voulez-vous que les tickets soient comptés ?")
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
        limit_content = 0
        mod_content = 0
        nb_dep_content = "Aucun"
        if reaction.emoji == "✅":
            await q.edit(content="Voulez-vous fixer un nombre de départ ?")
            await q.add_reaction("✅")
            await q.add_reaction("❌")
            reaction, user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
            if reaction.emoji == "✅":
                await q.clear_reactions()
                await q.edit(content="Merci d'indiquer le nombre de départ.")
                rep = await bot.wait_for("message", timeout=300, check=checkRep)
                if rep.content.lower() == "stop":
                    await q.delete()
                    await ctx.send("Annulation !", delete_after=10)
                    await rep.delete()
                    return
                else:
                    nb_dep_content = str(rep.content)
                    await rep.delete()
            else:
                nb_dep_content = "0"
            await q.edit(content="Voulez-vous fixer une limite ? C'est à dire que le ticket va se reset après ce nombre.")
            await q.add_reaction("✅")
            await q.add_reaction("❌")
            reaction, user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
            if reaction.emoji == "✅":
                await q.clear_reactions()
                await q.edit(content="Merci d'indiquer la limite.")
                rep = await bot.wait_for("message", timeout=300, check=checkRep)
                limit=rep.content
                if limit.lower() == "stop" or limit.lower()=="cancel" or limit.lower() is not limit.isnumeric():
                    await ctx.send("Annulation !", delete_after=10)
                    await q.delete()
                    await rep.delete()
                    return
                else:
                    await q.clear_reactions()
                    limit_content = int(limit)
                    await rep.delete()
                    mod_content = 0
                    await q.edit(content="Voulez-vous, après la limite, augmenter d'un certain nombre le numéro ?")
                    await q.add_reaction("✅")
                    await q.add_reaction("❌")
                    reaction, user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
                    if reaction.emoji == "✅":
                        await q.clear_reactions()
                        await q.edit(content="Quel est donc ce nombre ?")
                        rep = await bot.wait_for("message", timeout=300, check=checkRep)
                        if rep.content.lower() == "stop" or rep.content.lower() == "cancel" or rep.content.lower() is not rep.isnumeric():
                            await ctx.send("Annulation !", delete_after=10)
                            await rep.delete()
                            await q.delete()
                            return
                        elif rep.content.isnumeric():
                            mod_content = int(rep.content)
                            await rep.delete()
                    else:
                        await q.clear_reactions()
                        mod_content=0
            else:
                limit_content = 0
                mod_content = 0
                await q.clear_reactions()
        else:
            await q.clear_reactions()
    guild = ctx.message.guild
    await q.edit(content=f"Vos paramètres sont : \n Titre : {typeM} \n Numéro de départ : {nb_dep_content} \n Intervalle entre les nombres (on se comprend, j'espère) : {mod_content} (0 => Pas d'intervalle) \n Limite : {limit_content} (0 => Pas de limite) \n Catégorie : {cat_name}.\n Nom par défaut : {phrase_para}\n Confirmez-vous ces paramètres ?")
    await q.add_reaction("✅")
    await q.add_reaction("❌")
    reaction, user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
    if reaction.emoji == "✅":
        await q.clear_reactions()
        embed = discord.Embed(title=typeM,description=desc, color=col)
        if img_content != "none":
            embed.set_image(url=img_content)
        await q.edit(content="Vous pouvez choisir l'émoji de réaction en réagissant à ce message. Il sera sauvegardé et mis sur l'embed. Par défaut, l'émoji est : 🗒")
        symb, user = await bot.wait_for("reaction_add", timeout=300)
        if symb.custom_emoji:
            if symb.emoji in guild.emojis:
                symbole = str(symb.emoji)
            else:
                symbole = "🗒"
        elif symb.emoji != "🗒":
            symbole = str(symb.emoji)
        else:
            symbole = "🗒"
        await q.delete()
        react = await ctx.send(embed=embed)
        await react.add_reaction(symbole)
        sql = "INSERT INTO TICKET (idM, channelM, channel, num, modulo, limitation, emote, idS, name_auto) VALUES (?, ?, ?, ?, ?, ?, ?, ?,?)"
        id_serveur = ctx.message.guild.id
        id_message = react.id
        chanM = ctx.channel.id
        var = (id_message, chanM, ticket_chan_content, nb_dep_content,
               mod_content, limit_content, symbole, id_serveur, name_para)
        c.execute(sql, var)
        db.commit()
        c.close()
        db.close()
    else:
        await ctx.send("Annulation !", delete_after=30)
        await q.delete()
        return


async def create_category(self,ctx, bot):
    def checkValid(reaction, user):
        return ctx.message.author == user and q.id == reaction.message.id and (str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌")

    def checkRep(message):
        return message.author == ctx.message.author and ctx.message.channel == message.channel
    emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    chan = []
    q = await ctx.send(
        "Merci d'envoyer l'ID des catégories (ou leurs noms) que vous souhaitez utiliser pour cette configuration. \n Utiliser `stop` pour valider la saisie et `cancel` pour annuler la commande. "
    )
    while True:
        channels = await bot.wait_for("message", timeout=300, check=checkRep)
        chan_search = channels.content
        if chan_search.lower() == 'stop':
            await ctx.send("Validation en cours !", delete_after=5)
            await channels.delete()
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
        await ctx.send("Erreur ! Vous ne pouvez pas mettre plus de 9 catégories !", delete_after=30)
        await q.delete()
        return
    namelist = []
    guild = ctx.message.guild
    for i in range(0, len(chan)):
        number = int(chan[i])
        cat = get(guild.categories, id=number)
        phrase = f"{emoji[i]} : {cat}"
        namelist.append(phrase)
    msg = "\n".join(namelist)
    await q.delete()
    parameters_save = f"Votre channel sera donc créé dans une des catégories suivantes:\n{msg}\n\nLe choix final de la catégories se fait lors des réactions."
    q = await ctx.send(f"{parameters_save}\nVoulez-vous pouvoir nommer librement les channels créées ?")
    await q.add_reaction("✅")
    await q.add_reaction("❌")
    reaction, user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
    name_para = 0
    if reaction.emoji == "✅":
        name_para = 1
    else:
        name_para = 0
    await q.clear_reactions()
    await q.edit(content="Quel est le titre de l'embed ?")
    rep = await bot.wait_for("message", timeout=300, check=checkRep)
    if rep.content.lower() == "stop":
        await ctx.send("Annulation !", delete_after=30)
        await q.delete()
        await rep.delete()
        return
    else:
        titre = rep.content
        await rep.add_reaction("✅")
        await rep.delete(delay=5)
    await q.edit(content="Quelle couleur voulez vous utiliser ?\n 0 donnera une couleur aléatoire")
    rep = await bot.wait_for("message", timeout=300, check=checkRep)
    col = rep.content
    if col.lower() == "stop":
        await ctx.send("Annulation !", delete_after=30)
        await q.delete()
        await rep.delete()
        return
    elif col == "0":
        col = Colour.random()
        await rep.delete()
    else:
        try:
            col = await ColourConverter.convert(self,ctx, col)
        except CommandError:
            col = Colour.random()
        await rep.delete()
    await q.edit(content="Voulez-vous utiliser une image ?")
    await q.add_reaction("✅")
    await q.add_reaction("❌")
    reaction, user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
    if reaction.emoji == "✅":
        await q.clear_reactions()
        await q.edit(content="Merci d'envoyer l'image. \n**⚡ ATTENTION : Le message sera supprimé après l'envoi, vous devez donc utiliser un lien permanent. (hébergement sur un autre channel/serveur, imgur, lien google...)**"
                     )
        rep = await bot.wait_for("message", timeout=300, check=checkRep)
        img_content = rep.content
        if img_content.lower() == "stop":
            await ctx.send("Annulation !", delete_after=10)
            await q.delete()
            await rep.delete()
            return
        else:
            img_content = checkImg(ctx, img_content)
            if img_content == "Error":
                await ctx.send("Erreur ! Votre lien n'est pas une image valide.", delete_after=60)
                await q.delete()
                await rep.delete()
                return
            else:
                await rep.delete()
    else:
        await q.clear_reactions()
        img_content = "none"
    embed = discord.Embed(title=titre, description=msg, color=col)
    if img_content != "none":
        embed.set_image(url=img_content)
    await q.edit(content=f"Les catégories dans lequel vous pourrez créer des canaux seront : {parameters_save} \n Validez-vous ses paramètres ?")
    await q.add_reaction("✅")
    await q.add_reaction("❌")
    reaction, user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
    if reaction.emoji == "✅":
        react = await ctx.send(embed=embed)
        for i in range(0, len(chan)):
            await react.add_reaction(emoji[i])
        category_list_str = ",".join(chan)
        sql = "INSERT INTO CATEGORY (idM, channelM, category_list, idS, config_name) VALUES (?,?,?,?,?)"
        id_serveur = ctx.message.guild.id
        id_message = react.id
        chanM = ctx.channel.id
        var = (id_message, chanM, category_list_str, id_serveur, name_para)
        c.execute(sql, var)
        db.commit()
        c.close()
        db.close()
        await q.delete()
    else:
        await ctx.send("Annulation !", delete_after=10)
        await q.delete()
        c.close()
        db.close()
        return
