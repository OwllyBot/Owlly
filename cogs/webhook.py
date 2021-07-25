import discord
from discord.ext import commands
import sqlite3
import re
from cogs.function_webhook import gestion_webhook as gestion
from cogs.function_webhook import lecture_webhook as lecture
from cogs.function_webhook import menu_webhook as menu

# REPO PUBLIQUE


class Personae(
    commands.Cog,
    name="Personae",
    description="Toutes les commandes afin de créer et gérer un personnage "
    "sous forme de webhook",
):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        help="Ouvre le menu de gestion des Personae.", brief="Menu des Personae."
    )
    async def personae(self, ctx):
        await menu.menu(ctx, self.bot)
        return

    @commands.command(
        help="Ouvre le menu d'édition des Personae.",
        brief="Menu d'édition des Personae",
    )
    async def edit_persona(self, ctx):
        await menu.menu_edit(ctx, self.bot)
        return

    @commands.command(
        brief="Edition rapide du nom d'un Personae",
        help="Permet d'éditer rapidement le nom d'un Personae",
        usage='"Nom/token" "Nouveau Nom"',
    )
    async def persona_nom(self, ctx, nom, new):
        id = gestion.search_Persona(ctx, nom)
        tag = gestion.name_persona(ctx, new, id)
        check = gestion.name_check(ctx, tag)
        if check == "error":
            await ctx.send("Ce nom est déjà pris !")
            return
        db = sqlite3.connect("src/owlly.db", timeout=3000)
        c = db.cursor()
        sql = "UPDATE DC SET Nom = ? WHERE (idS=? AND idDC = ? AND Nom = ?)"
        var = (tag, ctx.guild.id, id, nom)
        c.execute(sql, var)
        await ctx.send("Le nom a été mis à jour !")
        db.commit()
        c.close()
        db.close()

    @commands.command(
        brief="Edition token de Persona",
        help="Permet d'éditer le token d'un Persona.",
        usage='"Token/nom"',
    )
    async def persona_token(self, ctx, nom):
        db = sqlite3.connect("src/owlly.db", timeout=3000)
        c = db.cursor()

        id = gestion.search_Persona(ctx, nom)
        token = gestion.token_Persona(ctx, self.bot)
        check = gestion.check_token(ctx, token)
        if check == "error":
            await ctx.send("Ce token est déjà pris !")
            return
        sql = "UPDATE DC SET token=? WHERE idDC = ?"
        var = (token, id)
        c.execute(sql, var)
        db.commit()
        c.close()
        db.close()
        return

    @commands.command(
        brief="Edition de l'image d'un Persona.",
        help="Permet d'éditer l'image d'un Persona.",
        usage='"nom/Token"',
    )
    async def persona_image(self, ctx, nom):
        db = sqlite3.connect("src/owlly.db", timeout=3000)
        c = db.cursor()

        def checkRep(message):
            return (
                message.author == ctx.message.author
                and ctx.message.channel == message.channel
            )

        idC = gestion.search_Persona(ctx, nom)
        if idC == "error":
            await ctx.send("Erreur ! Ce Persona est introuvable.")
            return
        await ctx.send("Merci d'envoyer l'image (lien ou fichier)")
        rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
        image = await gestion.image_persona(ctx, self.bot, rep)
        if image == "stop":
            return
        sql = "UPDATE DC SET Avatar = ? WHERE idDC = ?"
        var = (image, idC)
        c.execute(sql, var)
        db.commit()
        c.close()
        db.close()
        return

    @commands.command(
        help="Supprime un Persona de la base de donnée.",
        brief="Suppression d'un Persona.",
        usage='"Nom/Token"',
    )
    async def persona_delete(self, ctx, persona):
        db = sqlite3.connect("src/owlly.db", timeout=3000)
        c = db.cursor()
        id = gestion.search_Persona(ctx, persona)
        if id == "error":
            await ctx.send("Ce Persona n'existe pas")
            return
        sql = "DELETE FROM DC WHERE (idS = ? AND idU = ? AND idDC = ?)"
        var = (
            ctx.guild.id,
            ctx.message.author.id,
            id,
        )
        c.execute(sql, var)
        await ctx.send("La suppression a bien été effectuée !")
        db.commit()
        c.close()
        db.close()
        return

    @commands.Cog.listener()
    async def on_message(self, message):
        db = sqlite3.connect("src/owlly.db", timeout=3000)
        c = db.cursor()
        regex = "0"
        idS = message.guild.id
        chan = message.channel.id
        catego = message.channel.category_id
        user = message.author.id
        sql = "SELECT chanRP FROM SERVEUR WHERE idS=?"
        c.execute(sql, (idS,))
        chanRP = c.fetchone()
        if chanRP is not None:
            chanRP = chanRP[0]
            chanRP = chanRP.split(",")
        sql = "SELECT tokenHRP FROM SERVEUR WHERE idS=?"
        c.execute(sql, (idS,))
        token = c.fetchone()
        if token is not None:
            token = token[0]
        if token != "0":
            regex = re.compile(token, re.DOTALL)
        if chan in chanRP or catego in chanRP:
            if message.reference:
                # Reply
                await lecture.edit_webhook(message, idS, user)
            elif not isinstance(regex, str) and regex.match(message.content):
                # Delete HRP
                await lecture.delete_HRP(message, idS)
            else:
                await lecture.switch_persona(self.bot, message, idS, user)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        action = payload.emoji
        idS = payload.guild_id
        channel = self.bot.get_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)
        user = payload.user_id
        db = sqlite3.connect("src/owlly.db", timeout=3000)
        c = db.cursor()
        sql = "SELECT chanRP FROM SERVEUR WHERE idS=?"
        c.execute(sql, (idS,))
        chanRP = c.fetchone()
        if chanRP is not None:
            chanRP = chanRP[0].split(",")


def setup(bot):
    bot.add_cog(Personae(bot))
