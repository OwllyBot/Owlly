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
    part_type = "normal"
    if part == "physique":
        sql = "SELECT champ_physique FROM FICHE WHERE idS=?"
    elif part == "general":
        sql = "SELECT champ_general FROM FICHE WHERE idS = ?"
    elif part == "autre":
        sql = "SELECT champ_autre FROM FICHE WHERE idS = ?"
        part_type = "autre"
    c.execute(sql, (idS,))
    champ_part = c.fetchone()
    if part_type == "normal":
        champ_part = champ[0].split(",")
        index = champ_part[-1]
        perso_new = {}
        if index not in perso.keys():
            perso_new.update({index: "NA"})
    else:
        if champ[0] != "0":
            champ_part = ast.literal_eval(champ[0])
            perso_new = {}
            for k, v in champ_part:
                for i in v:
                    if i not in perso.keys():
                        perso_new.update({i: "NA"})
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
    if champs[2] != "0":
        autre = ast.literal_eval(champs[2])
    else:
        autre = {}
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
        if len(autre_list) == 0:
            del autre[search]
        else:
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


async def delete_autre(ctx, bot, cl):
    def checkRep(message):
        return (
            message.author == ctx.message.author
            and ctx.message.channel == message.channel
        )

    db = sqlite3.connect("src/owlly.db", timeout=3000)
    c = db.cursor()
    sql = "SELECT champ_autre FROM FICHE WHERE idS=?"
    c.execute(sql, (cl,))
    champ_autre = c.fetchone()
    champ_autre = champ_autre[0]
    if champ_autre != "0":
        autre = ast.literal_eval(champ_autre)
        q = await ctx.send("Quel est la partie que vous souhaitez supprimer ?")
        rep = await bot.wait_for("message", timeout=300, check=checkRep)
        if rep.content.lower() == "cancel" or rep.content.lower() == "stop":
            await q.delete()
            await rep.delete()
            await ctx.send("Annulation")
            return
        champ_uni = unidecode.unidecode(rep.content.lower())
        found = "Not"
        for k, v in autre:
            if unidecode.unidecode(k) == champ_uni:
                del autre[k]
                found = "Deleted"
        if found == "Not":
            await ctx.send("Cette partie n'existe pas.")
            await q.delete()
            await rep.delete()
            await ctx.send("Annulation")
            return
        sql = "UPDATE FICHE SET champ_autre= ? WHERE idS= ?"
        var = (autre, cl)
        c.execute(sql, var)
        db.commit()
    c.close()
    db.close()
    return "Deleted", rep.content.lower()


async def edit_champ(ctx, cl, bot):
    db = sqlite3.connect("src/owlly.db", timeout=3000)
    c = db.cursor()

    def checkRep(message):
        return (
            message.author == ctx.message.author
            and ctx.message.channel == message.channel
        )

    save = ""
    sql = "SELECT champ_general, champ_physique, champ_autre FROM FICHE WHERE idS=?"
    c.execute(sql, (cl,))
    champs = c.fetchone()
    if champs is None:
        await ctx.send(
            "Vous n'avez pas de fiche configurée. Vous devez d'abord en créer une.",
            delete_after=30,
        )
        return
    gen_msg = "".join(champs[0]).split(",")
    gen_msg = ", ".join(gen_msg)
    phys_msg = "".join(champs[1]).split(",")
    phys_msg = ", ".join(phys_msg)
    if champs[2] != "0":
        autre = ast.literal_eval(champs[2])
        autres_msg = dict_form(autre)
    else:
        autre = {}
        autres_msg = ""
    msg_full = f"**Général** : \n {gen_msg} \n\n **Physique** : \n {phys_msg}\n\n {autres_msg}\n"
    q = await ctx.send(f"{msg_full} Quel champ voulez-vous éditer ?")
    rep = await bot.wait_for("message", timeout=300, check=checkRep)
    if rep.content.lower() == "stop":
        await q.delete()
        await rep.delete()
        await ctx.send("Annulation", delete_after=30)
        return
    champ = unidecode.unidecode(rep.content.lower())
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
    champ_general = champs[0].split(",")
    gen_uni = [unidecode.unidecode(i.lower()) for i in champ_general]
    champ_physique = champs[1].split(",")
    phys_uni = [unidecode.unidecode(i.lower()) for i in champ_physique]

    if champ in gen_uni:
        await rep.delete()
        await q.edit(content=f"Par quoi voulez-vous modifier {champ} ?")
        rep = await bot.wait_for("message", timeout=300, check=checkRep)
        save = rep.content
        if rep.content.lower() == "stop":
            await q.delete()
            await rep.delete()
            await ctx.send("Annulation", delete_after=30)
            return
        champ_general = [
            rep.content.capitalize() if champ == unidecode.unidecode(x.lower()) else x
            for x in champ_general
        ]
        part = "general"
    elif champ in phys_uni:
        await q.edit(content=f"Par quoi voulez-vous modifier {champ} ?")
        rep = await bot.wait_for("message", timeout=300, check=checkRep)
        save = rep.content
        if rep.content.lower() == "stop":
            await q.delete()
            await rep.delete()
            await ctx.send("Annulation", delete_after=30)
            return
        champ_physique = [
            rep.content.capitalize() if champ == unidecode.unidecode(x.lower()) else x
            for x in champ_physique
        ]
        part = "physique"
    elif search != "False":
        await q.edit(content=f"Par quoi voulez-vous modifier {champ} ?")
        rep = await bot.wait_for("message", timeout=300, check=checkRep)
        save = rep.content
        if rep.content.lower() == "stop":
            await q.delete()
            await rep.delete()
            await ctx.send("Annulation", delete_after=30)
            return
        autre[search] = save
        part = search
    else:
        await q.delete()
        await rep.delete()
        await ctx.send("Erreur ! Ce champ n'existe pas.", delete_after=30)
        return
    champ_general = ",".join(champ_general)
    champ_physique = ",".join(champ_physique)
    autre = str(autre)
    sql = "UPDATE FICHE SET champ_general = ?, champ_physique = ?, champ_autre = ? WHERE idS=?"
    var = (champ_general, champ_physique, autre, cl)
    c.execute(sql, var)
    db.commit()
    c.close()
    db.close()
    await q.delete()
    await rep.delete()
    await ctx.send(f"Le champ : {champ} a bien été édité par {save}.")
    return "Edited", save, champ, part


