import discord
from discord.ext import commands, tasks
import sqlite3
import re
from discord.utils import get
from discord.ext.commands import CommandError
import unidecode as uni


async def search_cat_name(ctx, name, bot):
    emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

    def checkValid(reaction, user):
        return (
            ctx.message.author == user
            and info.id == reaction.message.id
            and str(reaction.emoji) in emoji
        )

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
        info = await ctx.send(
            f"Plusieurs catégories correspondent à ce nom. Pour choisir celle que vous souhaitez, cliquez sur le numéro correspondant :\n {search_question}"
        )
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
        await ctx.send(
            f"Catégorie : {mot} ✅ \n > Vous pouvez continuer l'inscription des channels. ",
            delete_after=30,
        )
        return number
    else:
        await ctx.send(
            "Il y a trop de correspondance ! Merci de recommencer la commande.",
            delete_after=30,
        )
        return

async def search_chan(ctx, chan):
    try:
        chan = await commands.TextChannelConverter().convert(ctx, chan)
        return chan
    except CommandError:
        chan = "Error"
        return chan

async def chanRp (ctx, bot):
    def checkValid(reaction, user):
        return (
            ctx.message.author == user
            and q.id == reaction.message.id
            and (str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌")
        )

    def checkRep(message):
        return message.author == ctx.message.author and ctx.message.channel == message.channel

    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    chan = []
    q = await ctx.send("Merci d'envoyer les catégories ou Channel que vous souhaitez utiliser.\n:white_small_square: `stop` : Valide la saisie\n:white_small_square: `cancel` : Annule la commande. ")
    while True:
        channels = await bot.wait_for("message", timeout=300, check=checkRep)
        chan_search = channels.content
        if chan_search.lower() == "stop":
            await ctx.send("Validation en cours !", delete_after=5)
            await channels.delete()
            break
        elif chan_search.lower() == "cancel":
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
                    check_id = bot.get_channel(chan_search)
                    if check_id is None or check_id == "None":
                        await ctx.send("Erreur ! Ce channel ou cette catégorie n'existe pas !", delete_after=30)
                        await q.delete()
                        await channels.delete()
                    else:
                        chan.append(str(chan_search))
                else: 
                    chan.append(str(chan_search))
            else:
                chan_search = await search_cat_name(ctx, chan_search, bot)
                if chan_search == 12:
                    chan_search = await search_chan(ctx, chan_search)
                    if chan_search == "Error":
                        await ctx.send("Erreur, ce channel ou cette catégorie n'existe pas.", delete_after=30)
                        await q.delete()
                        await channels.delete()
                        return
                    else:
                        chan.append(str(chan_search.id))
                else:
                    chan.append(str(chan_search))
        await channels.delete(delay=10)
    idS= ctx.guild.id
    chanRP=",".join(chan)
    sql= "UPDATE SERVEUR SET chanRP = ? WHERE idS = ?"
    var=(chanRP, idS)
    c.execute(sql, var)
    db.commit()
    c.close()
    db.close()

async def chanHRP_add(ctx, bot):
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    sql= "SELECT chanRP FROM SERVEUR WHERE idS = ?"
    c.execute(sql, (ctx.guild.id,))
    cat=c.fetchone()[0].split(",")
        
    def checkRep(message):
        return message.author == ctx.message.author and ctx.message.channel == message.channel
    q = await ctx.send("Merci de donner l'ID ou le nom du channel/catégorie que vous souhaitez rajouter.")
    rep = await bot.wait_for("message", timeout=300, check=checkRep)
    if rep.content.lower() == "stop":
       await q.delete()
       await rep.delete()
       await ctx.send("Annulation !", delete_after=30)
       return
    else:
        if rep.content.isnumeric():
            chan = int(rep.content)
            check_id = get(ctx.message.guild.categories, id=chan)
            if check_id is None or check_id == "None":
                check_id=bot.get_channel(chan)
                if check_id is None or check_id == "None":
                    await ctx.send("Erreur, ce channel ou cette catégorie n'existe pas.", delete_after=30)
                    await q.delete()
                    await rep.delete()
                else:
                  cat.append(str(chan))
            else:
                cat.append(str(chan))
        else:
            cat_search=await search_cat_name(ctx, rep.content.lower(), bot)
            if cat_search==12:
                cat_search = await search_chan(ctx, rep.content.lower())
                if cat_search == "Error":
                    await ctx.send("Erreur, ce channel ou cette catégorie n'existe pas", delete_after=30)
                    await q.delete()
                    await rep.delete()
                    return
                else:
                    cat.append(str(cat_search.id))
            else:
                cat.append(str(cat_search))
        chanRP= ",".join(cat)
        sql="UPDATE SERVEUR SET chanRP = ? WHERE idS=?"
        var=(chanRP, ctx.guild.id)
        c.execute(sql, var)
        db.commit()
        c.close()
        db.close()


async def chanHRP_rm(ctx, bot):
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    sql= "SELECT chanRP FROM SERVEUR WHERE idS = ?"
    c.execute(sql, (ctx.guild.id,))
    cat=c.fetchone()[0].split(",")
    def checkRep(message):
        return message.author == ctx.message.author and ctx.message.channel == message.channel
    q=await ctx.send("Merci de joindre l'ID/le nom du channel ou de la catégorie que vous souhaitez supprimer de la liste.")
    rep = await bot.wait_for("message", timeout=300, check=checkRep)
    if rep.content.lower() == "stop":
        await q.delete()
        await rep.delete()
        await ctx.send("Annulation !", delete_after=30)
    else:
        chan=rep.content
        if chan.isnumeric():
            chan=int(chan)
            check_id = get(ctx.message.guild.categories, id=chan)
            if check_id is None or check_id =="None":
                check_id = bot.get_channel(chan)
                if check_id is None or check_id == "None":
                    await ctx.send("Erreur, ce channel ou cette catégorie n'existe pas !", delete_after=30)
                    await q.delete()
                    await rep.delete()
                    return
            else:
                chan = await search_cat_name(ctx, rep.content.lower(), bot)
                if chan == 12:
                    chan = await search_chan(ctx, rep.content.lower())
                    if chan == "Error":
                        await ctx.send("Erreur, ce channel ou cette catégorie n'existe pas", delete_after=30)
                        await q.delete()
                        await rep.delete()
                        return
                    else:
                        chan=chan.id
        try:
            cat.remove(chan)
        except ValueError:
            await ctx.send("Cette catégorie / channel n'est pas dans la liste.",delete_after=30)
            await q.delete()
            return
        await q.edit(content="La catégorie/channel a été supprimé de la liste.")
        cat_sql=",".join(cat)
        sql="UPDATE SERVEUR SET chanRP = ? WHERE idS=?"
        var=(cat_sql, ctx.guild.id)
        c.execute(sql, var)
        db.commit()
        c.close()
        db.close()

                              
async def maxDC (ctx, bot, config):
    def checkRep(message):
        return message.author == ctx.message.author and ctx.message.channel == message.channel
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    if config != "0":
        q= await ctx.send("Quel est le nombre maximum de Personae voulez-vous autoriser pour les joueurs ?. \n `0`: illimité")
        rep = await bot.wait_for("message", timeout=300, check=checkRep)
        maxDC=rep.content.lower()
        if not maxDC.isnumeric() :
            await ctx.send("Erreur, c'est pas un nombre !\nAnnulation.", delete_after=30)
            maxDC=0
        else:
            maxDC=int(max)
    else:
        maxDC=0
    sql="UPDATE SERVEUR SET maxDC = ? WHERE idS = ?"
    idS = ctx.guild.id
    var=(maxDC, idS)
    c.execute(sql, var)
    db.commit()
    c.close()
    return
        
async def sticky(ctx, bot, sticky):
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    if sticky == "0": #false
        sql = "UPDATE SERVEUR SET sticky = ? WHERE idS = ?"
        var=(0, ctx.guild.id) 
    else:
        sql="UPDATE SERVEUR SET sticky = ? WHERE idS =?"
        var=(1, ctx.guild.id)
    c.execute(sql, var)
    db.commit()
    c.close()
    db.close()  

async def tokenHRP(ctx, bot, token):
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    if token != "0":
        token = token.replace("[text]", "(.*)/")
        token = "^/" + token + "$"
    sql="UPDATE SERVEUR SET tokenHRP = ? WHERE idS= ?"
    var=(token, ctx.guild.id)
    c.execute(sql, var)
    db.commit()
    c.close()
    db.close()

async def deleteHRP(ctx, bot, config):
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()

    def checkRep(message):
        return message.author == ctx.message.author and ctx.message.channel == message.channel
    timer = 0
    if config != "0":
        config = 1
        q = await ctx.send("Au bout de combien de temps les messages doivent-il être effacé ? Merci de mettre le temps en secondes.")
        rep = await bot.wait_for("message", timeout=300, check=checkRep)
        if rep.content.isnumeric():
            timer= int(rep.content.lower())
        else:
            await ctx.send("Erreur ! Ce n'est pas un nombre. Il n'y aura donc pas de suppression.")
            timer = 0
    else:
        config = 0
        timer = 0
    sql="UPDATE SERVEUR SET delete_HRP = ?, delay_HRP = ? WHERE idS=?"
    var=(config, timer, ctx.guild.id)
    c.execute(sql, var)
    db.commit()
    c.close()
    db.close()
    await q.delete()
    await rep.delete()
            
