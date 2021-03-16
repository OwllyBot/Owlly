import discord
from discord.ext import commands, tasks
from discord.utils import get
import sqlite3
from discord import NotFound

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
            msg = f"⭐ {i[0]} dans <#{i[1]}> :\n"
            cat_name=get(ctx.guild.categories, id=i[2])
            msg=msg+f"\tCatégorie : {cat_name.name}"
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
                    msg = msg + \
                        f"\n\t▫️ Nom : {nb} {chan_name}\n\t◽ Limitation : {limit}\n\t◽ Augmentation : {modulo}"
                else:
                    msg = msg+f"\n\t▫️ Nom : {nb} : {chan_name}"
            msg=msg+"\n\n"
    else:
        msg = "Il n'y a pas de ticket dans ce serveur."
    return msg

def list_category(ctx):
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    idS=ctx.guild.id
    SQL="SELECT * FROM CATEGORY WHERE idS=?"
    c.execute(SQL,(idS,))
    info=c.fetchall()
    msg=""
    print(info)
    if len(info) != 0:
        for i in info:
            msg = f"⭐ {i[0]} dans <#{i[1]}> :\n"
            cat_list=i[2].split(",")
            msg_cat=[]
            for k in cat_list:
                cat_name = get(ctx.guild.categories, id=int(k))
                if cat_name is None:
                    continue
                else:
                    msg_cat.append(cat_name.name)
            msg_cat_str="\n\t\t🔹".join(msg_cat)
            msg = msg+f"\t▫️ Catégories :\n\t\t🔹{msg_cat_str}"
            config=i[4]
            if config==1:
                para = "\t▫️ Nom : Libre"
            else:
                para = "\t▫️ Nom : Nom du personnage"
            msg = msg+f"\n{para}"
        msg=msg+"\n\n"
    else:
        msg= "Il n'y a pas de billet dans ce serveur."
    return msg

    
