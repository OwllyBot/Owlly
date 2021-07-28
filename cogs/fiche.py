import ast
import asyncio
import os
import os.path
import sqlite3
import discord
import pyimgur
import unidecode
from discord.ext import commands
from discord.ext.commands import CommandError

CLIENT_ID = os.environ.get("CLIENT_ID")
im = pyimgur.Imgur(CLIENT_ID)


async def search_chan(ctx, chan: str):
    chan = str(chan)
    try:
        chan = await commands.TextChannelConverter().convert(ctx, chan)
        return chan
    except CommandError:
        chan = "Error"
        return chan


async def dict_autre(perso, autre):
    if autre != "0":
        autre_info = {}
        for titre, champs in perso.items():
            for k, v in autre.items():
                for i in v:
                    if titre.lower() == i.lower():
                        titre = titre.replace("\\", "")
                        champs = champs.replace("\\", "")
                        k = k.replace("\\", "")
                        if champs.lower() == "na" or champs.lower() == "/":
                            pass
                        else:
                            autre_info.update({k: {titre: champs}})
        return autre_info
    else:
        return "void"


def titre_autre(autre):
    img = ""
    msg = ""
    for partie, champs in autre.items():
        titre = f"─────༺ {partie} ༻─────\n"
        for k, v in champs.items():
            if v.endswith((".png", ".jpg", ".jpeg", ".gif")):
                img = v
            else:
                k = k.replace("*", "")
                k = k.replace("$", "")
                k = k.replace("&", "")
                msg_content = f"**__{k.capitalize()}__** : {v}\n"
        msg = msg + titre + msg_content
    return msg