async def ajout_champ_norm(ctx, config, cl, bot):
    def checkRep(message):
        return (
            message.author == ctx.message.author
            and ctx.message.channel == message.channel
        )

    db = sqlite3.connect("src/owlly.db", timeout=3000)
    c = db.cursor()
    sql = "SELECT " + config + "FROM FICHE WHERE idS=?"
    c.execute(sql, (cl,))
    champ = c.fetchone()
    if not champ:
        await ctx.send(
            "Vous n'avez pas de fiche configurée. Vous devez d'abord en créer une.",
            delete_after=30,
        )
        return
    if config != "champ_autre":
        champ = champ[0].split(",")
        uni = [unidecode.unidecode(i.lower()) for i in champ]
        q = await ctx.send(
            "Quel est le champ à ajouter ?\n Utiliser `*` pour marquer l'obligation, `&` que c'est une image, et $` pour un lien."
        )
        rep = await bot.wait_for("message", timeout=300, check=checkRep)
        if rep.content.lower() == "stop":
            await q.delete()
            await rep.delete()
            await ctx.send("Annulation", delete_after=30)
            return
        new = rep.content.capitalize()
        if unidecode.unidecode(new.lower()) not in uni:
            champ.append(new)
        else:
            await q.delete()
            await rep.delete()
            await ctx.send("Ce champ existe déjà !", delete_after=30)
            return
        champ = ",".join(champ)
    else:
        if champ[0] != "0":
            champ = ast.literal_eval(champ[0])
            part = [x for x in champ.keys()]
            part = ", ".join(part)
            q = await ctx.send(
                f"Dans quelle partie voulez-vous ajouter ce champ ? Les parties disponibles sont :\n{part}"
            )
            rep = await bot.wait_for("message", timeout=300, check=checkRep)
            champ_uni = {}
            for k, v in champ:
                champ_uni.update(
                    {
                        unidecode.unidecode(k.lower()): [
                            unidecode.unidecode(i.lower()) for i in v
                        ]
                    }
                )
            search = search_autre(
                champ_uni, unidecode.unidecode(rep.content.lower()), champ
            )
            if search != "False":
                partie = champ[search]
                await q.delete()
                await ctx.send("Quel champs voulez-vous rajouter ?")
                rep = await bot.wait_for("message", timeout=300, check=checkRep)
                new = rep.content.capitalize()
                if unidecode.unidecode(rep.content.lower()) not in partie:
                    partie.append(new)
                else:
                    await q.delete()
                    await rep.delete()
                    await ctx.send("Erreur, ce champs existe déjà !")
                    return
                champ[search] = partie
                champ = str(champ)
            else:
                await q.delete()
                await ctx.send("Cette partie n'existe pas.")
                await rep.delete()
                return
        else:
            await ctx.send(
                "Il n'y a pas de partie configurée, merci d'en créer avant de rajouter des champs."
            )
    sql = "UPDATE FICHE SET " + config + "= ? WHERE idS = ?"
    var = (champ, cl)
    c.execute(sql, var)
    db.commit()
    c.close()
    db.close()
    await ctx.send(f"Le champ {new} a bien été ajouté")
    await q.delete()
    await rep.delete()
    return new


async def ajout_partie(ctx, cl, bot):
    def checkRep(message):
        return (
            message.author == ctx.message.author
            and ctx.message.channel == message.channel
        )

    db = sqlite3.connect("src/owlly.db", timeout=3000)
    c = db.cursor()
    sql = "SELECT champ_autre FROM FICHE WHERE idS = ?"
    c.execute(sql, (cl,))
    autre = c.fetchone()
    if autre[0] != "0":
        autre = ast.literal_eval(autre[0])
    else:
        autre = {}
    q = await ctx.send("Combien de parties voulez-vous rajouter ? ")
    rep = await bot.wait_for("message", timeout=300, check=checkRep)
    if (
        rep.content.lower() == "0"
        or rep.content.lower() == "stop"
        or rep.content.lower() == "cancel"
    ):
        await ctx.send("Annulation")
    else:
        while not rep.content.lower().isnumeric():
            await ctx.send("Veuillez rentrer un nombre !")
            rep = await bot.wait_for("message", timeout=300, check=checkRep)
            if (
                rep.content.lower() == "stop"
                or rep.content.lower() == "cancel"
                or rep.content.lower() == "0"
            ):
                await ctx.send("Annulation")
                return
    nb_part = int(rep.content.lower())
    i = 0
    while i < nb_part:
        q = await ctx.send("Quel est le nom de la partie ?")
        rep = await bot.wait_for("message", timeout=300, check=checkRep)
        titre = rep.content
        await q.delete()
        await rep.delete()
        part_champ = await part_fiche(bot, ctx, titre)
        autre.update({titre: part_champ.split(",")})
        i = i + 1
    return autre
