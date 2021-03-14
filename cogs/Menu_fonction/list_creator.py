import discord
from discord.ext import commands, tasks
from discord.utils import get
from typing import Optional
import sqlite3
import re
from discord import Colour


def bot():
    def getprefix(bot, message):
        db = sqlite3.connect("owlly.db", timeout=3000)
        c = db.cursor()
        prefix = "SELECT prefix FROM SERVEUR WHERE idS = ?"
        c.execute(prefix, (int(message.guild.id), ))
        prefix = c.fetchone()
        if prefix is None:
            prefix = "?"
            sql = "INSERT INTO SERVEUR (prefix, idS) VALUES (?,?)"
            var = ("?", message.guild.id)
            c.execute(sql, var)
            db.commit()
        else:
            prefix = prefix[0]
        c.close()
        db.close()
        return prefix
    intents = discord.Intents(
        messages=True, guilds=True, reactions=True, members=True)
    bot = commands.bot(command_prefix=getprefix, intents=intents)
    return bot

def list_ticket(ctx):
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    idS=ctx.guild.id
    sql="SELECT * FROM TICKET WHERE idS=?"
    c.execute(sql, (idS,))
    info=c.fetchall()
    for i in info:
        msg=f"▫ {i[0]} dans <#{i[1]}> :\n"
        cat_name=get(ctx.guild.categories, id=i[2])
        msg=msg+f" Catégorie : {cat_name}"
        if i[8] == "1":
            chan_name="Nom libre"
        else:
            if i[8] =="2":
                chan_name="Nom du personnage"
            else:
                chan_name=i[8]
            nb = i[3]
            if nb.isnumeric():
                limit=i[5]
                modulo= i[4]
                msg=msg+f"\nNom : {nb} : {chan_name}\n Limitation : {limit}\n Augmentation : {modulo}"
            else:
                msg=msg+f"\nNom : {nb} : {chan_name}"
        msg=msg+"\n\n"
    return msg