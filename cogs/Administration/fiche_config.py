import discord
import ast
import os
import sqlite3
from collections import OrderedDict


async def edit_update(ctx, dm, chartype, champ, old):
    idS = ctx.guild.id
    f = open(
        f"src/fiche/{dm.id}_{chartype}_{dm.name}_{ctx.guild.id}.txt",
        "r",
        encoding="utf-8",
    )
    data = f.readlines()
    f.close()
    if len(data) > 0:
        data = "".join(data)
        perso = ast.literal_eval(data)
        save = open(
            f"src/fiche/Saves_files/{dm.id}_{chartype}_{dm.name}_{idS}.txt",
            "w",
            encoding="utf-8",
        )
        save.write(str(perso))
        save.close()
    else:
        try:
            os.path.isfile(
                f"src/fiche/Saves_files/{dm.id}_{chartype}_{dm.name}_{idS}.txt"
            )
            save = open(
                f"src/fiche/Saves_files/{dm.id}_{chartype}_{dm.name}_{idS}.txt",
                "r",
                encoding="utf-8",
            )
            save_data = save.readlines()
            save.close()
            if len(save_data) > 0:
                save_data = "".join(save_data)
                perso = ast.literal_eval(save_data)
            else:
                perso = {}
        except OSError:
            perso = {}
    f = open(f"src/fiche/{dm.id}_{chartype}_{dm.name}_{idS}.txt", "w", encoding="utf-8")
    perso_new = {}
    for k, v in perso.keys():
        if k != old:
            perso_new.update({k.lower: v})
        else:
            perso_new.update({champ.lower(): {v}})
    f.write(str(perso_new))
    f.close()


async def add_update(ctx, dm, chartype, champ, part):
    idS = ctx.guild.id
    f = open(
        f"src/fiche/{dm.id}_{chartype}_{dm.name}_{ctx.guild.id}.txt",
        "r",
        encoding="utf-8",
    )
    data = f.readlines()
    f.close()
    if len(data) > 0:
        data = "".join(data)
        perso = ast.literal_eval(data)
        save = open(
            f"src/fiche/Saves_files/{dm.id}_{chartype}_{dm.name}_{idS}.txt",
            "w",
            encoding="utf-8",
        )
        save.write(str(perso))
        save.close()
    else:
        try:
            os.path.isfile(
                f"src/fiche/Saves_files/{dm.id}_{chartype}_{dm.name}_{idS}.txt"
            )
            save = open(
                f"src/fiche/Saves_files/{dm.id}_{chartype}_{dm.name}_{idS}.txt",
                "r",
                encoding="utf-8",
            )
            save_data = save.readlines()
            save.close()
            if len(save_data) > 0:
                save_data = "".join(save_data)
                perso = ast.literal_eval(save_data)
            else:
                perso = {}
        except OSError:
            perso = {}
    f = open(f"src/fiche/{dm.id}_{chartype}_{dm.name}_{idS}.txt", "w", encoding="utf-8")
    d = OrderedDict()
    db = sqlite3.connect("src/owlly.db", timeout=3000)
    c = db.cursor()
    if part == "physique":
        sql = "SELECT champ_physique FROM FICHE WHERE idS=?"
    else:
        sql = "SELECT champ_general FROM FICHE WHERE idS = ?"
    c.execute(sql, (idS,))
    champ_part = c.fetchone()
    champ_part = champ[0].split(",")
    index = champ_part[-1]
    for k, v in perso.items():
        if k == index:
            d[champ] = "NA"
        d[k] = v
    perso_new = dict(d)
    f.write(str(perso_new))
    f.close()
    c.close()
    db.close()


async def part_fiche(bot, ctx, type):
    def checkRep(message):
        return (
            message.author == ctx.message.author
            and ctx.message.channel == message.channel
        )

    q = await ctx.send(
        f"Merci de rentrer les champs que vous souhaitez pour la partie présentation **{type}**.\n `cancel` pour annuler et `stop` pour valider.\n Utiliser le symbole `*` pour marquer l'obligation du champ, `$` pour les liens et `&` pour les images."
    )
    champs = []
    while True:
        general_rep = await bot.wait_for("message", timeout=300, check=checkRep)
        general_champ = general_rep.content
        if general_champ.lower() == "stop":
            await ctx.send("Validation en cours !", delete_after=5)
            await general_rep.delete()
            break
        elif general_champ.lower() == "cancel":
            await general_rep.delete()
            await ctx.send("Annulation !", delete_after=30)
            await q.delete()
            return
        else:
            await general_rep.add_reaction("✅")
            general_champ = general_champ.replace("'", "\\'")
            champs.append(general_champ.capitalize())
        await general_rep.delete(delay=10)
    general = ",".join(champs)
    await q.delete()
    return general


def dict_form(dict):
    champ = ""
    phrase = ""
    for k, v in dict.items():
        phrase = f"__{k.capitalize()}__ : \n "
        for i in v:
            champ = champ + f"  ▫️ {i}\n"
        phrase = phrase + champ + "\n\n"
    return phrase
