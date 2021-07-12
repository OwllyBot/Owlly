import discord
from cogs.webhook import gestion_Webhook as gestion
import sqlite3
from discord.ext import commands
import os
import uuid


async def webhook_create(ctx, bot):
    check = gestion.number_check(ctx)
    if check == "Error":
        await ctx.send("Vous avez trop de personnages !")
        return
    elif check == "inactive":
        await ctx.send("Les Personae sont désactivés sur le serveur.")
        return
    else:
        id_Persona = str(uuid.uuid4())
        id_Persona = id_Persona.split("-")[0]

        def checkRep(message):
            return (
                message.author == ctx.message.author
                and ctx.message.channel == message.channel
            )

        db = sqlite3.connect("src/owlly.db", timeout=3000)
        c = db.cursor()
        q = await ctx.send("Rentrez d'abord un nom !")
        rep = await bot.wait_for("message", timeout=300, check=checkRep)
        if rep.content.lower() == "stop":
            await ctx.send("Annulation")
            await q.delete()
            await rep.delete()
            return
        nom = rep.content()
        nom = gestion.name_persona(ctx, nom, id_Persona)
        check_name = gestion.name_check(ctx, nom)
        if check_name == "error":
            await ctx.send("Erreur ! Ce nom est déjà pris.")
            await q.delete()
            await rep.delete()
            return
        q = await ctx.send(
            "Maintenant, envoyez une image. Cela peut être un lien, ou une pièce-jointe."
        )
        rep = await bot.wait_for("message", timeout=300, check=checkRep)
        image = await gestion.image_persona(ctx, bot, rep)
        if image == "stop":
            return
        token = await gestion.token_Persona(ctx, bot)
        if token == "stop":
            return
        sql = "INSERT INTO DC (idDC, idS, idU, Nom, Avatar, Token, active) VALUES (?,?,?,?,?,?,?)"
        var = (
            id_Persona,
            ctx.guild.id,
            ctx.message.author.id,
            nom,
            image,
            token,
            "false",
        )
        await ctx.send("La création est maintenant terminée !")
        c.execute(sql, var)
        db.commit()
        c.close()
        db.close()

async def webhook_edit(ctx, bot, idDC, config):
    def checkRep(message):
        return (
            message.author == ctx.message.author
            and ctx.message.channel == message.channel
        )

    db = sqlite3.connect("src/owlly.db", timeout=3000)
    c = db.cursor()

    if config == "1":  # Edition nom
        q = await ctx.send("Merci d'entrer le nouveau nom du personnage.")
        rep = await bot.wait_for("message", timeout=300, check=checkRep)
        if rep.content.lower() == "stop" or rep.content.lower() == "cancel":
            await ctx.send("Annulation !")
            await q.delete()
            await rep.delete()
            return
        name = gestion.name_persona(ctx, rep.content, idDC)
        check=gestion.name_check(ctx, name)
        if check == "error":
            await ctx.send("Erreur ! Ce nom est déjà pris.")
            await q.delete()
            await rep.delete()
            return
        sql = "UPDATE DC SET Nom = ? WHERE idDC = ?"
        var = (name, idDC)
        c.execute(sql, var)
        db.commit()
        c.close()
        db.close()
        await ctx.send("Modification enregistrée !")
        return

    elif config == "2":  # Avatar
        q = await ctx.send("Merci d'envoyer la nouvelle image.")
        rep = await bot.wait_for("message", timeout=300, check=checkRep)
        if rep.content.lower() == "stop" or rep.content.lower() == "cancel":
            await ctx.send("Annulation !", delete_after=30)
            await q.delete()
            await rep.delete()
            return
        image = gestion.image_persona(ctx, bot, rep)
        if image == "stop":
            return
        sql = "UPDATE DC SET Avatar = ? WHERE idDC = ?"
        var = (image, idDC)
        c.execute(sql, var)
        db.commit()
        c.close()
        db.close()
        await ctx.send("Modification enregistrée !")
        return

    elif config == "3":  # Token
        token = gestion.token_Persona(ctx, bot)
        if token == "stop":
            return
        sql = "UPDATE DC SET token=? WHERE idDC = ?"
        var = (token, idDC)
        c.execute(sql, var)
        db.commit()
        c.close()
        db.close()
        await ctx.send("Modification enregistrée !")
        return
