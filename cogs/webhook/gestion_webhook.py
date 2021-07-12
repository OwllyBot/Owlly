import discord
import sqlite3
import re
from discord.ext import commands
import pyimgur
import os
import uuid

CLIENT_ID = os.environ.get("CLIENT_ID")
im = pyimgur.Imgur(CLIENT_ID)


def number_check(ctx):
    db = sqlite3.connect("src/owlly.db", timeout=3000)
    c = db.cursor()
    sql = "SELECT maxDC FROM SERVEUR WHERE idS = ?"
    c.execute(sql, (ctx.guild.id,))
    maxDC = c.fetchone()
    if maxDC is None:
        maxDC = 0
    else:
        maxDC = maxDC[0]
    sql = "SELECT idDC FROM DC WHERE( idS = ? AND idU = ?)"
    c.execute(sql, (ctx.guild.id, ctx.message.author.id))
    list_perso = c.fetchall()
    c.close()
    db.close()
    if ctx.message.author.guild_permissions.manage_nicknames:
        maxDC = 0
    if maxDC != -1:
        if list_perso is not None:
            number = len(list_perso)
            if maxDC != 0:
                if number >= maxDC:
                    return "Error"
                else:
                    return "ok"
            else:
                return "ok"
        else:
            return "ok"
    else:
        return "inactive"


def name_check(ctx, name):
    db = sqlite3.connect("src/owlly.db", timeout=3000)
    c = db.cursor()
    sql = "SELECT * FROM DC WHERE idS=? AND idU=? AND Nom=?"
    var = (ctx.guild.id, ctx.message.author.id, name)
    c.execute(sql, var)
    check = c.fetchall()
    c.close()
    db.close()
    if check is None or len(check) == 0:
        return "ok"
    else:
        return "error"


def name_persona(ctx, nom, id_Persona):
    db = sqlite3.connect("src/owlly.db", timeout=3000)
    c = db.cursor()
    # Tag name
    sql = "SELECT tag FROM SERVEUR WHERE idS=?"
    c.execute(sql, (ctx.guild.id,))
    tag = c.fetchone()
    c.close()
    db.close()
    if tag is None:
        return nom
    else:
        tag = tag[0]
        if tag == "0":
            return nom
        else:
            tag = tag.replace("@user", ctx.message.author.name)
            tag = tag.replace("@server", ctx.guild.name)
            tag = tag.replace("@persona", id_Persona)
            if ">" in tag:
                # Avant le nom
                name = tag + " " + nom
            elif "<" in tag:  # Après le nom
                name = nom + " " + tag
        return name


async def image_persona(ctx, bot, image):
    def checkRep(message):
        return (
            message.author == ctx.message.author
            and ctx.message.channel == message.channel
        )

    image_url = image.content()
    if image.content.lower() == "stop" or image.content.lower() == "cancel":
        await ctx.send("Annulation !", delete_after=30)
        return "stop"
    else:
        while not (
            (image.attachments)
            or ("discordapp" in image_url)
            or (any(x in image_url for x in ["jpg", "png", "jpeg", "gif"]))
        ):
            await ctx.send(f"Erreur, vous devez envoyer une image")
            image = await bot.wait_for("message", timeout=300, check=checkRep)
            image_url = image.content
        if image.attachments:
            file = image.attachments[0]
            imgur = im.upload_image(url=file.url)
            image_imgur = imgur.link
            return image_imgur
        elif "cdn.discordapp.com" in image_url or image_url.endswith(
            ("jpg", "png", "jpeg", "gif")
        ):
            imgur = im.upload_image(url=image_url)
            image_imgur = imgur.link
            return image_imgur


