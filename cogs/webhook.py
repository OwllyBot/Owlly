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
    description="Toutes les commandes afin de créer et gérer un personnage sous forme de webhook",
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

    @Commands.Cog.listener()
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
        config = False
        if chanRP is not none:
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
                ref_id = message.reference.message_id
                ref_msg = await fetch_message(ref_id)
                perso_name = ref_msg.author.name
                sql = "SELECT idDC WHERE (idS = ? AND idU=? AND Nom = ?)"
                var = (
                    idS,
                    user,
                    perso_name,
                )
                c.execute(sql, var)
                perso_check=c.fetchone()
                if perso:
                    id_edit=ref_msg.webhook_id
                    if isinstance()
            if regex.match(message.content):
                sql = "SELECT delay_HRP FROM SERVEUR WHERE idS=?"
                c.execute(sql, (idS,))
                delay = c.fetchone()
                if delay:
                    delay = delay[0]
                if delay != 0:
                    await message.delete(delay)
                    return
            sql = "SELECT token FROM DC WHERE (idS=? AND idU=?)"
            var = (
                idS,
                user,
            )
            c.execute(sql, var)
            perso = [x[0] for x in c.fetchall()]
            sql = "SELECT sticky from SERVEUR WHERE idS=?"
            c.execute(sql, (idS,))
            sticky = c.fetchone()
            web = False
            webcontent = message.content
            if sticky:
                sticky = sticky[0]
            else:
                sticky = "0"
            for snippet in perso:
                reg = re.compile(snippet, re.DOTALL)
                if reg.match(message.content):
                    sql = (
                        "SELECT Nom, Avatar FROM DC WHERE (idS=? AND "
                        "idU=? AND Token = ?)"
                    )
                    var = (
                        idS,
                        user,
                        snippet,
                    )
                    c.execute(sql, var)
                    if char:
                        char = [x for x in char]
                        web = True
                        send = reg.match(message.content)
                        webcontent = send.group(1)
                        if sticky == "1":
                            sql = (
                                "UPDATE DC SET Active = ? WHERE (idS=? AND "
                                "idU=? AND Token =?)"
                            )
                            c.execute(sql, idS, user, snippet)
                        break
            if not web and sticky == "1":
                sql = (
                    "SELECT Nom, Avatar FROM DC WHERE (idS = ? AND idU=? AND Active=?)"
                )
                var = (
                    idS,
                    user,
                    1,
                )
                c.execute(sql, var)
                char = c.fetchone()
                if char:
                    web = true
                    char = [x for x in char]
            if web:
                NPC = await message.channel.webhooks()
                OwllyE = False
                if len(NPC) > 0:
                    # Webhook exists
                    for i in NPC:
                        if i.name == "OwllyNPC":
                            # OWLLYNPC exists
                            OwllyNPC = i  # Est un webhook
                            OwllyE = True
                            break
                if not OwllyE:
                    OwllyNPC = await create_webhook(
                        "OwllyNPC",
                        avatar=self.bot.avatar_url,
                        reason="OwllyNPC doesn't exist yet !",
                    )
                await OwllyNPC.send(
                    content=webcontent,
                    username=char[0],
                    avatar_url=char[1],
                    allowed_mentions=True,
                )
                await message.delete()


def setup(bot):
    bot.add_cog(Personae(bot))
