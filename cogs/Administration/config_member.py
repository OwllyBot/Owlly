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


async def roliste_init(ctx, bot, type_db, role):
    db = sqlite3.connect("src/owlly.db", timeout=3000)
    c = db.cursor()
    sql = "UPDATE SERVEUR SET " + type_db + " = ? WHERE idS = ?"
    role_list = []
    phrase = []
    if (len(role)) > 1:
        for i in role:
            try:
                roles = await commands.RoleConverter().convert(ctx, i)
                role_list.append(str(roles.id))
                phrase.append(roles.name)
            except RoleNotFound:
                pass
    else:
        try:
            roles = await commands.RoleConverter().convert(ctx, role[0])
            role_str = str(roles.id)
            phrase.append(roles.name)
        except RoleNotFound:
            pass
    if len(phrase) > 1:
        phrase = ", ".join(phrase)
    else:
        phrase = phrase[0]
    if (len(phrase)) == "0":
        await ctx.send("Erreur ! Aucun rôle n'a été reconnu.")
        return
    await ctx.send(
        f"Les rôles {phrase} ont bien été enregistré dans la base de données"
    )
    if len(role_list) > 0:
        role_str = ",".join((role_list))
    var = (role_str, ctx.guild.id)
    c.execute(sql, var)
    db.commit()
    c.close()
    db.close()


async def role_init(ctx, *role: discord.Role, bot):
    db = sqlite3.connect("src/owlly.db", timeout=3000)
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
    await ctx.send(
        f"Les rôles {phrase} ont bien été enregistré dans la base de données"
    )
    db.commit()
    c.close()
    db.close()


async def init_role_rm(ctx, *role: discord.Role, bot):
    db = sqlite3.connect("src/owlly.db", timeout=3000)
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
    await ctx.send(
        f"Les rôles {phrase} ont bien été enregistré dans la base de données"
    )
    db.commit()
    c.close()
    db.close()


async def inscription_role(bot, ctx, type_db):
    db = sqlite3.connect("src/owlly.db", timeout=3000)
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
            return (
                message.author == ctx.message.author
                and ctx.message.channel == message.channel
            )

        emoji = ["1️⃣", "2️⃣", "3️⃣", "✅", "❌"]
        if role_list is not None:
            role_list = role_list[0].split(",")
            role_phrase = ""
            for i in role_list:
                try:
                    role_phrase = (
                        str(await commands.RoleConverter().convert(ctx, i))
                        + " / "
                        + role_phrase
                    )
                except RoleNotFound:
                    role_phrase = "Role Supprimé : id - " + i + " / " + role_phrase
            q = await ctx.send(
                f"Vous avez actuellement des rôles enregistrés : {role_phrase}\n Voulez-vous :\n 1️⃣ - Rajouter un rôle \n 2️⃣ - Supprimer un rôle \n 3️⃣ - Recommencer votre inscription \n ❌ - Annuler. "
            )
            for i in emoji:
                if i != "✅":
                    await q.add_reaction(i)
            reaction, user = await bot.wait_for(
                "reaction_add", timeout=300, check=checkValid
            )
            if reaction.emoji == "1️⃣":
                await q.clear_reactions()
                await q.edit(content="Quel est le rôle que vous voulez rajouter ?")
                rep = await bot.wait_for("message", timeout=300, check=checkRep)
                if rep.content.lower() == "stop":
                    await ctx.send("Annulation")
                    await q.delete()
                else:
                    try:
                        add_role = await commands.RoleConverter().convert(
                            ctx, rep.content.lower()
                        )
                    except RoleNotFound:
                        await ctx.send("Erreur ! Ce rôle n'existe pas.")
                        await q.delete()
                        await rep.delete()
                        return
                    if str(add_role.id) not in role_list:
                        role_list.append(str(add_role.id))
                        role_list_str = ",".join(role_list)
                        sql = "UPDATE SERVEUR SET " + type_db + " = ? WHERE idS = ?"
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
                rep = await bot.wait_for("message", timeout=300, check=checkRep)
                if rep.content.lower() == "stop":
                    await ctx.send("Annulation")
                    await q.delete()
                else:
                    try:
                        rm_role = await commands.RoleConverter().convert(
                            ctx, rep.content.lower()
                        )
                        rm = str(rm_role.id)
                    except RoleNotFound:
                        rm = str(rep.content.lower())
                    if rm in role_list:
                        role_list.remove(rm)
                        role_list_str = ",".join(role_list)
                        sql = f"UPDATE SERVEUR SET " + type_db + " = ? WHERE idS = ?"
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
                await q.edit(
                    content="Merci d'envoyer les rôles que vous voulez rajouter."
                )
                rep = await bot.wait_for("message", timeout=300, check=checkRep)
                roliste = rep.content.split(" ")
                await roliste_init(ctx, roliste, type_db)
            else:
                await q.delete()
                await ctx.send("Annulation", delete_after=30)
                return