async def token_Persona(ctx, bot):
    def checkRep(message):
        return (
            message.author == ctx.message.author
            and ctx.message.channel == message.channel
        )

    q = await ctx.send(
        "Les patterns permettent de sélectionner et parler avec un personnage. Le pattern doit être composé du mot `text` entouré par un ou plusieurs caractères, d'un côté ou les deux.\n *__Par exemple__ :* `text<` et `>text<` ou encore `N:/text` sont tous les trois valides. "
    )
    rep = await bot.wait_for("message", timeout=300, check=checkRep)
    token = rep.content
    if token.lower() == "stop" or token.lower() == "cancel":
        await ctx.send("Annulation de la création.", delete_after=30)
        return "stop"
    else:
        while "text" not in token:
            await ctx.send("Erreur ! Vous avez oublié `text`.")
            rep = await bot.wait_for("message", timeout=300, check=checkRep)
            token = rep.content
            if token.lower() == "stop" or token.lower() == "cancel":
                await ctx.send("Annulation de la création.", delete_after=30)
                await rep.delete()
                await q.delete()
                return "stop"
        token = token.replace("text", "(.*)/")
        token = "^/" + token + "$"
        return token


def check_token(ctx, token):
    db = sqlite3.connect("src/owlly.db", timeout=3000)
    c = db.cursor()
    sql = "SELECT idDC FROM DC WHERE (token=? AND idU = ? AND idS = ?)"
    var = (
        token,
        ctx.message.author.id,
        ctx.guild.id,
    )
    c.execute(sql, var)
    check = c.fetchall()
    c.close()
    db.close()
    if check is None or len(check) == 0:
        return "ok"
    else:
        return "error"


def search_Persona(ctx, nom):
    db = sqlite3.connect("src/owlly.db", timeout=3000)
    c = db.cursor()
    sql = "SELECT idDC FROM DC WHERE (Nom = ? AND idU = ? AND idS = ?)"
    c.execute(
        sql,
        (
            nom,
            ctx.author.message.id,
            ctx.guild.id,
        ),
    )
    perso = c.fetchone()
    if perso is None:
        sql = "SELECT idDC FROM DC WHERE (token = ? AND idU = ? AND idS = ?)"
        c.execute(
            sql,
            (
                nom,
                ctx.author.message.id,
                ctx.guild.id,
            ),
        )
        perso = c.fetchone()
        if perso is None or len(perso) == 0:
            return "error"
        else:
            return perso[0]
    else:
        return perso[0]


async def webhook_delete(ctx, bot):
    db = sqlite3.connect("src/owlly.db", timeout=3000)
    c = db.cursor()

    def checkRep(message):
        return (
            message.author == ctx.message.author
            and ctx.message.channel == message.channel
        )

    q = await ctx.send(
        "Quel est le Persona que vous souhaitez supprimer ? Vous pouvez utiliser son nom ou son token."
    )
    rep = await bot.wait_for("message", timeout=300, check=checkRep)
    if rep.content.lower() == "stop" or rep.content.lower() == "cancel":
        await ctx.send("Annulation !", delete_after=30)
        await q.delete()
        await rep.delete()
        return
    persona = rep.content
    # Check if token :
    sql = "SELECT token FROM DC WHERE (idS = ? AND idU = ? AND token = ?)"
    var = (
        ctx.guild.id,
        ctx.message.author.id,
        persona,
    )
    c.execute(sql, var)
    check = c.fetchall()
    config = ""
    if check is None or len(check) == 0:
        # Check nom
        sql = "SELECT Nom FROM DC WHERE (idS= ? AND idU = ? AND Nom = ?)"
        var = (
            ctx.guild.id,
            ctx.message.author.id,
            persona,
        )
        c.execute(sql, var)
        check = c.fetchall()
        if check is None or len(check) == 0:
            await ctx.send(
                "Ce personnage n'existe pas, merci de vérifier votre saisie."
            )
            return
        else:
            config = "Nom"
    else:
        config = "token"
    if config == "Nom":
        sql = "DELETE FROM DC WHERE (idS=? and idU=? AND Nom=?)"
        var = (
            ctx.guild.id,
            ctx.message.author.id,
            persona,
        )
        c.execute(sql, var)
    elif config == "token":
        sql = "DELETE FROM DC WHERE (idS = ? AND idU = ? AND token = ?)"
        var = (
            ctx.guild.id,
            ctx.message.author.id,
            persona,
        )
        c.execute(sql, var)
    await ctx.send("La suppression a bien été effectuée !")
    db.commit()
    c.close()
    db.close()
    return
