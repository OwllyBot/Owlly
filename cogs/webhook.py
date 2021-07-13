import discord
from discord.ext import commands
import sqlite3
from cogs.webhook import gestionWebhook as gestion
from cogs.webhook import lecture_webhook as lecture
from cogs.webhook import menu_webhook as menu

# REPO PUBLIQUE


class Personae(
    commands.cogs,
    name="Personae",
    description="Toutes les commandes afin de créer et gérer un personnage sous forme de webhook",
):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        help="Ouvre le menu de gestion des Personae.",
        brief="Menu des Personae."
    )
    async def personae (self, ctx):
        await menu.menu(ctx, self.bot)
        return

    @commands.command(
        help="Ouvre le menu d'édition des Personae.",
        brief="Menu d'édition des Personae"
    )
    async def edit_persona(self, ctx):
        await menu.menu_edit(ctx, self.bot)
        return

    @commands.command(
        brief="Edition rapide du nom d'un Personae",
        help="Permet d'éditer rapidement le nom d'un Personae",
        usage="\"Nom/token\" \"Nouveau Nom\""
    )
    async def persona_nom(self, ctx, nom, new):
        id=gestion.search_Persona(ctx, nom)
        tag=gestion.name_persona(ctx, new, id)
        check=gestion.name_check(ctx, tag)
        if check == "error":
            await ctx.send("Ce nom est déjà pris !")
            return
        db = sqlite3.connect("src/owlly.db", timeout=3000)
        c = db.cursor()
        sql="UPDATE DC SET Nom = ? WHERE (idS=? AND idDC = ? AND Nom = ?)"
        var=(tag, ctx.guild.id, id, nom)
        c.execute(sql, var)
        await ctx.send("Le nom a été mis à jour !")
        db.commit()
        c.close()
        db.close()

    @commands.command(
        brief="Edition token de Persona",
        help="Permet d'éditer le token d'un Persona.",
        usage="\"Token/nom\""
    )   
    async def persona_token(self, ctx, nom):
        db = sqlite3.connect("src/owlly.db", timeout=3000)
        c = db.cursor()
        
        id = gestion.search_Persona(ctx, nom)
        token=gestion.token_Persona(ctx, self.bot)
        check=gestion.check_token(ctx,token)
        if check == "error":
            await ctx.send ("Ce token est déjà pris !")
            return
        sql = "UPDATE DC SET token=? WHERE idDC = ?"
        var=(token, id)
        c.execute(sql, var)
        db.commit()
        c.close()
        db.close()
        return

    @commands.command(
        brief="Edition de l'image d'un Persona.",
        help="Permet d'éditer l'image d'un Persona.",
        usage="\"nom/Token\""
    )
    async def persona_image(self, ctx, nom):
        db = sqlite3.connect("src/owlly.db", timeout=3000)
        c = db.cursor()
        def checkRep(message):  
            return message.author == ctx.message.author and ctx.message.channel == message.channel
        idC= gestion.search_Persona(ctx, nom)
        if idC == "error":
            await ctx.send("Erreur ! Ce Persona est introuvable.")
            return
        await ctx.send("Merci d'envoyer l'image (lien ou fichier)")
        rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
        image=await gestion.image_persona(ctx, self.bot, rep)
        if image == "stop":
            return
        sql="UPDATE DC SET Avatar = ? WHERE idDC = ?"
        var=(image, idC)
        c.execute(sql, var)
        db.commit()
        c.close()
        db.close()
        return
        


    
def setup(bot):
    bot.add_cog(Personae)
