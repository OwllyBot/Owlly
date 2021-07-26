import sqlite3
import uuid

import discord
from cogs.function_webhook import gestion_webhook as gestion
from discord.colour import Color


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
        check_token = gestion.check_token(ctx, bot, token)
        if check_token == "error":
            await ctx.send("Erreur ! Ce token est déjà pris.")
            await q.delete()
            await rep.delete()
            return
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
        check = gestion.name_check(ctx, name)
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
        check = gestion.check_token(ctx, token)
        if check == "error":
            await ctx.send("Erreur ! Ce token est déjà pris.")
            return
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


async def menu_edit(ctx, bot):
    emoji = ["1️⃣", "2️⃣", "3️⃣", "❌", "✅"]

    def checkRep(message):
        return (
            message.author == ctx.message.author
            and ctx.message.channel == message.channel
        )

    def checkValid(reaction, user):
        return (
            ctx.message.author == user
            and q.id == reaction.message.id
            and reaction.emoji in emoji
        )

    edition = discord.Embed(title="PERSONAE - ÉDITION", color=Color.dark_teal())
    edition.add_field(
        name="1️⃣ | Nom",
        value="Édition du nom",
        inline=False,
    )
    edition.add_field(name="2️⃣ | Avatar", value="Édition de l'avatar", inline=False)
    edition.add_field(name="3️⃣ | Token", value="Édition du token", inline=False)
    edition.set_footer(
        text="Cliquez sur la réaction pour choisir !\n ❌ Pour quitter le menu."
    )
    q = await ctx.send(embed=edition)
    await q.add_reaction("1️⃣")
    await q.add_reaction("2️⃣")
    await q.add_reaction("3️⃣")
    await q.add_reaction("❌")
    reaction, user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
    if reaction.emoji == "1️⃣":
        await q.delete()
        q = await ctx.send(
            "Merci d'envoyer le nom ou le token du personnage que vous voulez éditer."
        )
        rep = await bot.wait_for("message", timeout=300, check=checkRep)
        persona = rep.content
        if rep.content.lower() == "stop" or rep.content.lower() == "cancel":
            await ctx.send("Annulation !", delete_after=30)
            await q.delete()
            await rep.delete()
            return
        idDC = gestion.search_Persona(ctx, persona)
        if idDC == "error":
            await ctx.send("Erreur ! Ce Persona n'existe pas.")
            return
        await webhook_edit(ctx, bot, idDC, "1")
        return
    elif reaction.emoji == "2️⃣":
        await q.delete()
        q = await ctx.send(
            "Merci d'envoyer le nom ou le token du personnage que vous voulez éditer."
        )
        rep = await bot.wait_for("message", timeout=300, check=checkRep)
        persona = rep.content
        if rep.content.lower() == "stop" or rep.content.lower() == "cancel":
            await ctx.send("Annulation !", delete_after=30)
            await q.delete()
            await rep.delete()
            return
        idDC = gestion.search_Persona(ctx, persona)
        if idDC == "error":
            await ctx.send("Erreur ! Ce Persona n'existe pas.")
            return
        await webhook_edit(ctx, bot, idDC, "2")
        return
    elif reaction.emoji == "3️⃣":
        await q.delete()
        q = await ctx.send(
            "Merci d'envoyer le nom ou le token du personnage que vous voulez éditer."
        )
        rep = await bot.wait_for("message", timeout=300, check=checkRep)
        persona = rep.content
        if rep.content.lower() == "stop" or rep.content.lower() == "cancel":
            await ctx.send("Annulation !", delete_after=30)
            await q.delete()
            await rep.delete()
            return
        idDC = gestion.search_Persona(ctx, persona)
        if idDC == "error":
            await ctx.send("Erreur ! Ce Persona n'existe pas.")
            return
        await webhook_edit(ctx, bot, idDC, "3")
        return
    else:
        await q.delete()
        await ctx.send("Annulation !")
        return


async def menu(ctx, bot):
    emoji = ["1️⃣", "2️⃣", "3️⃣", "❌", "✅"]

    def checkValid(reaction, user):
        return (
            ctx.message.author == user
            and q.id == reaction.message.id
            and reaction.emoji in emoji
        )

    embed = discord.Embed(title="GESTION PERSONAE", color=Color.dark_teal())
    embed.add_field(
        name="1️⃣ | Création",
        value="Permet de débuter la création d'un Persona",
        inline=False,
    )
    embed.add_field(
        name="2️⃣ | Édition",
        value="Permet d'éditer un Persona",
        inline=False,
    )
    embed.add_field(
        name="3️⃣ | Suppression", value="Permet de supprimer un Persona", inline=False
    )
    embed.set_footer(
        text="Cliquez sur la réaction pour choisir !\n ❌ Pour quitter le menu."
    )
    q = await ctx.send(embed=embed)
    i = 0
    while emoji[i] != "✅":
        await q.add_reaction(emoji[i])
        i += 1
    reaction, user = await bot.wait_for("reaction_add", timeout=300, check=checkValid)
    if reaction.emoji == "1️⃣":  # Création
        await q.delete()
        await webhook_create(ctx, bot)
        return
    elif reaction.emoji == "2️⃣":  # Edition
        await q.delete()
        await menu_edit(ctx, bot)
        return

    elif reaction.emoji == "3️⃣":  # Deletion
        await q.delete()
        await gestion.webhook_delete(ctx, bot)
        return
    else:
        await ctx.send("Annulation !")
        return
