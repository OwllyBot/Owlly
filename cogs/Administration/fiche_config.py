import discord
import ast
import os
import sqlite3
from collections import OrderedDict
import unidecode


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


def search_autre(du, val, d):
    for k, v in du.items():
        for clef in d:
            for i in v:
                if i == val:
                    return clef
    return "False"


async def delete_part(ctx, cl, bot):
    db = sqlite3.connect("src/owlly.db", timeout=3000)
    c = db.cursor()

    def checkRep(message):
        return (
            message.author == ctx.message.author
            and ctx.message.channel == message.channel
        )

    sql = "SELECT champ_general, champ_physique, champ_autre FROM FICHE WHERE idS=?"
    c.execute(sql, (cl,))
    champs = c.fetchone()
    gen_msg = "".join(champs[0]).split(",")
    gen_msg = ", ".join(gen_msg)
    phys_msg = "".join(champs[1]).split(",")
    phys_msg = ", ".join(phys_msg)
    autre = ast.literal_eval(champs[2])
    autres_msg = dict_form(autre)
    msg_full = (
        f"**Général** : \n {gen_msg} \n\n **Physique** : \n {phys_msg}\n\n {autres_msg}"
    )
    q = await ctx.send(f"{msg_full} Quel champ voulez-vous supprimer ?")
    rep = await bot.wait_for("message", timeout=300, check=checkRep)
    if rep.content.lower() == "stop":
        await q.delete()
        await rep.delete()
        await ctx.send("Annulation", delete_after=30)
        return
    else:
        champ = unidecode.unidecode(rep.content.lower())

    if champs[0] is not None:
        champ_general = champs[0].split(",")
        champ_physique = champs[1].split(",")
    else:
        await ctx.send(
            "Vous n'avez pas de fiche configurée. Vous devez d'abord en créer une.",
            delete_after=30,
        )
        await q.delete()
        await rep.delete()
        return
    gen_uni = [unidecode.unidecode(i.lower()) for i in champ_general]
    phys_uni = [unidecode.unidecode(i.lower()) for i in champ_physique]
    autre_uni = {}
    for k, v in autre:
        autre_uni.update(
            {
                unidecode.unidecode(k.lower()): [
                    unidecode.unidecode(i.lower()) for i in v
                ]
            }
        )
    search = search_autre(autre_uni, champ, autre)
    if champ in gen_uni:
        for i in range(0, len(gen_uni)):
            if gen_uni[i] == champ:
                del champ_general[i]
    elif champ in phys_uni:
        for i in range(0, len(phys_uni)):
            if phys_uni[i] == champ:
                del champ_physique[i]
    elif search != "False":
        autre_list = autre[search]
        for i in range(0, len(autre_list)):
            if autre_list[i] == champ:
                del autre_list[i]
        autre[search] = autre_list
    else:
        await ctx.send("Ce champ n'existe pas !", delete_after=30)
        return
    champ_general = ",".join(champ_general)
    champ_physique = ",".join(champ_physique)
    autre_champ = str(autre)
    sql = "UPDATE FICHE SET champ_general = ?, champ_physique = ?, champ_autre=? WHERE idS=?"
    var = (champ_general, champ_physique, autre, cl)
    c.execute(sql, var)
    db.commit()
    await rep.delete()
    await q.delete()
    await ctx.send(f"Le Champ : {champ} a bien été supprimé !")
    return "Deleted", champ