async def forme(ctx, member: discord.Member, chartype, idS):
    f = open(
        f"src/fiche/{member.id}_{chartype}_{member.name}_{idS}.txt",
        "r",
        encoding="utf-8",
    )
    perso = {}
    data = f.readlines()
    f.close()
    msg = "error forme msg"
    img = "Error forme image"
    if len(data) > 0:
        data = "".join(data)
        perso = ast.literal_eval(data)
    else:
        try:
            os.path.isfile(
                f"src/fiche/Saves_files/{member.id}_{chartype}_{member.name}_{idS}.txt"
            )
            save = open(
                f"src/fiche/Saves_files/{member.id}_{chartype}_{member.name}_{idS}.txt",
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
    db = sqlite3.connect("src/owlly.db", timeout=3000)
    c = db.cursor()
    sql = "SELECT champ_physique, champ_general, champ_autre FROM FICHE WHERE idS=?"
    c.execute(sql, (idS,))
    champ = c.fetchone()
    general = champ[1].split(",")
    physique = champ[0].split(",")
    general_info = {}
    physique_info = {}
    if champ[2] != 0:
        autre = ast.literal_eval(champ[2])
    else:
        autre = "0"
    for k, v in perso.items():
        for gen in general:
            for phys in physique:
                gen = gen.replace("\\", "")
                phys = phys.replace("\\", "")
                k = k.replace("\\", "")
                if v == "NA" or v == "na" or v == "/":
                    pass
                else:
                    if k.lower() == gen.lower():
                        general_info.update({k: v})
                    elif k.lower() == phys.lower():
                        physique_info.update({k: v})
    autre_info = dict_autre(perso, autre)
    general_msg = "─────༺ Présentation ༻─────\n"
    physique_msg = "──────༺ Physique ༻──────\n"
    img = ""
    for k, v in general_info.items():
        if v.endswith((".png", ".jpg", ".jpeg", ".gif")):
            img = v
        else:
            k = k.replace("*", "")
            k = k.replace("$", "")
            k = k.replace("&", "")
            general_msg = general_msg + f"**__{k.capitalize()}__** : {v}\n"
    for l, m in physique_info.items():
        if m.endswith((".png", ".jpg", ".jpeg", ".gif")):
            img = m
        else:
            l = l.replace("*", "")
            l = l.replace("$", "")
            l = l.replace("&", "")
            physique_msg = physique_msg + f"**__{l.capitalize()}__** : {m}\n"
    autre_msg = titre_autre(autre)
    if autre_msg[0] != "":
        img = autre_msg[0]
    msg = (
        general_msg
        + "\n"
        + physique_msg
        + "\n"
        + autre_msg[1]
        + "\n"
        + f"⋆⋅⋅⋅⊱∘──────∘⊰⋅⋅⋅⋆\n *Joueur* : {member.mention}"
    )
    return msg, img


class fiches(
    commands.Cog, name="Fiche", description="Permet la création, édition, de fiche RP."
):
    def __init__(self, bot):
        self.bot = bot

    async def checkTriggers(self, rep, c, member: discord.Member):
        def checkRep(message):
            return message.author == member and isinstance(
                message.channel, discord.DMChannel
            )

        reponse = rep.content.replace("'", "\\'")
        if "&" in c:
            while not (
                rep.attachments
                or ("discordapp" in reponse)
                or (any(x in reponse for x in ["jpg", "png", "jpeg", "gif"]))
            ):
                await member.send(
                    f"Erreur, ce champ doit être une image (pièce-jointe / lien)"
                )
                rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
                reponse = rep.content
            if rep.attachments:
                reponse = rep.attachments[0]
                imgur = im.upload_image(url=reponse.url)
                reponse = imgur.link
            elif "cdn.discordapp.com" in reponse or reponse.endswith(
                ("jpg", "png", "gif", "jpeg")
            ):
                imgur = im.upload_image(url=reponse)
                reponse = imgur.link
        elif "$" in c:
            while "http" not in reponse:
                await member.send(f"Erreur, ce champ doit être un lien.")
                rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
                reponse = rep.content
        return reponse

    async def validation(self, ctx, msg, img, chartype, member: discord.Member):
        idS = ctx.guild.id
        if msg != "error":
            db = sqlite3.connect("src/owlly.db", timeout=3000)
            c = db.cursor()
            SQL = "SELECT fiche_pj, fiche_pnj, fiche_validation FROM FICHE WHERE idS=?"
            c.execute(SQL, (ctx.guild.id,))
            channel = c.fetchone()

            def checkValid(reaction, user):
                return (
                    user.bot != True
                    and q.id == reaction.message.id
                    and (reaction.emoji == "✅" or reaction.emoji == "❌")
                )

            if (
                (channel[0] is not None)
                and (channel[1] is not None)
                and (channel[0] != 0)
                and (channel[1] != 0)
            ):
                chan = await search_chan(ctx, channel[2])
                q = await chan.send(
                    f"Il y a une présentation à valider ! Son contenu est :\n {msg}\n {img} \n Validez-vous la fiche ? "
                )
                await q.add_reaction("✅")
                await q.add_reaction("❌")
                reaction, user = await self.bot.wait_for(
                    "reaction_add", check=checkValid
                )
                if reaction.emoji == "✅":
                    if chartype.lower() == "pnj":
                        if channel[1] != 0:
                            chan_send = await search_chan(ctx, channel[1])
                        else:
                            chan_send = await search_chan(ctx, channel[0])
                    else:
                        chan_send = await search_chan(ctx, channel[0])
                    if img != "Error" or img != "":
                        embed = discord.Embed(color=0x36393F)
                        embed.set_image(url=img)
                        await chan_send.send(embed=embed)
                        await chan_send.send(msg)
                    else:
                        await chan_send.send(msg)
                    os.remove(
                        f"src/fiche/{member.id}_{chartype}_{member.name}_{idS}.txt"
                    )
                    try:
                        os.remove(
                            f"src/fiche/Saves_files/{member.id}_{chartype}_{member.name}_{idS}.txt"
                        )
                    except OSError:
                        pass
                else:
                    await member.send(
                        "Il y a un soucis avec votre fiche ! Rapprochez-vous des modérateurs pour voir le soucis."
                    )
            else:
                await member.send(
                    "Huh, il y a eu un soucis avec l'envoie. Il semblerait que les channels ne soient pas configurés "
                    "! Rapproche toi du staff pour le prévenir. \n Note : Ce genre de chose n'est pas sensé arrivé, "
                    "donc contacte aussi @Mara#3000 et fait un rapport de bug. "
                )

    async def start_presentation(self, ctx, member, chartype):
        db = sqlite3.connect("src/owlly.db", timeout=3000)
        c = db.cursor()
        idS = ctx.guild.id
        sql = "SELECT champ_general, champ_physique, champ_autre FROM FICHE WHERE idS=?"
        c.execute(sql, (idS,))
        champ_map = c.fetchone()
        general = champ_map[0]
        physique = champ_map[1]
        autre = champ_map[2]
        if general is None or physique is None:
            return "ERROR"
        general = general.split(",")
        physique = physique.split(",")
        if autre != "0":
            autre = ast.literal_eval(autre)
        else:
            autre = ""
        champ = general + physique + autre
        template = champ
        last = champ[-1]

        def checkRep(message):
            return message.author == member and isinstance(
                message.channel, discord.DMChannel
            )

        emoji = ["✅", "❌"]

        def checkValid(reaction, user):
            return (
                user.bot != True
                and isinstance(reaction.message.channel, discord.DMChannel)
                and q.id == reaction.message.id
                and reaction.emoji in emoji
            )

        if not os.path.isfile(
            f"src/fiche/{member.id}_{chartype}_{member.name}_{idS}.txt"
        ):
            perso = {}
        else:
            f = open(
                f"src/fiche/{member.id}_{chartype}_{member.name}_{idS}.txt",
                "r",
                encoding="utf-8",
            )
            data = f.readlines()
            f.close()
            if len(data) > 0:
                data = "".join(data)
                perso = ast.literal_eval(data)
                save = open(
                    f"src/fiche/Saves_files/{member.id}_{chartype}_{member.name}_{idS}.txt",
                    "w",
                    encoding="utf-8",
                )
                save.write(str(perso))
                save.close()
            else:
                try:
                    os.path.isfile(
                        f"src/fiche/Saves_files/{member.id}_{chartype}_{member.name}_{idS}.txt"
                    )
                    save = open(
                        f"src/fiche/Saves_files/{member.id}_{chartype}_{member.name}_{idS}.txt",
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
        f = open(
            f"src/fiche/{member.id}_{chartype}_{member.name}_{idS}.txt",
            "w",
            encoding="utf-8",
        )
        await member.send(
            f":white_small_square: `*` signifie que le champ est obligatoire. \n :white_small_square: `$` signifie que le réponse **doit être un lien** \n :white_small_square: `&` signifie que la réponse doit être **une image**."
        )
        while last.lower() not in perso.keys():
            for t in template:
                t = t.replace("\\", "")
                if t.lower() not in perso.keys():
                    c = t.capitalize()
                    if "*" in c:
                        msg = f"{c} ?\n Ce champ est obligatoire."
                    else:
                        msg = f"{c} ?\n Si votre perso n'en a pas, merci de mettre `/` ou `NA`."
                    if "$" in c:
                        msg = f"{msg}\n Ce champ doit être sous forme de lien."
                    if "&" in c:
                        msg = f"{msg}\n Ce champ doit être une image (pièce-jointe ou lien)."
                    await member.send(msg)
                    c = c.replace("'", "\\'")
                    rep = await self.bot.wait_for(
                        "message", timeout=300, check=checkRep
                    )
                    try:
                        if rep.content.lower() == "stop":
                            await member.send(
                                f"Mise en pause. Vous pourrez reprendre plus tard avec la commande `{ctx.prefix}fiche`"
                            )
                            f.write(str(perso))
                            f.close()
                            return "NOTdone"
                        elif rep.content.lower() == "cancel":
                            await member.send("Annulation de la présentation.")
                            f.close()
                            os.remove(
                                f"src/fiche/{member.id}_{chartype}_{member.name}_{idS}.txt"
                            )
                            try:
                                os.remove(
                                    f"src/fiche/Saves_files/{member.id}_{chartype}_{member.name}_{idS}.txt"
                                )
                            except OSError:
                                pass
                            return "delete"
                        else:
                            reponse = rep.content
                            if ("*" in c) or ("$" in c) or ("&" in c):
                                while "NA" in reponse:
                                    await member.send(
                                        f"Erreur ! Ce champ est obligatoire \n {c} ?"
                                    )
                                    rep = await self.bot.wait_for(
                                        "message", timeout=300, check=checkRep
                                    )
                                    reponse = rep.content
                                    if reponse.lower() == "stop":
                                        await member.send(
                                            f"Mise en pause. Vous pourrez reprendre plus tard avec la commande `{ctx.prefix}fiche`"
                                        )
                                        f.write(str(perso))
                                        f.close()
                                        return "NOTdone"
                                if reponse.lower() == "stop":
                                    await member.send(
                                        f"Mise en pause. Vous pourrez reprendre plus tard avec la commande `{ctx.prefix}fiche`"
                                    )
                                    f.write(str(perso))
                                    f.close()
                                    return "NOTdone"
                                reponse = await self.checkTriggers(rep, c, member)
                            perso.update({c.lower(): reponse})
                    except asyncio.TimeoutError:
                        await member.send(
                            f"Timeout ! Enregistrement des modifications. Vous pourrez la reprendre plus tard avec la commande `{ctx.prefix}fiche`"
                        )
                        f.write(str(perso))
                        f.close()
                        return "NOTdone"
        f.write(str(perso))
        f.close()
        msg, img = await forme(ctx, member, chartype, idS)
        if img != "Error" or img != "":
            msg = msg + "\n\n" + img
        if msg != "error":
            q = await member.send(
                f"Votre présentation est donc : \n {msg}.\n Validez-vous ses paramètres ?"
            )
            await q.add_reaction("✅")
            await q.add_reaction("❌")
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=300, check=checkValid
            )
            if reaction.emoji == "✅":
                await q.edit(
                    content=f"Fin de la présentation ! Merci de votre coopération."
                )
                return "done"
            else:
                await q.edit(
                    content=f"Vous êtes insatisfait. La commande `{ctx.prefix}fiche` vous permettra d'édite ou supprimer votre fiche."
                )
                return "NOTdone"
        return "ERROR"

    @commands.command(
        usage="@mention",
        brief="Permet d'éditer une présentation non validé ou en cours.",
        help="Permet à un administrateur de modifier ou supprimer une fiche en cours de validation, ou en cours d'écriture.",
    )
    @commands.has_permissions(administrator=True)
    async def admin_edit(self, ctx, member: discord.Member):
        idS = ctx.guild.id
        emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "❌"]

        def checkRep(message):
            return message.author == member and ctx.message.channel == message.channel

        def checkValid(reaction, user):
            return (
                ctx.message.author == user
                and q.id == reaction.message.id
                and reaction.emoji in emoji
            )

        if os.path.isfile(
            f"src/fiche/{member.id}_pj_{member.name}_{idS}.txt"
        ) and os.path.isfile(f"src/fiche/{member.id}_pnj_{member.name}_{idS}.txt"):
            q = await ctx.send(
                "Voulez-vous modifier la fiche du PNJ ou PJ ?\n 1️⃣ : PJ\n 2️⃣ : PNJ"
            )
            await q.add_reaction("1️⃣")
            await q.add_reaction("2️⃣")
            await q.add_reaction("❌")
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=300, check=checkValid
            )
            if reaction.emoji == "1️⃣":
                chartype = "pj"
                await q.delete()
            elif reaction.emoji == "2️⃣":
                chartype = "pnj"
                await q.delete()
            else:
                await q.delete()
                await ctx.send("Annulation", delete_after=30)
                return
        elif os.path.isfile(f"src/fiche/{member.id}_pnj_{member.name}_{idS}.txt"):
            chartype = "pnj"
        elif os.path.isfile(f"src/fiche/{member.id}_pj_{member.name}_{idS}.txt"):
            chartype = "pj"
        else:
            chartype = "ERROR"
            await ctx.send(f"{member.name} n'a pas de fiche en cours.")
            return
        f = open(
            f"src/fiche/{member.id}_{chartype}_{member.name}_{idS}.txt",
            "r",
            encoding="utf-8",
        )
        data = f.readlines()
        f.close()
        if len(data) > 0:
            data = "".join(data)
            perso = ast.literal_eval(data)
            save = open(
                f"src/fiche/Saves_files/{member.id}_{chartype}_{member.name}_{idS}.txt",
                "w",
                encoding="utf-8",
            )
            save.write(str(perso))
            save.close()
        else:
            try:
                os.path.isfile(
                    f"src/fiche/Saves_files/{member.id}_{chartype}_{member.name}_{idS}.txt"
                )
                save = open(
                    f"src/fiche/Saves_files/{member.id}_{chartype}_{member.name}_{idS}.txt",
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
        f = open(
            f"src/fiche/{member.id}_{chartype}_{member.name}_{idS}.txt",
            "w",
            encoding="utf-8",
        )
        if chartype != "ERROR":
            menu = discord.Embed(
                title=f"MENU {chartype} EDITION ADMIN",
                description="1️⃣ - EDITION\n 2️⃣ - SUPPRESSION \n 3️⃣ - VOIR LA FICHE \n 4️⃣ - ENVOYER EN VERIFICATION",
            )
            msg, img = await forme(ctx, member, chartype, idS)
            q = await ctx.send(embed=menu)
            for i in emoji:
                await q.add_reaction(i)
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=300, check=checkValid
            )
            if reaction.emoji == "1️⃣":
                await q.delete()
                q = await ctx.send(
                    f"Actuellement, la fiche ressemble à ça : {msg} \n {img} \n Quel champ voulez-vous éditer ?"
                )
                rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
                if rep.content.lower() == "stop":
                    await q.delete()
                    await rep.delete()
                    await ctx.send("Annulation", delete_after=30)
                    return
                value = rep.content
                await rep.delete()
                found = "not"
                for k in perso.keys():
                    if unidecode.unidecode(k.lower()) in unidecode.unidecode(
                        value.lower()
                    ):
                        q = await ctx.send(
                            f"Par quoi voulez-vous modifier {value.capitalize()} ? \n Actuellement, sa valeur est {perso.get(k)}"
                        )
                        rep = self.bot.wait_for("message", timeout=300, check=checkRep)
                        if rep.content.lower() == "stop":
                            await ctx.send("Annulation", delete_after=30)
                            await q.delete()
                            await rep.delete()
                            return
                        c = k.capitalize()
                        if ("*" in c) or ("$" in c) or ("&" in c):
                            while "NA" in rep.content:
                                await member.send(
                                    f"Erreur ! Ce champ est obligatoire \n {value.capitalize()} ?"
                                )
                                rep = await self.bot.wait_for(
                                    "message", timeout=300, check=checkRep
                                )
                                repCheck = await self.checkTriggers(rep, c, member)
                                if repCheck.lower() == "stop":
                                    await member.send(f"Mise en pause.")
                                    f.write(str(perso))
                                    f.close()
                        perso[k] = rep.content
                        f = open(
                            f"src/fiche/{member.id}_{chartype}_{member.name}_{idS}.txt",
                            "w",
                            encoding="utf-8",
                        )
                        f.write(str(perso))
                        f.close()
                        q = await q.edit(
                            content=f"{value.capitalize()} a bien été modifié !"
                        )
                        found = "yes"
                        break
                if found == "not":
                    await ctx.send("Erreur ! {value} n'a pas été trouvé...")
                    await q.delete()
                    return
            elif reaction.emoji == "2️⃣":
                await q.delete()
                os.remove(f"src/fiche/{member.id}_{chartype}_{member.name}_{idS}.txt")
                try:
                    os.remove(
                        f"src/fiche/Saves_files/{member.id}_{chartype}_{member.name}_{idS}.txt"
                    )
                except OSError:
                    pass
                await ctx.send(f"La présentation de {member.name} a été supprimé.")
            elif reaction.emoji == "3️⃣":
                msg, img = await forme(ctx, member, chartype, idS)
                await ctx.send(f"{msg} \n {img}")
            elif reaction.emoji == "4️⃣":
                fiche, img = await forme(ctx, member, chartype, idS=ctx.guild.id)
                await self.validation(ctx, fiche, img, chartype, member)
            else:
                await q.delete()
                await ctx.send(f"Annulation", delete_after=30)
                return
        else:
            await ctx.send(f"{member.name} n'a pas de présentation en cours...")
            return

    @commands.command(
        aliases=["pres", "edit_pres"],
        brief="Commandes pour modifier une présentation en cours.",
        help="Le champ PNJ est à indiquer pour les fiches lorsque celles-ci sont pour les PNJ. Autrement, par défaut, les fiches PJ sont sélectionnées. \n Cette commande permet la reprise, modification ou suppression d'une présentation.",
    )
    async def fiche(self, ctx):
        member = ctx.message.author
        idS = ctx.guild.id
        emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "❌"]

        def checkValid(reaction, user):
            return (
                ctx.message.author == user
                and q.id == reaction.message.id
                and reaction.emoji in emoji
            )

        if os.path.isfile(
            f"src/fiche/{member.id}_pj_{member.name}_{idS}.txt"
        ) and os.path.isfile(f"src/fiche/{member.id}_pnj_{member.name}_{idS}.txt"):
            q = await ctx.send(
                "Voulez-vous modifier la fiche de votre PNJ ou PJ ?\n 1️⃣ : PJ\n 2️⃣ : PNJ"
            )
            await q.add_reaction("1️⃣")
            await q.add_reaction("2️⃣")
            await q.add_reaction("❌")
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=300, check=checkValid
            )
            if reaction.emoji == "1️⃣":
                chartype = "pj"
                await q.delete()
            elif reaction.emoji == "2️⃣":
                chartype = "pnj"
                await q.delete()
            else:
                await q.delete()
                await ctx.send("Annulation", delete_after=30)
                return
        elif os.path.isfile(f"src/fiche/{member.id}_pnj_{member.name}_{idS}.txt"):
            chartype = "pnj"
        elif os.path.isfile(f"src/fiche/{member.id}_pj_{member.name}_{idS}.txt"):
            chartype = "pj"
        else:
            chartype = "ERROR"
            await ctx.send("Erreur ! Vous n'avez pas de présentation en cours.")
            return
        f = open(
            f"src/fiche/{member.id}_{chartype}_{member.name}_{idS}.txt",
            "r",
            encoding="utf-8",
        )
        data = f.readlines()
        f.close()
        if len(data) > 0:
            data = "".join(data)
            perso = ast.literal_eval(data)
            save = open(
                f"src/fiche/Saves_files/{member.id}_{chartype}_{member.name}_{idS}.txt",
                "w",
                encoding="utf-8",
            )
            save.write(str(perso))
            save.close()
        else:
            try:
                os.path.isfile(
                    f"src/fiche/Saves_files/{member.id}_{chartype}_{member.name}_{idS}.txt"
                )
                save = open(
                    f"src/fiche/Saves_files/{member.id}_{chartype}_{member.name}_{idS}.txt",
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
        f = open(
            f"src/fiche/{member.id}_{chartype}_{member.name}_{idS}.txt",
            "w",
            encoding="utf-8",
        )

        def checkRep(message):
            return message.author == member and isinstance(
                message.channel, discord.DMChannel
            )

        db = sqlite3.connect("src/owlly.db", timeout=3000)
        c = db.cursor()
        SQL = "SELECT fiche_pj, fiche_pnj, fiche_validation FROM FICHE WHERE idS=?"
        c.execute(SQL, (ctx.guild.id,))
        channel = c.fetchone()
        if (
            (channel[0] is not None)
            and (channel[1] is not None)
            and (channel[0] != 0)
            and (channel[1] != 0)
        ):
            if chartype != "ERROR":
                msg, img = await forme(ctx, member, chartype, idS)
                menu = discord.Embed(
                    title=f"Menu ({chartype})",
                    description="1️⃣ - Edition\n 2️⃣ - Suppression\n 3️⃣ - Reprise \n 4️⃣ - Voir la fiche en cours",
                )
                q = await ctx.send(embed=menu)
                for i in emoji:
                    await q.add_reaction(i)
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=300, check=checkValid
                )
                if reaction.emoji == "1️⃣":
                    await member.send(
                        f"Actuellement, votre fiche ressemble à ceci :\n {msg}"
                    )
                    q = await member.send(
                        "Quel est le champ que vous voulez modifier ?"
                    )
                    rep = await self.bot.wait_for(
                        "message", timeout=300, check=checkRep
                    )
                    if rep.content.lower() == "stop":
                        await q.delete()
                        await rep.delete()
                        await ctx.send("Annulation", delete_after=30)
                        return
                    value = rep.content
                    found = "not"
                    for k in perso.keys():
                        if unidecode.unidecode(value.lower()) in unidecode.unidecode(
                            k.lower()
                        ):
                            q = await member.send(
                                f"Par quoi voulez-vous modifier {value.capitalize()} ?\n Actuellement, elle a pour valeur {perso.get(k)}."
                            )
                            rep = await self.bot.wait_for(
                                "message", timeout=300, check=checkRep
                            )
                            if rep.content.lower() == "stop":
                                await q.delete()
                                await member.send("Annulation")
                                await rep.delete()
                                return
                            c = k.capitalize()
                            if ("*" in c) or ("$" in c) or ("&" in c):
                                while "NA" in rep.content:
                                    await member.send(
                                        f"Erreur ! Ce champ est obligatoire \n {value.capitalize()} ?"
                                    )
                                    rep = await self.bot.wait_for(
                                        "message", timeout=300, check=checkRep
                                    )
                                    repCheck = await self.checkTriggers(rep, c, member)
                                    if repCheck.lower() == "stop":
                                        await member.send(
                                            f"Mise en pause. Vous pourrez reprendre plus tard avec la commande `{ctx.prefix}fiche`"
                                        )
                                        f.write(str(perso))
                                        f.close()
                            perso[k] = rep.content
                            f = open(
                                f"src/fiche/{member.id}_{chartype}_{member.name}_{idS}.txt",
                                "w",
                                encoding="utf-8",
                            )
                            f.write(str(perso))
                            f.close()
                            q = await q.edit(
                                content=f"{value.capitalize()} a bien été modifié !"
                            )
                            found = "yes"
                            break
                    if found == "not":
                        await ctx.send(
                            f"{value} n'a pas été trouvé dans votre fiche..."
                        )
                        return
                elif reaction.emoji == "2️⃣":
                    os.remove(
                        f"src/fiche/{member.id}_{chartype}_{member.name}_{idS}.txt"
                    )
                    try:
                        os.remove(
                            f"src/fiche/Saves_files/{member.id}_{chartype}_{member.name}_{idS}.txt"
                        )
                    except OSError:
                        pass
                    await ctx.send("Votre présentation a été supprimé.")
                elif reaction.emoji == "3️⃣":
                    await ctx.send("Regardez vos DM 📨 !")
                    step = await self.start_presentation(ctx, member, chartype)
                    if step == "done":
                        msg, img = await forme(ctx, member, chartype, idS)
                        await self.validation(ctx, msg, img, chartype, member)
                elif reaction.emoji == "4️⃣":
                    msg, img = await forme(ctx, member, chartype, idS)
                    await member.send(f"{msg} \n {img}")
            else:
                await ctx.send("Vous n'avez pas de présentation en cours !")
        else:
            await ctx.send(
                "Impossible de faire une présentation : Les channels ne sont pas configuré !"
            )

    @commands.command(
        usage="@mention",
        brief="Lance la création d'une fiche",
        help="Permet à un joueur ayant sa fiche valider de faire sa présentation.",
        aliases=["add_pj", "validation", "add_pres", "add_presentation"],
    )
    @commands.has_permissions(manage_nicknames=True)
    async def pj(self, ctx, member: discord.Member):
        chartype = "pj"
        await ctx.send(f"{member.mention} check tes DM ! 📧")
        await ctx.message.delete()
        # Member seems to have problem with pycharm here
        pres = await self.start_presentation(ctx, member, chartype)
        if pres == "done":
            fiche, img = await forme(ctx, member, chartype, ctx.guild.id)
            await self.validation(ctx, fiche, img, chartype, member)

    @commands.command(
        usage="@mention",
        brief="Lance la création d'une fiche PNJ",
        help="Permet à un joueur ayant sa fiche PNJ validée de faire sa présentation.",
        aliases=["add_pnj", "validation_pnj"],
    )
    @commands.has_permissions(manage_nicknames=True)
    async def pnj(self, ctx, member: discord.Member):
        chartype = "pnj"
        await ctx.send(f"{member.mention} check tes DM ! 📧")
        pres = await self.start_presentation(ctx, member, chartype)
        await ctx.message.delete()
        if pres == "done":
            fiche, img = await forme(ctx, member, chartype, ctx.guild.id)
            await self.validation(ctx, fiche, img, chartype, member)


def setup(bot):
    bot.add_cog(fiches(bot))
