import discord
from discord.colour import Color
from discord.ext import commands, tasks
from discord.utils import get
from typing import Optional
import sqlite3
import re
from discord import Colour
from discord.ext.commands import ColourConverter
from cogs.chan_creator import config_creators as cfg
from cogs.chan_creator import edit_creator as edit
from cogs.chan_creator import list_creator as listing


class ChanCreator(
    commands.Cog,
    name="Créateur",
    description="Affiche le menu afin de permettre la création, l'édition mais aussi lister les créateurs de tickets.",
):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @commands.command(
        aliases=["tick"],
        brief="Débute la configuration des tickets",
        help="Permet de créer la configuration des tickets avec divers paramètres, notamment ceux le numéros dans le nom, ainsi que le moment où ce numéros va se reset.",
        description="Configuration pour une seule catégorie.",
    )
    async def ticket(self, ctx):
        await ctx.message.delete()
        emoji = ["1️⃣", "2️⃣", "3️⃣", "❌"]

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

        embed = discord.Embed(title="Menu des tickets", color=Color.blurple())
        embed.add_field(
            name="1️⃣ - Création",
            value="Créer un nouveau créateur de ticket.",
            inline=False,
        )
        embed.add_field(
            name="2️⃣ - Modification",
            value="Modifier un créateur de ticket.",
            inline=False,
        )
        embed.add_field(
            name="3️⃣ - Liste",
            value="Afficher la liste des paramètres d'un ticket.",
            inline=False,
        )
        embed.set_footer(
            text="Cliquez sur la réaction pour choisir !\n❌ Permet de quitter le menu."
        )
        q = await ctx.send(embed=embed)
        await q.add_reaction("1️⃣")
        await q.add_reaction("2️⃣")
        await q.add_reaction("3️⃣")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for(
            "reaction_add", timeout=300, check=checkValid
        )
        if reaction.emoji == "1️⃣":
            await q.delete()
            await cfg.create_ticket(self, ctx, self.bot)
        elif reaction.emoji == "2️⃣":
            await q.delete()
            q = await ctx.send("Merci de donner l'ID du créateur à modifier.")
            rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
            if rep.content.lower() == "stop":
                await q.delete()
                await ctx.send("Annulation", delete_after=30)
                await rep.delete()
                return
            elif rep.content.isnumeric():
                idM = int(rep.content)
                db = sqlite3.connect("owlly.db", timeout=3000)
                c = db.cursor()
                sql = "SELECT idM FROM TICKET where idM=?"
                c.execute(sql, (idM,))
                check = c.fetchone()
                if check is not None:
                    await edit.edit_ticket(ctx, idM, self.bot)
                else:
                    await q.delete()
                    await rep.delete()
                    await ctx.send(
                        "Il y a une erreur : Cet ID n'existe pas dans la base de donnée.",
                        delete_after=30,
                    )
                    return
            else:
                await q.delete()
                await rep.delete()
                await ctx.send(
                    "Il y a une erreur : La valeur n'est pas numérique", delete_after=30
                )
                return
        elif reaction.emoji == "3️⃣":
            await q.delete()
            affichage = listing.list_ticket(ctx)
            await ctx.send(affichage)
        elif reaction.emoji == "❌":
            await q.delete()
            await ctx.send("Annulation", delete_after=30)
            return

    @commands.has_permissions(administrator=True)
    @commands.command(
        aliases=["cat", "categories", "bill", "billet"],
        brief="Configuration d'un créateur pour plusieurs catégorie",
        help="Permet de créer divers channels dans plusieurs catégories qui seront recherchées sur le serveur. La configuration offre une option pour autoriser ou nom le nommage automatique des channels.",
        description="Pour plusieurs catégories, 9 au maximum.",
    )
    async def category(self, ctx):
        emoji = ["1️⃣", "2️⃣", "3️⃣", "❌"]
        await ctx.message.delete()

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

        embed = discord.Embed(title="Menu des billets", color=Color.blurple())
        embed.add_field(
            name="1️⃣ - Création",
            value="Créer un nouveau créateur de billet.",
            inline=False,
        )
        embed.add_field(
            name="2️⃣ - Modification",
            value="Modifier un créateur de billet.",
            inline=False,
        )
        embed.add_field(
            name="3️⃣ - Liste",
            value="Afficher la liste des paramètres d'un billet.",
            inline=False,
        )
        embed.set_footer(
            text="Cliquez sur la réaction pour choisir !\n❌ Permet de quitter le menu."
        )
        q = await ctx.send(embed=embed)
        await q.add_reaction("1️⃣")
        await q.add_reaction("2️⃣")
        await q.add_reaction("3️⃣")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for(
            "reaction_add", timeout=300, check=checkValid
        )
        if reaction.emoji == "1️⃣":
            await q.delete()
            await cfg.create_category(self, ctx, self.bot)
        elif reaction.emoji == "2️⃣":
            await q.delete()
            q = await ctx.send("Merci de donner l'ID du créateur à modifier.")
            rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
            if rep.content.lower() == "stop":
                await q.delete()
                await ctx.send("Annulation", delete_after=30)
                await rep.delete()
                return
            elif rep.content.isnumeric():
                idM = int(rep.content)
                db = sqlite3.connect("owlly.db", timeout=3000)
                c = db.cursor()
                sql = "SELECT idM FROM CATEGORY where idM=?"
                c.execute(sql, (idM,))
                check = c.fetchone()
                if check is not None:
                    await edit.edit_category(ctx, idM, self.bot)
                else:
                    await q.delete()
                    await rep.delete()
                    await ctx.send(
                        "Il y a une erreur : Cet ID n'existe pas dans la base de donnée.",
                        delete_after=30,
                    )
                    return
            else:
                await q.delete()
                await rep.delete()
                await ctx.send(
                    "Il y a une erreur : La valeur n'est pas numérique", delete_after=30
                )
                return
        elif reaction.emoji == "3️⃣":
            await q.delete()
            affichage = listing.list_category(ctx)
            await ctx.send(affichage)
        elif reaction.emoji == "❌":
            await q.delete()
            await ctx.send("Annulation", delete_after=30)
            return

    @commands.has_permissions(administrator=True)
    @commands.command(
        aliases=["count", "edit_count"],
        brief="Permet de changer le compteur des ticket",
        help="Permet de reset, ou changer manuellement le numéro d'un créateur de ticket.",
        usage="nombre id_message_createur",
    )
    async def recount(self, ctx, arg, ticket_id):
        await ctx.message.delete()
        db = sqlite3.connect("owlly.db", timeout=3000)
        c = db.cursor()
        search_db = "SELECT num FROM TICKET WHERE idM=?"
        sql = "UPDATE TICKET SET num = ? WHERE idM=?"
        search_regex_arg = re.search(
            "(?:(?P<channel_id>[0-9]{15,21})-)?(?P<message_id>[0-9]{15,21})$", str(arg)
        )
        if search_regex_arg is None:
            search_regex_arg = re.search(
                "(?:(?P<channel_id>[0-9]{15,21})-)?(?P<message_id>[0-9]{15,21})$",
                str(ticket_id),
            )
            if search_regex_arg is None:
                await ctx.send(
                    "Aucun de vos arguments ne correspond à l'ID du message du créateur de ticket...",
                    delete_after=30,
                )
                c.close()
                db.close()
                return
            else:
                arg = int(arg)
                ticket_id = int(ticket_id)
        else:
            silent = int(ticket_id)
            ticket_id = int(arg)
            arg = silent
            c.execute(search_db, (ticket_id,))
            search = c.fetchone()
            if search is None:
                await ctx.send("Aucun ne ticket ne possède ce numéro.")
                c.close()
                db.close()
                return
            else:
                var = (arg, (ticket_id))
                c.execute(sql, var)
                db.commit()
                c.close()
                db.close()
                await ctx.send(f"Le compte a été fixé à : {arg}")


def setup(bot):
    bot.add_cog(ChanCreator(bot))
