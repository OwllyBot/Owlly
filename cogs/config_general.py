import discord
from discord import role
from discord.colour import Color
from discord.ext import commands, tasks
import sqlite3
import re
from typing import Optional
from discord.ext.commands import CommandError
from discord.ext.commands.errors import RoleNotFound
from cogs.Administration import config_member as member
from cogs.Administration import admin_fiche as fiche
from cogs.Administration import webhook 
import unidecode
import os
import ast
from collections import OrderedDict


class CogAdmins(
    commands.Cog,
    name="Administration",
    description="Permet d'enregistrer quelques paramètres pour le bot.",
):
    def __init__(self, bot):
        self.bot = bot

    async def search_chan(self, ctx, chan):
        try:
            chan = await commands.TextChannelConverter().convert(ctx, chan)
            return chan
        except CommandError:
            chan = "Error"
            return chan

    @commands.command(
     name= "config",
     help="Permet de faire la configuration générale du bot.",
     brief="Configuration du bot.",
     )
    @commands.has_permissions(administrator=True)
    async def config (self, ctx):
        db = sqlite3.connect("owlly.db", timeout=3000)
        c = db.cursor()
        fi = self.bot.get_cog("Fiche")
        adminfi = self.bot.get_cog("Administration des fiches")
        emoji=["✅", "❌"]
        def checkRep(message):
            return message.author == ctx.message.author and ctx.message.channel == message.channel

        def checkValid(reaction, user):
            return (
                ctx.message.author == user
                and q.id == reaction.message.id
                and (str(reaction.emoji) in emoji)
            )
        q = await ctx.send("Configuration du bot. Tout d'abord, définissez le préfix du bot.\n `0` pour garder par défaut ; `cancel` ou `stop` pour annuler.")
        rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
        if rep.content.lower() == "stop" or rep.content.lower() == "cancel":
            await q.delete()
            await ctx.send("Annulation", delete_after=30)
            await rep.delete()
            return
        elif rep.content != "0" :
            await self.set_prefix(ctx, rep.content.lower())
        q = await ctx.send("Voulez-vous configurez les rôles mis automatiquement par la commande DB ?")
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
        if reaction.emoji == "✅":
            await q.clear_reactions()
            await q.edit(content="Merci d'envoyer les rôles que vous voulez rajouter.")
            rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
            roliste = rep.content.split(" ")
            await member.roliste_init(ctx, roliste, "roliste", self.bot)
            q= await ctx.send("Voulez-vous supprimez des rôles lorsqu'un joueur devient membre du RP ?")
            await q.add_reaction("✅")
            await q.add_reaction("❌")
            reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
            if reaction.emoji == "✅":
                await q.clear_reactions()
                await q.edit(content="Merci d'envoyer les rôles que vous souhaitez faire supprimer.")
                rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
                rolerm = rep.content.split(" ")
                await member.roliste_init(ctx, rolerm, "rolerm", self.bot)
        q= await ctx.send("Voulez-vous configurer un chan servant de lexique, pour la commande `search` ? ")
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction,user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
        if reaction.emoji == "✅":
            q.clear_reactions()
            q=await q.edit(content="Merci de donner le channel voulu, sous forme de mention, nom ou ID.")
            await self.notes_config(ctx, rep.content)        
        q = await ctx.send("Voulez-vous configurer les channels des fiches de présentation ?")
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
        if reaction.emoji == "✅":
            await adminfi.chan_fiche(ctx)
            await ctx.send("Faites la commande `config_fiche` pour configurer les champs des fiches.")
        q = await ctx.send("Voulez-vous configurez les channels RP ? Cela permettra d'utiliser les Personae plus tard.")
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
        if reaction.emoji == "✅":
            await webhook.chanRp(ctx, self.bot)
        else:
           sql= "UPDATE SERVEUR SET chanRP = ? WHERE idS = ?"
           idS= ctx.guild.id
           var=("0", idS)
           c.execute(sql, var)
           db.commit()
           c.close()
           db.close()
        q = await ctx.send("Voulez-vous que les Personae soit sticky, c'est à dire qu'il suffit de parler une fois avec pour que les messages soient automatiquement changés, jusqu'au changement de token, ou l'utilisation de `\` avant un message ?")
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
        if reaction.emoji == "✅":
            await webhook.sticky(ctx, self.bot, "1")
        else:
            await webhook.sticky(ctx, self.bot, "0")
        await q.clear_reactions()
        q = await ctx.send("Voulez-vous avoir un tag HRP ? Tous les messages utilisant ce token ne seront pas converti alors que vous avez sélectionné un Persona.")
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
        if reaction.emoji == "✅":
            await q.clear_reactions()
            q = await ctx.send("Voici les différentes manières de définir un pattern :\n :white_small_square: /[text]/\n/[text]\n[text]/.\n Vous pouvez mettre ce que vous voulez à la place des `/` mais vous êtes obligée de mettre [text]! ")
            rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
            token = rep.content.lower()
            while "[text]" not in token:
                await ctx.send("Erreur ! Vous avez oublié `[text]`")
                rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
                token = rep.content.lower()
            await webhook.tokenHRP(ctx, self.bot, token)
            q=await ctx.send("Voulez-vous faire supprimer tous les messages contenant le token suivant un temps configuré ?")
            await q.add_reaction("✅")
            await q.add_reaction("❌")
            reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
            if reaction.emoji == "✅":
                await webhook.deleteHRP(ctx, self.bot, "1")
        else:
            await webhook.tokenHRP(ctx, self.bot, "0")
            await webhook.deleteHRP(ctx, self.bot, "0")
        await ctx.send("La configuration du serveur est maintenant terminé ! Vous pouvez éditer chaque paramètres séparément.")
            
    @commands.command(
        name="set_prefix",
        help="Permet de changer le prefix du bot.",
        brief="Changement du prefix.",
    )
    @commands.has_permissions(administrator=True)
    async def set_prefix(self, ctx, prefix):
        db = sqlite3.connect("owlly.db", timeout=3000)
        c = db.cursor()
        sql = "UPDATE SERVEUR SET prefix = ? WHERE idS = ?"
        var = (prefix, ctx.guild.id)
        c.execute(sql, var)
        await ctx.send(f"Prefix changé pour {prefix}")
        db.commit()
        c.close()
        db.close()


    @commands.command(
        aliases=["lexique_config"],
        help="Permet de configurer le channel dans lequel la commande `search` va faire ses recherches.",
        brief="Configuration de la recherche de message dans un channel.",
    )
    @commands.has_permissions(administrator=True)
    async def notes_config(self, ctx, chan: discord.TextChannel):
        server = ctx.guild.id
        db = sqlite3.connect("owlly.db", timeout=3000)
        c = db.cursor()
        sql = "UPDATE SERVEUR SET notes=? WHERE idS=?"
        chanID = chan.id
        var = (chanID, server)
        c.execute(sql, var)
        db.commit()
        c.close()
        db.close()
        await ctx.send(f"Le channels des notes est donc {chan}", delete_after=30)
        await ctx.message.delete()

    @commands.has_permissions(administrator=True)
    @commands.command(
        help="Permet d'enregistrer / réenregistrer la liste des rôles données par la commandes member, sans passer par le menu de configuration.",
        brief="Enregistrement de rôles pour la commande member, sans passer par le menu.",
        usage="@mention/ID des rôles à enregistrer",
        aliases=["init_role", "assign_init"],
    )
    async def role_init(self, ctx, *role: discord.Role):
        await member.role_init(ctx, role, self.bot)

    @commands.has_permissions(administrator=True)
    @commands.command(
        help="Permet d'enregistrer / réenregistrer la liste des rôles retirés par la commandes member, sans passer par le menu de configuration.",
        brief="Enregistrement de rôles pour la commande member, sans passer par le menu.",
        usage="@mention/ID des rôles à enregistrer",
        aliases=["init_rm", "assign_rm"],
    )
    async def init_role_rm(self, ctx, *role: discord.Role):
       await member.init_role_rm(ctx, role, self.bot)

    @commands.has_permissions(administrator=True)
    @commands.command(
        help="Permet d'inscrire des rôles à retirer lorsqu'un membre est validé.",
        brief="Enregistrement de rôle pour les faire retirer.",
        aliases=["rm_role", "role_remove", "remover_member"],
    )
    async def role_rm(self, ctx):
        await member.inscription_role(self.bot, ctx, "rm")

    @commands.has_permissions(administrator=True)
    @commands.command(
        help="Assignation des rôles par la commande `member`.",
        brief="Enregistrement de rôles pour la commande member.",
        aliases=["role_config", "roliste_config", "assign"],
    )
    async def roliste(self, ctx):
        await member.inscription_role(self.bot, ctx, "roliste")

    @commands.has_permissions(administrator=True)
    @commands.command(
        help= "Menu de configuration des Channels et catégories de RP",
        brief="Configuration des channels RP.",
        aliases=["chanRP", "config_chanRP"])
    async def chanHRP_menu(self, ctx):
        emoji=["1️⃣", "2️⃣", "3️⃣", "❌", "✅"]
        q=await ctx.send("1️⃣| Ajout d'un channel\n2️⃣| Suppression d'un channel\n3️⃣| Reconfiguration")
        await q.add_reaction("1️⃣")
        await q.add_reaction("2️⃣")
        await q.add_reaction("3️⃣")
        def checkRep(message):
            return message.author == ctx.message.author and ctx.message.channel == message.channel

        def checkValid(reaction, user):
            return (
                ctx.message.author == user
                and q.id == reaction.message.id
                and (str(reaction.emoji) in emoji)
            )
        reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
        if reaction.emoji == "3️⃣":
            await q.clear_reactions()
            await webhook.chanRp(ctx, self.bot)
        elif reaction.emoji == "1️⃣":
            await q.clear_reactions()
            await webhook.chanHRP_add(ctx, self.bot)
        elif reaction.emoji == "2️⃣":
            await q.clear_reactions()
            await webhook.chanHRP_rm(ctx, self.bot)
def setup(bot):
    bot.add_cog(CogAdmins(bot))
