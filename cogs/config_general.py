from test import up_DB
from cogs.clean_db import DB_utils
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
        name="config",
        help="Permet de faire la configuration générale du bot.",
        brief="Configuration du bot.",
    )
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
        db = sqlite3.connect("owlly.db", timeout=3000)
        c = db.cursor()
        utils = self.bot.get_cog("DB_utils")
        adminfi = self.bot.get_cog("Administration des fiches")
        emoji = ["✅", "❌"]
        server = ctx.guild.id

        def checkRep(message):
            return (
                message.author == ctx.message.author
                and ctx.message.channel == message.channel
            )

        def checkValid(reaction, user):
            return (
                ctx.message.author == user
                and q.id == reaction.message.id
                and (str(reaction.emoji) in emoji)
            )

        q = await ctx.send(
            "Configuration du bot. Tout d'abord, définissez le préfix du bot.\n `0` pour garder par défaut ; `cancel` ou `stop` pour annuler."
        )
        rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
        if rep.content.lower() == "stop" or rep.content.lower() == "cancel":
            await q.delete()
            await ctx.send("Annulation", delete_after=30)
            await rep.delete()
            return
        elif rep.content != "0":
            await self.set_prefix(ctx, rep.content.lower())
        q = await ctx.send(
            "Voulez-vous configurez les rôles mis automatiquement par la commande `member` ?"
        )
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for(
            "reaction_add", timeout=300, check=checkValid
        )
        if reaction.emoji == "✅":
            await q.clear_reactions()
            await q.edit(content="Merci d'envoyer les rôles que vous voulez rajouter.")
            rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
            roliste = rep.content.split(" ")
            await member.roliste_init(ctx, roliste, "roliste", self.bot)
            q = await ctx.send(
                "Voulez-vous supprimez des rôles lorsqu'un joueur devient membre du RP ?"
            )
            await q.add_reaction("✅")
            await q.add_reaction("❌")
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=300, check=checkValid
            )
            if reaction.emoji == "✅":
                await q.clear_reactions()
                await q.edit(
                    content="Merci d'envoyer les rôles que vous souhaitez faire supprimer."
                )
                rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
                rolerm = rep.content.split(" ")
                await member.roliste_init(ctx, rolerm, "rolerm", self.bot)
        else:
            await utils.init_value("roliste", "SERVEUR", "idS", "0", server)
            await utils.init_value("rolerm", "SERVEUR", "idS", "0", server)
        q = await ctx.send(
            "Voulez-vous configurer un chan servant de lexique, pour la commande `search` ? "
        )
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for(
            "reaction_add", timeout=300, check=checkValid
        )
        if reaction.emoji == "✅":
            await q.clear_reactions()
            q = await q.edit(
                content="Merci de donner le channel voulu, sous forme de mention, nom ou ID."
            )
            rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
            chan = await self.search_chan(ctx, rep.content)

            if chan != "Error":
                await self.notes_config(ctx, chan)
            else:
                await ctx.send("Channel introuvable.")
                await self.notes_config(ctx, "0")
        else:
            await utils.init_value("notes", "SERVEUR", "idS", 0, server)
        q = await ctx.send(
            "Voulez-vous configurer les channels des fiches de présentation ?"
        )
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for(
            "reaction_add", timeout=300, check=checkValid
        )
        if reaction.emoji == "✅":
            await adminfi.chan_fiche(ctx)
            await ctx.send(
                "Faites la commande `config_fiche` pour configurer les champs des fiches."
            )
        else:
            await utils.init_value("fiche_pj", "FICHE", "idS", 0, server)
            await utils.init_value("fiche_pnj", "FICHE", "idS", 0, server)
            await utils.init_value("fiche_validation", "FICHE", "idS", 0, server)

        q = await ctx.send(
            "Voulez-vous configurez les channels RP ? Cela permettra d'utiliser les Personae plus tard.\n *Les Personae peuvent agir comme des doubles comptes : ils peuvent parler à votre place en remplaçant vos messages dans les salons RP, via l'utilisation d'un préfix/suffixe que vous aurez configuré.*"
        )
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for(
            "reaction_add", timeout=300, check=checkValid
        )
        if reaction.emoji == "✅":
            await webhook.chanRp(ctx, self.bot, "1")
        else:
            await utils.init_value("chanRP", "SERVEUR", "idS", "0", server)

        q = await ctx.send(
            "Voulez-vous que les Personae soit sticky, c'est à dire qu'il suffit de parler une fois avec pour que les messages soient automatiquement changés, jusqu'au changement de token, ou l'utilisation de `\` avant un message ?"
        )
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for(
            "reaction_add", timeout=300, check=checkValid
        )
        if reaction.emoji == "✅":
            await webhook.sticky(ctx, self.bot, "1")
        else:
            await utils.init_value("sticky", "SERVEUR", "idS", 0, server)
        await q.clear_reactions()
        q = await ctx.send(
            "Voulez-vous avoir un tag HRP ? Tous les messages utilisant ce token ne seront pas converti alors que vous avez sélectionné un Persona."
        )
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for(
            "reaction_add", timeout=300, check=checkValid
        )
        if reaction.emoji == "✅":
            await q.clear_reactions()
            q = await ctx.send(
                "Voici les différentes manières de définir un pattern :\n :white_small_square: /[text]/\n/[text]\n[text]/.\n Vous pouvez mettre ce que vous voulez à la place des `/` mais vous êtes obligée de mettre [text]! \n Vous pouvez annuler avec `0`, `stop` ou `cancel`."
            )
            rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
            token = rep.content.lower()
            if token == "0" or token == "cancel" or token == "stop":
                await ctx.send("Annulation")
                await webhook.tokenHRP(ctx, self.bot, "0")
                await webhook.deleteHRP(ctx, self.bot, "0")
            else:
                while "[text]" not in token:
                    await ctx.send("Erreur ! Vous avez oublié `[text]`")
                    rep = await self.bot.wait_for(
                        "message", timeout=300, check=checkRep
                    )
                    token = rep.content.lower()
                    if token.lower() == "stop" or token.lower() == "cancel":
                        await ctx.send("Annulation", delete_after=30)
                        await rep.delete()
                        return
                await webhook.tokenHRP(ctx, self.bot, token)
                q = await ctx.send(
                    "Voulez-vous faire supprimer tous les messages contenant le token suivant un temps configuré ?"
                )
                await q.add_reaction("✅")
                await q.add_reaction("❌")
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=300, check=checkValid
                )
                if reaction.emoji == "✅":
                    await webhook.deleteHRP(ctx, self.bot, "1")
        else:
            await utils.init_value("tokenHRP", "SERVEUR", "idS", "0", server)
            await utils.init_value("delete_HRP", "SERVEUR", "idS", 0, server)
            await utils.init_value("delay_HRP", "SERVEUR", "idS", 0, server)

        q = await ctx.send("Voulez-vous limiter le nombre de Personae de vos joueurs ?")
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for(
            "reaction_add", timeout=300, check=checkValid
        )
        if reaction.emoji == "✅":
            await webhook.maxDC(ctx, self.bot, "1")
        else:
            await utils.init_value("maxDC", "SERVEUR", "idS", 0, server)
        await ctx.send(
            "La configuration du serveur est maintenant terminé ! Vous pouvez éditer chaque paramètres séparément."
        )

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
        db = sqlite3.connect("owlly.db", timeout=3000)
        c = db.cursor()
        server = ctx.guild.id
        if chan != "0":
            chanID = chan.id
            phrase = f"Le channel des notes est donc {chan}"
        else:
            chanID = 0
            phrase = f"Le lexique est désactivé."
        sql = "UPDATE SERVEUR SET notes=? WHERE idS=?"
        var = (chanID, server)
        c.execute(sql, var)
        db.commit()
        c.close()
        db.close()
        await ctx.send(phrase, delete_after=30)
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
        help="Menu de configuration des Channels et catégories de RP",
        brief="Configuration des channels RP.",
        aliases=["chanRP", "config_chanRP"],
    )
    async def chanHRP_menu(self, ctx):
        emoji = ["1️⃣", "2️⃣", "3️⃣", "❌", "✅"]
        q = await ctx.send(
            "1️⃣| Ajout d'un channel\n2️⃣| Suppression d'un channel\n3️⃣| Reconfiguration"
        )
        await q.add_reaction("1️⃣")
        await q.add_reaction("2️⃣")
        await q.add_reaction("3️⃣")

        def checkRep(message):
            return (
                message.author == ctx.message.author
                and ctx.message.channel == message.channel
            )

        def checkValid(reaction, user):
            return (
                ctx.message.author == user
                and q.id == reaction.message.id
                and (str(reaction.emoji) in emoji)
            )

        reaction, user = await self.bot.wait_for(
            "reaction_add", timeout=300, check=checkValid
        )
        if reaction.emoji == "3️⃣":
            await q.delete()
            q = await ctx.send("Voulez-vous avoir des channels HRP pour les webhook ?")
            await q.add_reaction("✅")
            await q.add_reaction("❌")
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=300, check=checkValid
            )
            if reaction.emoji == "✅":
                config = "1"
            else:
                await q.delete()
                await ctx.send("Aucun channel ne sera configuré.")
                config = "0"
            await webhook.chanRp(ctx, self.bot, config)
        elif reaction.emoji == "1️⃣":
            await q.clear_reactions()
            await webhook.chanHRP_add(ctx, self.bot)
        elif reaction.emoji == "2️⃣":
            await q.clear_reactions()
            await webhook.chanHRP_rm(ctx, self.bot)

    @commands.has_permissions(administrator=True)
    @commands.command(
        help="Permet d'activer ou désactiver le mode sticky.",
        brief="Configuration du Sticky",
        aliases=["sticky_config", "config_sticky"],
    )
    async def sticky_mode(self, ctx):
        def checkValid(reaction, user):
            return (
                ctx.message.author == user
                and q.id == reaction.message.id
                and (str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌")
            )

        db = sqlite3.connect("owlly.db", timeout=3000)
        c = db.cursor()
        sql = "SELECT sticky FROM SERVEUR WHERE idS = ?"
        c.execute(sql, (ctx.guild.id,))
        mode = c.fetchone()
        if mode is None:
            mode = 0
        else:
            mode = mode[0]
        if mode == 0:
            q = await ctx.send(
                "Actuellement, le sticky est désactivé. Voulez-vous l'activer ?"
            )
            await q.add_reaction("✅")
            await q.add_reaction("❌")
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=300, check=checkValid
            )
            if reaction.emoji == "✅":
                await q.delete()
                mode = 1
                await webhook.sticky(ctx, self.bot, mode)
                await ctx.send("Changement effectué.")
                return
            else:
                await q.delete()
                await ctx.send("Annulation.")
                return
        else:
            q = await ctx.send(
                "Actuellement, le sticky est activé. Voulez-vous le désactiver ?"
            )
            await q.add_reaction("✅")
            await q.add_reaction("❌")
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=300, check=checkValid
            )
            if reaction.emoji == "✅":
                mode = 0
                await webhook.sticky(ctx, self.bot, mode)
                await q.delete()
                await ctx.send("Changement effectué.")
                return
            else:
                await q.delete()
                await ctx.send("Annulation.")
                return

    @commands.has_permissions(administrator=True)
    @commands.command(help="Permet de configurer le HRP", brief="Configuration du HRP")
    async def patternHRP(self, ctx):
        def checkRep(message):
            return (
                message.author == ctx.message.author
                and ctx.message.channel == message.channel
            )

        db = sqlite3.connect("owlly.db", timeout=3000)
        c = db.cursor()
        sql = "SELECT tokenHRP FROM SERVEUR where idS=?"
        c.execute(sql, (ctx.guild.id,))
        tokenHRP = c.fetchone()
        if tokenHRP is None:
            tokenHRP = "0"
        else:
            tokenHRP = tokenHRP[0]
        if tokenHRP == "0":
            info = "Actuellement, vous n'avez pas de pattern.\n"
        else:
            info = f"Actuellement, votre pattern est {tokenHRP}.\n Pour supprimer le pattern, écrivez `0`."
        await ctx.send(
            f"{info}Voici les différentes manières de définir un pattern :\n :white_small_square: /[text]/\n/[text]\n[text]/.\n Vous pouvez mettre ce que vous voulez à la place des `/` mais vous êtes obligée de mettre [text]! "
        )
        rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
        token = rep.content.lower()
        if "0" in token:
            await ctx.send(f"Suppression du pattern.")
            await webhook.tokenHRP(ctx, self.bot, "0")
            await webhook.deleteHRP(ctx, self.bot, "0")
            return
        else:
            while "[text]" not in token:
                await ctx.send("Erreur ! Vous avez oublié `[text]`")
                rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
                token = rep.content.lower()
                if token.lower() == "stop" or token.lower() == "cancel":
                    await ctx.send("Annulation", delete_after=30)
                    await rep.delete()
                    return
            await webhook.tokenHRP(ctx, self.bot, token)
            await ctx.send("Changement effectué.")
            return

    @commands.has_permissions(administrator=True)
    @commands.command(
        help="Permet de configurer le délais de suppression du HRP",
        brief="Configuration du délais HRP.",
    )
    async def delay_hrp(self, ctx):
        def checkRep(message):
            return (
                message.author == ctx.message.author
                and ctx.message.channel == message.channel
            )

        emoji = ["✅", "❌", "1️⃣", "2️⃣"]

        def checkValid(reaction, user):
            return (
                ctx.message.author == user
                and q.id == reaction.message.id
                and str(reaction.emoji) in emoji
            )

        db = sqlite3.connect("owlly.db", timeout=3000)
        c = db.cursor()
        sql = "SELECT delete_HRP, delay_HRP WHERE idS=?"
        c.execute(sql, (ctx.guild.id,))
        data = c.fetchone()
        if data is None:
            delete = 0
            delay_HRP = 0
        else:
            delete = data[0]
            delay_HRP = data[1]
        if delete == 0:
            q = await ctx.send(
                "Actuellement, il n'y a pas de suppression automatique du HRP. Voulez-vous l'activez ?"
            )
            await q.add_reaction("✅")
            await q.add_reaction("❌")
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=300, check=checkValid
            )
            if reaction.emoji == "✅":
                config = "1"
                await webhook.deleteHRP(ctx, self.bot, config)
                await q.delete()
                await ctx.send("Changement effectué.")
                return
            else:
                await ctx.send("Annulation")
                await q.delete()
                return
        else:
            q = await ctx.send(
                f"Actuellement, la suppression automatique est activé, et son délais est de {delay_HRP}s. Que souhaitez vous changer ?\n1️⃣ - Enlever la suppression automatique \n2️⃣ - Régler le délais"
            )
            await q.add_reaction("1️⃣")
            await q.add_reaction("2️⃣")
            await q.add_reaction("❌")
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=300, check=checkValid
            )
            if reaction.emoji == "1️⃣":
                await q.delete()
                await webhook.deleteHRP(ctx, self.bot, "0")
                await ctx.send("Changement effectué, le HRP ne sera plus supprimé.")
                return
            elif reaction.emoji == "2️⃣":
                await q.delete
                await webhook.deleteHRP(ctx, self.bot, "1")
                await ctx.send("Changement effectué")
                return
            else:
                await ctx.send("Annulation")
                await q.delete()
                return

    @commands.command(
        help="Permet de configurer le nombre maximum de Personae qu'un joueur peut créer et utiliser.",
        brief="Permet de configurer le maximum de Personae.",
        alias=["config_max", "maxDC", "maxdc_config"],
    )
    @commands.has_permissions(administrator=True)
    async def max_config(self, ctx):
        def checkValid(reaction, user):
            return (
                ctx.message.author == user
                and q.id == reaction.message.id
                and (str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌")
            )

        def checkRep(message):
            return (
                message.author == ctx.message.author
                and ctx.message.channel == message.channel
            )

        db = sqlite3.connect("owlly.db", timeout=3000)
        c = db.cursor()
        sql = "SELECT maxDC FROM SERVEUR WHERE idS=?"
        c.execute(sql, (ctx.guild.id))
        maxDC = c.fetchone()
        if maxDC is None:
            maxDC = 0
        else:
            maxDC = maxDC[0]
        if maxDC == 0:
            phrase = f"Actuellement, le nombre de Persona est illimité. Voulez-vous le limiter ?"
        else:
            phrase = f"Actuellement, le nombre de Persona est limité à {maxDC}, voulez-vous le changer ?"
        q = await ctx.send(phrase)
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for(
            "reaction_add", timeout=300, check=checkValid
        )
        if reaction.emoji == "✅":
            await webhook.maxDC(ctx, self.bot, "1")
            await ctx.send("Changement effectué")
            return
        else:
            await ctx.send("Annulation")
            return


def setup(bot):
    bot.add_cog(CogAdmins(bot))
