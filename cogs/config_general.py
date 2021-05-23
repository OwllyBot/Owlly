import discord
from discord import role
from discord.ext import commands, tasks
import sqlite3
import re
from typing import Optional
from discord.ext.commands import CommandError
from discord.ext.commands.errors import RoleNotFound
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

    async def roliste_init(self, ctx, role, type_db):
        db = sqlite3.connect("owlly.db", timeout=3000)
        c = db.cursor()
        type_db=type_db
        sql = "UPDATE SERVEUR SET "+type_db+" = ? WHERE idS = ?"
        role_list = []
        if (len(role)) > 1:
            for i in role:
                try:
                    roles = await commands.RoleConverter().convert(ctx, i)
                    role_list.append(str(roles.id))
                except RoleNotFound:
                    pass
        else:
            try:
                role_str = await commands.RoleConverter().convert(ctx, role[0])
                role_str = str(role_str.id)
            except RoleNotFound:
                pass
        phrase = []
        for i in role:
            try:
                roles = await commands.RoleConverter().convert(ctx, i)
                phrase.append(roles.name)
            except RoleNotFound:
                pass
        phrase = ", ".join(phrase)
        if (len(phrase)) == "0":
            await ctx.send("Erreur ! Aucun rôle n'a été reconnu.")
            return
        await ctx.send(f"Les rôles {phrase} ont bien été enregistré dans la base de données")
        role_str = ",".join((role_list))
        var = (role_str, ctx.guild.id)
        c.execute(sql, var)
        db.commit()
        c.close()
        db.close()

    @commands.has_permissions(administrator=True)
    @commands.command(
        help="Permet d'enregistrer / réenregistrer la liste des rôles données par la commandes member, sans passer par le menu de configuration.",
        brief="Enregistrement de rôles pour la commande member, sans passer par le menu.",
        usage="@mention/ID des rôles à enregistrer",
        aliases=["init_role", "assign_init"],
    )
    async def role_init(self, ctx, *role: discord.Role):
        db = sqlite3.connect("owlly.db", timeout=3000)
        c = db.cursor()
        sql = "UPDATE SERVEUR SET roliste = ? WHERE idS = ?"
        role_list = []
        if (len(role)) > 1:
            for i in role:
                role_list.append(str(i.id))
            role_str = ",".join((role_list))
        else:
            role_str = str(role[0].id)
        var = (role_str, ctx.guild.id)
        c.execute(sql, var)
        phrase = []
        for i in role:
            phrase.append(i.name)
        phrase = ", ".join(phrase)
        await ctx.send(f"Les rôles {phrase} ont bien été enregistré dans la base de données")
        db.commit()
        c.close()
        db.close()

    @commands.has_permissions(administrator=True)
    @commands.command(
        help="Permet d'enregistrer / réenregistrer la liste des rôles retirés par la commandes member, sans passer par le menu de configuration.",
        brief="Enregistrement de rôles pour la commande member, sans passer par le menu.",
        usage="@mention/ID des rôles à enregistrer",
        aliases=["init_rm", "assign_rm"],
    )
    async def init_role_rm(self, ctx, *role: discord.Role):
        db = sqlite3.connect("owlly.db", timeout=3000)
        c = db.cursor()
        sql = "UPDATE SERVEUR SET rolerm = ? WHERE idS = ?"
        role_list = []
        if (len(role)) > 1:
            for i in role:
                role_list.append(str(i.id))
            role_str = ",".join((role_list))
        else:
            role_str = str(role[0].id)
        print(role_str)
        var = (role_str, ctx.guild.id)
        c.execute(sql, var)
        phrase = []
        for i in role:
            phrase.append(i.name)
        phrase = ", ".join(phrase)
        await ctx.send(f"Les rôles {phrase} ont bien été enregistré dans la base de données")
        db.commit()
        c.close()
        db.close()

    async def inscription_role(self, ctx, type_db):
        db = sqlite3.connect("owlly.db", timeout=3000)
        c = db.cursor()
        if type_db == "rm":
            sql = "SELECT rolerm FROM SERVEUR WHERE idS =?"
            type_db = "rolerm"
        else:
            sql = "SELECT roliste FROM SERVEUR WHERE idS=?"
            type_db = "roliste"
        c.execute(sql, (ctx.guild.id,))
        role_list = c.fetchone()

        def checkValid(reaction, user):
            return (
                ctx.message.author == user
                and q.id == reaction.message.id
                and (str(reaction.emoji) in emoji)
            )

        def checkRep(message):
            return message.author == ctx.message.author and ctx.message.channel == message.channel

        emoji = ["1️⃣", "2️⃣", "3️⃣", "✅", "❌"]
        if role_list is not None:
            role_list = role_list[0].split(",")
            role_phrase = ""
            for i in role_list:
                try:
                    role_phrase = (
                        str(await commands.RoleConverter().convert(ctx, i)) + " / " + role_phrase
                    )
                except RoleNotFound:
                    role_phrase= "Role Supprimé : id - " + i +" / " + role_phrase
            q = await ctx.send(
                f"Vous avez actuellement des rôles enregistrés : {role_phrase}\n Voulez-vous :\n 1️⃣ - Rajouter un rôle \n 2️⃣ - Supprimer un rôle \n 3️⃣ - Recommencer votre inscription \n ❌ - Annuler. "
            )
            for i in emoji:
                if i != "✅":
                    await q.add_reaction(i)
            reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
            if reaction.emoji == "1️⃣":
                await q.clear_reactions()
                await q.edit(content="Quel est le rôle que vous voulez rajouter ?")
                rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
                if rep.content.lower() == "stop":
                    await ctx.send("Annulation")
                    await q.delete()
                else:
                    try:
                        add_role = await commands.RoleConverter().convert(ctx, rep.content.lower())
                    except RoleNotFound:
                        await ctx.send("Erreur ! Ce rôle n'existe pas.")
                        await q.delete()
                        await rep.delete()
                        return
                    if str(add_role.id) not in role_list:
                        role_list.append(str(add_role.id))
                        role_list_str = ",".join(role_list)
                        sql = "UPDATE SERVEUR SET "+type_db+" = ? WHERE idS = ?"
                        var = (role_list_str, ctx.guild.id)
                        c.execute(sql, var)
                        await q.edit(content="La liste a été mise à jour !")
                        await rep.delete()
                        db.commit()
                        c.close()
                        return
                    else:
                        await ctx.send("Ce rôle est déjà dans la liste !")
                        await q.delete()
                        await rep.delete()
                        return
            elif reaction.emoji == "2️⃣":
                await q.clear_reactions()
                await q.edit(content="Quel est le rôle que vous voulez supprimer ?")
                rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
                if rep.content.lower() == "stop":
                    await ctx.send("Annulation")
                    await q.delete()
                else:
                    try:
                        rm_role = await commands.RoleConverter().convert(ctx, rep.content.lower())
                        rm=str(rm_role.id)
                    except RoleNotFound:
                        rm=str(rep.content.lower())
                    if rm in role_list:
                        role_list.remove(rm)
                        role_list_str = ",".join(role_list)
                        sql = f"UPDATE SERVEUR SET "+type_db+" = ? WHERE idS = ?"
                        var = (role_list_str, ctx.guild.id)
                        c.execute(sql, var)
                        await q.edit(content="La liste a été mise à jour !")
                        await rep.delete()
                        db.commit()
                        c.close()
                        return
                    else:
                        await q.delete()
                        await ctx.send("Ce rôle n'est pas enregistré.")
                        await rep.delete()
                        return
            elif reaction.emoji == "3️⃣":
                await q.clear_reactions()
                await q.edit(content="Merci d'envoyer les rôles que vous voulez rajouter.")
                rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
                roliste = rep.content.split(" ")
                await self.roliste_init(ctx, roliste, type_db)
            else:
                await q.delete()
                await ctx.send("Annulation", delete_after=30)
                return

    @commands.has_permissions(administrator=True)
    @commands.command(
        help="Permet d'inscrire des rôles à retirer lorsqu'un membre est validé.",
        brief="Enregistrement de rôle pour les faire retirer.",
        aliases=["rm_role", "role_remove", "remover_member"],
    )
    async def role_rm(self, ctx):
        await self.inscription_role(ctx, "rm")

    @commands.has_permissions(administrator=True)
    @commands.command(
        help="Assignation des rôles par la commande `member`.",
        brief="Enregistrement de rôles pour la commande member.",
        aliases=["role_config", "roliste_config", "assign"],
    )
    async def roliste(self, ctx):
        await self.inscription_role(ctx, "roliste")

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
    bot.add_cog(CogAdmins(bot))
