import discord
from discord.ext import commands, tasks
from discord.utils import get
import sqlite3

def list_ticket(ctx):
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    idS=ctx.guild.id
    sql="SELECT * FROM TICKET WHERE idS=?"
    c.execute(sql, (idS,))
    info=c.fetchall()
    msg=""
    if len(info) != 0:
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
    else:
        msg = "Il n'y a pas de ticket dans ce serveur."
    return msg