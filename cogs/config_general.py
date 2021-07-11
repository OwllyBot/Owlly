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
from cogs.Administration import webhook_config as webhook
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
            await member.roliste_init(ctx, self.bot, "roliste", roliste)
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
                await member.roliste_init(ctx, self.bot, "rolerm", rolerm)
            else:
                await q.clear_reactions()
                await utils.init_value("rolerm","SERVEUR", "idS", "0", server)
                       
        else:
            await q.clear_reactions()
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
            await q.clear_reactions()
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
            await q.clear_reactions()
            await adminfi.chan_fiche(ctx)
            await ctx.send(
                "Faites la commande `config_fiche` pour configurer les champs des fiches."
            )
        else:
            await q.clear_reactions()
            await utils.init_value("fiche_pj", "FICHE", "idS", 0, server)
            await utils.init_value("fiche_pnj", "FICHE", "idS", 0, server)
            await utils.init_value("fiche_validation", "FICHE", "idS", 0, server)
        q = await ctx.send("Voulez-vous configurez les Personae ?\n *Les Personae peuvent agir comme des doubles comptes : ils peuvent parler à votre place en remplaçant vos messages dans les salons RP, via l'utilisation d'un préfix/suffixe que vous aurez configuré.*")
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for("add_reaction", timeout=300, check=checkValid)
        if reaction.emoji == "✅":
            q = await ctx.send("Voulez-vous limiter le nombre de Personae de vos joueurs ?")
            await q.add_reaction("✅")
            await q.add_reaction("❌")
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=300, check=checkValid
            )
            if reaction.emoji == "✅":
                await q.clear_reactions()
                await webhook.maxDC(ctx, self.bot, "1")
            else:
                await q.clear_reactions()
                await utils.init_value("maxDC", "SERVEUR", "idS", 0, server)

            q = await ctx.send(
                "Voulez-vous avoir un tag avant le nom des persona ?\n Les tags sont des patterns préconfigurés donnant diverses informations, que ce soit le nom du joueur, le nom du serveur..."
            )
            await q.add_reaction("✅")
            await q.add_reaction("❌")
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=300, check=checkValid
            )
            if reaction.emoji == "✅":
                await q.clear_reactions()
                await webhook.tag_Personae(ctx, self.bot, "1")
            else:
                await q.clear_reactions()
                await utils.init_value("tag", "SERVEUR", "idS", "0", server)

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
        else:
            await q.clear_reactions()
            await utils.init_value("sticky", "SERVEUR", "idS", 0, server)
            await utils.init_value("tag", "SERVEUR", "idS", "0", server)
            await utils.init_value("maxDC", "SERVEUR", "idS", -1, server)
            await ctx.send("Les Personae sont donc désactivés sur ce serveur.")
            
        q = await ctx.send(
            "Voulez-vous avoir un tag HRP ?\n Cela permet :\n:white_small_square: Que tous les messages utilisant ce token ne soient pas converti alors que vous avez sélectionné un Persona.\n:white_small_square: De faire supprimer automatiquement le HRP suivant un temps configuré."
        )
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for(
            "reaction_add", timeout=300, check=checkValid
        )
        if reaction.emoji == "✅":
            await q.clear_reactions()
            q = await ctx.send(
           "Quel est le temps que vous voulez configurer ?"
           )
            await q.add_reaction("✅")
            await q.add_reaction("❌")
            reaction, user = await self.bot.wait_for(
               "reaction_add", timeout=300, check=checkValid
            )
            if reaction.emoji == "✅":
                await q.clear_reactions()
                await webhook.deleteHRP(ctx, self.bot, "1")
            else:
                await q.clear_reactions()
                await webhook.deleteHRP(ctx, self.bot, "0")
        else:
            await q.clear_reactions()
            await utils.init_value("tokenHRP", "SERVEUR", "idS", "0", server)
            await utils.init_value("delete_HRP", "SERVEUR", "idS", 0, server)
            await utils.init_value("delay_HRP", "SERVEUR", "idS", 0, server)       

        q = await ctx.send(
            "Voulez-vous configurez les channels et catégories RP ? Cela définira les channels où les Personae peuvent être utilisés, et où le HRP sera supprimé."
        )
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for(
            "reaction_add", timeout=300, check=checkValid
        )
        if reaction.emoji == "✅":
            await q.clear_reactions()
            await webhook.chanRp(ctx, self.bot, "1")
        else:
            await q.clear_reactions()
            await utils.init_value("chanRP", "SERVEUR", "idS", "0", server)
            await webhook.tokenHRP(ctx, self.bot, "1")
        
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
        brief="Enregistrement des rôles retirés pour la commande member, sans passer par le menu.",
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
            info = f"Actuellement, votre pattern est {tokenHRP}.\n"
        await ctx.send(info)
        await webhook.tokenHRP(ctx, self, "1")
        c.close()
        db.close()
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
        c.execute(sql, (ctx.guild.id,))
        maxDC = c.fetchone()
        if maxDC is None:
            maxDC = 0
        else:
            maxDC = maxDC[0]
        if maxDC == 0:
            phrase = f"Actuellement, le nombre de Persona est illimité. Voulez-vous le limiter ?"
        if maxDC == -1:
            phrase=f"Actuellement, les Personae sont désactivés sur le serveur. Voulez-vous le changer ?"
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

    @commands.command(
        help="Affiche le menu de configuration des Personae, permettant de modifier les différents paramètres à partir de choix.",
        brief="Affiche le menu d'administration des Personae.",
    )
    @commands.has_permissions(manage_nicknames=True)
    async def admin_rp(self, ctx):
        await ctx.message.delete()
        db = sqlite3.connect("owlly.db", timeout=3000)
        c = db.cursor()
        emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "❌", "✅"]

        def checkValid(reaction, user):
            return (
                ctx.message.author == user
                and q.id == reaction.message.id
                and str(reaction.emoji) in emoji
            )

        def checkRep(message):
            return (
                message.author == ctx.message.author
                and ctx.message.channel == message.channel
            )

        embed = discord.Embed(title="PERSONAE ADMINISTRATION", color=Color.dark_teal())
        embed.add_field(
            name="1️⃣ - Gestion des channels",
            value="Permet d'ajouter ou supprimers les channels de RP",
            inline=False,
        )
        embed.add_field(
            name="2️⃣ - Sticky",
            value="Permet d'activer ou désactiver le mode sticky.",
            inline=False,
        )
        embed.add_field(
            name="3️⃣ - Maximum de personnages",
            value="Permet de régler le nombre maximum de personnages autorisés par joueurs.",
            inline=False,
        )
        embed.add_field(
            name="4️⃣ - Tag automatique",
            value="Permet d'activer un tag avant le nom du personnage, préconfiguré.",
            inline=False,
        )
        embed.add_field(
            name="5️⃣ - Token HRP",
            value="Permet de régler le token pour le HRP.",
            inline=False,
        )
        embed.add_field(
            name="6️⃣ - Activation | Désactivation des Personae",
            value="Permet de désactiver/activer de manière générale les Personae.",
            inline=False,
        )
        embed.set_footer(
            text="Cliquez sur la réaction pour choisir !\n ❌ permet d'annuler. "
        )
        q = await ctx.send(embed)
        i = 0
        while emoji[i] != "✅":
            await q.add_reaction(emoji[i])
            i += 1
        reaction, user = await self.bot.wait_for(
            "reaction_add", timeout=300, check=checkValid
        )
        if reaction.emoji == "1️⃣":
            await q.clear_reactions()
            menu_channel = discord.Embed(title=embed.title, color=embed.color)
            menu_channel.add_field(
                name="1️⃣ - Ajouter des channels.",
                value="Permet de rajouter des channels (ou catégorie) dans la configuration, sans effacer les précédents.",
                inline=False,
            )
            menu_channel.add_field(
                name="2️⃣ - Supprimer des channels",
                value="Permet de supprimer un channel (ou une catégorie) de la configuration.",
                inline=False,
            )
            menu_channel.add_field(
                name="3️⃣ - Reset",
                value="Permet d'effacer tous les channels (et/ou catégories) enregistré. ",
                inline=False,
            )
            await q.edit(embed=menu_channel)
            await q.add_reaction("1️⃣")
            await q.add_reaction("2️⃣")
            await q.add_reaction("3️⃣")
            await q.add_reaction("❌")
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=300, check=checkValid
            )
            if reaction.emoji == "1️⃣":
                await q.delete()
                await webhook.chanHRP_add(ctx, self.bot)
                return
            elif reaction.emoji == "2️⃣":
                await q.delete()
                await webhook.chanHRP_rm(ctx, self.bot)
                return
            elif reaction.emoji == "3️⃣":
                await q.delete()
                db = sqlite3.connect("owlly.db", timeout=3000)
                c = db.cursor()
                sql = "UPDATE chanRP set chanRP=? WHERE idS=?"
                var = ("0", ctx.guild.id)
                c.execute(sql, var)
                db.commit()
                c.close()
                db.close()
                q = await ctx.send(
                    "Il n'y a plus aucun channel enregistrés. Voulez-vous en enregistrer ?"
                )
                await q.add_reaction("✅")
                await q.add_reaction("❌")
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=300, check=checkValid
                )
                if reaction.emoji == "✅":
                    await webhook.chanHRP_add(ctx, self.bot)
                    return
                else:
                    await q.delete()
                    await ctx.send(
                        "Aucun channel n'est configuré.\n Fin de la configuration."
                    )
                    return
        elif reaction.emoji == "2️⃣":
            await q.clear_reactions()
            menu_sticky = discord.Embed(title=embed.title, color=embed.color)
            menu_sticky.add_field(
                name="1️⃣ - Activation",
                value="Permet d'activer le mode sticky.",
                inline=False,
            )
            menu_sticky.add_field(
                name="2️⃣ - Désactivation",
                value="Permet de désactiver le mode sticky.",
                inline=False,
            )
            await q.edit(embed=menu_sticky)
            await q.add_reaction("1️⃣")
            await q.add_reaction("2️⃣")
            await q.add_reaction("❌")
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=300, check=checkValid
            )
            if reaction.emoji == "1️⃣":
                await q.delete()
                await webhook.sticky(ctx, self.bot, "0")
                return
            elif reaction.emoji == "2️⃣":
                await q.delete()
                await webhook.sticky(ctx, self.bot, "1")
                return
            else:
                await q.delete()
                await ctx.send("Annulation", delete_after=30)
                return
        elif reaction.emoji == "3️⃣":
            await q.clear_reactions()
            menu = discord.Embed(title=embed.title, color=embed.color)
            menu.add_field(
                name="1️⃣ - Désactivation",
                value="Permet de désactiver la limite.",
                inline=False,
            )
            menu.add_field(
                name="2️⃣ - Changement",
                value="Permet d'éditer la limite.",
                inline=False,
            )
            await q.edit(embed=embed)
            await q.add_reaction("1️⃣")
            await q.add_reaction("2️⃣")
            await q.add_reaction("❌")
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=300, check=checkValid
            )
            if reaction.emoji == "1️⃣":
                await q.delete()
                await webhook.maxDC(ctx, self.bot, "0")
                return
            elif reaction.emoji == "2️⃣":
                await q.delete()
                await webhook.maxDC(ctx, self.bot, "1")
                return
            else:
                await q.delete()
                await ctx.send("Annulation", delete_after=30)
                return
        elif reaction.emoji == "4️⃣":
            await q.clear_reactions()
            menu = discord.Embed(
                title=embed.title,
                color=embed.color,
                description="Les tags sont des mots préconfigurés (nom du serveur / nom du joueur / ID du Persona) se plaçant dans le nom du Persona, afin de donner des informations à propos du joueur; serveur ; ou id.",
            )
            menu.add_field(
                name="1️⃣ - Modification du Tag",
                value="Permet de modifier ou d'ajouter un tag.",
            )
            menu.add_field(
                name="2️⃣ - Suppression du tag", value="Permet de supprimer le tag."
            )
            await q.edit(embed=menu)
            await q.add_reaction("1️⃣")
            await q.add_reaction("2️⃣")
            await q.add_reaction("❌")
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=300, check=checkValid
            )
            if reaction.emoji == "1️⃣":
                await q.delete()
                await webhook.tag_Personae(ctx, self.bot, "1")
            elif reaction.emoji == "2️⃣":
                await q.delete()
                await webhook.tag_Personae(ctx, self.bot, "0")
            else:
                await q.delete()
                await ctx.send("Annulation, aucun changement effectué.")
                return
        elif reaction.emoji == "5️⃣":
            await q.clear_reactions()
            menu = discord.Embed(title=embed.title, color=embed.color)
            menu.add_field(
                name="1️⃣ - Supprimer le pattern",
                value="Permet de désactiver la fonction.",
                inline=False,
            )
            menu.add_field(
                name="2️⃣ - Changer le pattern",
                value="Permet d'éditer le pattern HRP.",
                inline=False,
            )
            await q.edit(embed=menu)
            await q.add_reaction("1️⃣")
            await q.add_reaction("2️⃣")
            await q.add_reaction("❌")
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=300, check=checkValid
            )
            if reaction.emoji == "1️⃣":
                await q.delete()
                await webhook.tokenHRP(ctx, self.bot, "0")
                await ctx.send(
                    "Suppression du pattern, la fonction n'est plus configurée."
                )
                return
            elif reaction.emoji == "2️⃣":
                await q.delete()
                await webhook.tokenHRP(ctx, self.bot, "1")
                await ctx.send("Changement effectué")
                return
            else:
                await q.delete()
                await ctx.send("Annulation.")
                return
        elif reaction.emoji == "6️⃣":
            await q.delete()
            db = sqlite3.connect("owlly.db", timeout=3000)
            c = db.cursor()
            sql="SELECT maxDC FROM SERVEUR WHERE idS = ?"
            c.execute(sql, (ctx.guild.id,))
            maxDC= c.fetchone()
            if maxDC is None:
                maxDC="0"
            else:
                maxDC= maxDC[0]
            if maxDC != -1:
                phrase="Désactivation des Personae"
                config=-1
            elif maxDC == -1:
                phrase="Activation des Personae"
                config=0
            q=await ctx.send(f"{phrase}\nSouhaitez-vous continuer ?")
            await q.add_reaction("✅")
            await q.add_reaction("❌")
            reaction, user = await self.bot.wait_for("add_reaction", timeout=300, check=checkValid)
            if reaction.emoji == "✅":
                await q.delete()
                utils = self.bot.get_cog("DB_utils")
                await utils.init_value("maxDC", "SERVEUR", "idS", config, ctx.guild.id)
                await ctx.send("Modification enregistrée.")
                return
            else:
                await q.delete()
                await ctx.send("Annulation", delete_after=30)
                return
        else:
            await q.delete()
            await ctx.send("Annulation !", delete_after=30)
            return

    @commands.has_permissions(administrator=True)
    @commands.command(
        help="Permet de configurer le tag des Persona.",
        description="Les tags sont des patterns préconfigurés qui permettent d'indiquer diverses informations quant à l'utilisateur du Persona.",
        brief="Configuration des tags de Personae.",
    )
    async def tag_persona(self, ctx):
        emoji = ["1️⃣", "2️⃣", "3️⃣", "❌"]

        def checkRep(message):
            return (
                message.author == ctx.message.author
                and ctx.message.channel == message.channel
            )

        def checkValid(reaction, user):
            return (
                ctx.message.author == user
                and q.id == reaction.message.id
                and str(reaction.emoji) in emoji
            )

        db = sqlite3.connect("owlly.db", timeout=3000)
        c = db.cursor()
        sql = "SELECT tag FROM SERVEUR WHERE idS = ?"
        c.execute(sql, (ctx.guild.id,))
        tag = c.fetchone()
        if tag is None:
            tag = "0"
            msg = "Actuellement, aucun tag n'est configuré."
        else:
            tag = tag[0]
            if tag != "0":
                msg = f"Actuellement, votre tag est {tag}"
            else:
                msg = f"Actuellement, aucun tag n'est configuré."
        q = await ctx.send(f"{msg}\n Voulez-vous changer les paramètres ?")
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for(
            "reaction_add", timeout=300, check=checkValid
        )
        if reaction.emoji == "✅":
            if tag != "0":
                await ctx.send("Modification du tag")
                await webhook.tag(ctx, self.bot, "1")
            else:
                await ctx.send("1️⃣ - Modification du tag\n2️⃣ - Suppression du tag")
                await q.add_reaction("1️⃣")
                await q.add_reaction("2️⃣")
                await q.add_reaction("❌")
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=300, check=checkValid
                )
                if reaction.emoji == "1️⃣":
                    await q.delete()
                    await webhook.tag_Personae(ctx, self.bot, "1")
                    return
                elif reaction.emoji == "2️⃣":
                    await q.delete()
                    await webhook.tag_Personae(ctx, self.bot, "0")
                    await ctx.send("Changement effectué, la fonction est désactivée.")
                    return
                else:
                    await q.delete()
                    await ctx.send("Annulation, aucun changement effectué.")
                    return
        else:
            await q.delete()
            await ctx.send("Annulation, aucun changement effectué.")
            return

    @commands.has_permissions(administrator=True)
    @commands.command(
        help="Active ou désactive les Personae sur tout le serveur. Permet aussi de configurer le maximum de Personae.",
        brief="Activation/désactivation des Personae",
        usage="<0 : Désactivation> <1 : Activation>  "
    )
    async def active_persona(self, ctx, config):
        if config == "1":
            await webhook.maxDC(ctx, self.bot, "1")
        elif config == "1":
            await webhook.maxDC(ctx, self.bot, "-1")

def setup(bot):
    bot.add_cog(CogAdmins(bot))
