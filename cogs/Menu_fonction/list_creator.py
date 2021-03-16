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

def list_category(ctx):
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    idS=ctx.guild.id
    SQL="SELECT * FROM CATEGORY WHERE idS=?"
    c.execute(SQL,(idS,))
    info=c.fetchall()
    msg=""
    if len(info) != 0:
        for i in info:
            msg = f"⭐ {i[0]} dans <#{i[1]}> :\n"
            cat_list=i[2].split(",")
            msg_cat=[]
            for i in cat_list:
                cat_name=get(ctx.guild.categories, id=int(i))
                msg_cat.append(cat_name)
            msg_cat_str="       \n🔹".join(msg_cat)
            msg=msg+f"\n    ◽ Catégories :\n{msg_cat_str}"
            config=i[4]
            if config==1:
                para = "    ◽ Nom : Libre"
            else:
                para = "    ◽ Nom : Nom du personnage"
        msg=msg+"\n\n"



    
