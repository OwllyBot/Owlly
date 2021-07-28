import os
import sqlite3
import json
import discord
import unidecode
from discord.ext import commands
from discord.ext.commands import CommandError
from cogs.Administration import fiche_config as utils


class adminfiche(
    commands.Cog,
    name="Administration des fiches",
    description="Permet de configurer les fiches.",
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

    async def presence_membre(self, ctx, type_edit, champ, old, part):
        if len(os.listdir("fiche")) > 1:  # Repertoire avec autre chose que .pouic
            await ctx.send("Alerte ! Il y a des fiches en cours ! ")
            list_files = []
            for (rep, sous_rep, fichier) in os.walk("fiche"):
                list_files.extend(fichier)
            play = []
            pj = []
            for i in list_files:
                if i != ".pouic" and i not in play:
                    play.append(i.split("_")[0])
                    pj.append(i.split("_")[1])
            for member in play:
                for chartype in pj:
                    dm = await commands.MemberConverter.convert(ctx, member)
                    await dm.send(f"⚠️ {ctx.author.mention} a {type_edit} {champ}. ")
                    if type_edit == "édité":
                        await utils.edit_update(ctx, dm, chartype, champ, old)
                    elif type_edit == "ajouté":
                        await utils.add_update(ctx, dm, chartype, champ, part)

    @commands.group(
        brief="Permet de choisir les champs de la présentation des personnages.",
        help="Cette commande permet de choisir les champs de présentation générale et du physique, de les éditer, supprimer mais aussi en ajouter.",
    )
    @commands.has_permissions(administrator=True)
    async def fiche(self, ctx):
        emoji = [
            "1️⃣",
            "2️⃣",
            "3️⃣",
            "4️⃣",
            "👀",
            "❌",
            "✅",
        ]

        def checkValid(reaction, user):
            return (
                ctx.message.author == user
                and q.id == reaction.message.id
                and reaction.emoji in emoji
            )

        def checkRep(message):
            return (
                message.author == ctx.message.author
                and ctx.message.channel == message.channel
            )

        cl = ctx.guild.id
        db = sqlite3.connect("src/owlly.db", timeout=3000)
        c = db.cursor()
        menu = discord.Embed(
            title="Menu de gestion des fiches",
            description="1️⃣ | Création\n2️⃣ | Suppression\n3️⃣ | Edition\n4️⃣ | Ajout\n👀 | Affichage",
        )
        menu.set_footer(text="❌ pour annuler.")
        q = await ctx.send(embed=menu)
        for i in emoji:
            if i != "✅":
                await q.add_reaction(i)
        reaction, user = await self.bot.wait_for(
            "reaction_add", timeout=300, check=checkValid
        )
        if reaction.emoji == "1️⃣":
            if len(os.listdir("fiche")) > 1:
                await ctx.send(
                    "ALERTE ! Il y a des fiches en cours. Vous devez attendre qu'elles soient terminé pour pouvoir modifier les champs...."
                )
                return
            await q.delete()
            sql = "SELECT fiche_pj, fiche_validation, fiche_pnj FROM FICHE WHERE idS=?"
            c.execute(sql, (cl,))
            channels = c.fetchone()
            if channels[0] is None:
                await self.fiche(ctx)
            general = await utils.part_fiche(self.bot, ctx, "générale")
            physique = await utils.part_fiche(self.bot, ctx, "physique")
            await q.delete()
            q = await ctx.send("Voulez-vous rajouter des parties à votre fiche ? ")
            await q.add_reaction("✅")
            await q.add_reaction("❌")
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=300, check=checkValid
            )
            if reaction.emoji == "✅":
                champ_autre = {}
                await q.delete()
                q = await ctx.send("Combien de partie voulez-vous rajouter ? ")
                rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
                if (
                    rep.content.lower() == "0"
                    or rep.content.lower() == "stop"
                    or rep.content.lower() == "cancel"
                ):
                    await ctx.send("Annulation")
                else:
                    while not isinstance(rep.content, int):
                        await ctx.send("Veuillez rentrer un nombre !")
                        rep = await self.bot.wait_for(
                            "message", timeout=300, check=checkRep
                        )
                nb_part = int(rep.content.lower())
                i = 0
                while i < nb_part:
                    q = await ctx.send("Quel est le nom de la partie ?")
                    rep = await self.bot.wait_for(
                        "message", timeout=300, check=checkRep
                    )
                    titre = rep.content
                    await q.delete()
                    await rep.delete()
                    part_champ = await utils.part_fiche(self.bot, ctx, titre)
                    champ_autre.update({titre: part_champ.split(",")})
                    i = i + 1
            phrase_autre = utils.dict_form(champ_autre)
            q = await ctx.send(
                f"Vos champs sont donc :\n __GÉNÉRAL__ :\n {general} \n\n __PHYSIQUE__ : {physique}\n\n {phrase_autre} Validez-vous ses paramètres ?"
            )
            await q.add_reaction("✅")
            await q.add_reaction("❌")
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=300, check=checkValid
            )
            if reaction.emoji == "✅":
                autre = str(champ_autre)
                sql = "UPDATE FICHE SET champ_general = ?, champ_physique = ?, champ_autre=? WHERE idS=?"
                var = (general, physique, autre, cl)
                c.execute(sql, var)
                db.commit()
                await ctx.send("Enregistré !")
                await q.delete()
                return
            else:
                await q.delete()
                await ctx.send("Annulation", delete_after=30)
                return
        elif reaction.emoji == "2️⃣":  # Suppression
            await q.delete()
            check = await utils.delete_part(ctx, cl, self.bot)
            if check[0] == "Deleted":
                await self.presence_membre(ctx, "supprimé", check[1], 0, 0)
        elif reaction.emoji == "3️⃣":  # Edition
            save = ""
            await q.delete()
            sql = "SELECT champ_general, champ_physique FROM FICHE WHERE idS=?"
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
            msg_full = f"**Général** : \n {gen_msg} \n\n **Physique** : \n {phys_msg}\n"
            q = await ctx.send(f"{msg_full} Quel champ voulez-vous éditer ?")
            rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
            if rep.content.lower() == "stop":
                await q.delete()
                await rep.delete()
                await ctx.send("Annulation", delete_after=30)
                return
            else:
                champ = unidecode.unidecode(rep.content.lower())

            champ_general = champs[0].split(",")
            gen_uni = [unidecode.unidecode(i.lower()) for i in champ_general]
            champ_physique = champs[1].split(",")
            phys_uni = [unidecode.unidecode(i.lower()) for i in champ_physique]

            if champ in gen_uni:
                await rep.delete()
                await q.edit(content=f"Par quoi voulez-vous modifier {champ} ?")
                rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
                save = rep.content
                if rep.content.lower() == "stop":
                    await q.delete()
                    await rep.delete()
                    await ctx.send("Annulation", delete_after=30)
                    return
                champ_general = [
                    rep.content.capitalize()
                    if champ == unidecode.unidecode(x.lower())
                    else x
                    for x in champ_general
                ]
                part = "general"
            elif champ in phys_uni:
                await q.edit(content=f"Par quoi voulez-vous modifier {champ} ?")
                rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
                save = rep.content
                if rep.content.lower() == "stop":
                    await q.delete()
                    await rep.delete()
                    await ctx.send("Annulation", delete_after=30)
                    return
                champ_physique = [
                    rep.content.capitalize()
                    if champ == unidecode.unidecode(x.lower())
                    else x
                    for x in champ_physique
                ]
                part = "physique"
            else:
                await q.delete()
                await rep.delete()
                await ctx.send("Erreur ! Ce champ n'existe pas.", delete_after=30)
                return
            champ_general = ",".join(champ_general)
            champ_physique = ",".join(champ_physique)
            sql = "UPDATE FICHE SET champ_general = ?, champ_physique = ? WHERE idS=?"
            var = (champ_general, champ_physique, cl)
            c.execute(sql, var)
            db.commit()
            c.close()
            db.close()
            await q.delete()
            await rep.delete()
            await ctx.send(f"Le champ : {champ} a bien été édité par {save}.")
            await self.presence_membre(ctx, "édité", save, champ, part)
            return
        elif reaction.emoji == "4️⃣":  # Ajout
            await q.delete()
            sql = "SELECT champ_general, champ_physique FROM FICHE WHERE idS=?"
            c.execute(sql, (cl,))
            champs = c.fetchone()
            gen_msg = "".join(champs[0]).split(",")
            gen_msg = ", ".join(gen_msg)
            phys_msg = "".join(champs[1]).split(",")
            phys_msg = ", ".join(phys_msg)
            msg_full = f"**Général** : \n {gen_msg} \n\n **Physique** : \n {phys_msg}\n"
            q = await ctx.send(
                f"__**Fiche actuelle**__ :\n {msg_full}\n Dans quelle partie voulez-vous ajouter votre champ ? \n 1️⃣ : GÉNÉRALE \n 2️⃣: PHYSIQUE"
            )
            await q.add_reaction("1️⃣")
            await q.add_reaction("2️⃣")
            await q.add_reaction("❌")
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=300, check=checkValid
            )
            if reaction.emoji == "1️⃣":
                sql = "SELECT champ_general FROM FICHE WHERE idS=?"
                c.execute(sql, (cl,))
                champ_general = c.fetchone()[0]
                part = "general"
                if champ_general is None:
                    await ctx.send(
                        "Vous n'avez pas de fiche configurée. Vous devez d'abord en créer une.",
                        delete_after=30,
                    )
                    return
                champ_general = champ_general.split(",")
                gen_uni = [unidecode.unidecode(i.lower()) for i in champ_general]
                await q.delete()
                q = await ctx.send(
                    "Quel est le champ à ajouter ?\n Utiliser `*` pour marquer l'obligation, `&` que c'est une image, et $` pour un lien."
                )
                rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
                if rep.content.lower() == "stop":
                    await q.delete()
                    await rep.delete()
                    await ctx.send("Annulation", delete_after=30)
                    return
                new = rep.content.capitalize()
                if unidecode.unidecode(new.lower()) not in gen_uni:
                    champ_general.append(new)
                else:
                    await q.delete()
                    await rep.delete()
                    await ctx.send("Ce champ existe déjà !", delete_after=30)
                    return
                champ_general = ",".join(champ_general)
                sql = "UPDATE FICHE SET champ_general = ? WHERE idS=?"
                var = (champ_general, cl)
                c.execute(sql, var)
                db.commit()
                c.close()
                db.close()
                await ctx.send(f"Le champ {new} a bien été ajouté !")
                await q.delete()
                await rep.delete()
                return
            elif reaction.emoji == "2️⃣":
                sql = "SELECT champ_physique FROM FICHE WHERE idS=?"
                c.execute(sql, (cl,))
                champ_physique = c.fetchone()[0]
                if champ_physique is None:
                    await ctx.send(
                        "Vous n'avez pas de fiche configurée. Vous devez d'abord en créer une.",
                        delete_after=30,
                    )
                    return
                champ_physique = champ_physique.split(",")
                part = "physique"
                phys_uni = [unidecode.unidecode(i.lower()) for i in champ_physique]
                await q.delete()
                q = await ctx.send("Quel est le champ à ajouter ?")
                rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
                if rep.content.lower() == "stop":
                    await q.delete()
                    await rep.delete()
                    await ctx.send("Annulation", delete_after=30)
                    return
                new = rep.content.capitalize()
                if unidecode.unidecode(new.lower()) not in phys_uni:
                    champ_physique.append(new)
                else:
                    await q.delete()
                    await rep.delete()
                    await ctx.send("Ce champ existe déjà !", delete_after=30)
                    return
                champ_physique = ",".join(champ_physique)
                sql = "UPDATE FICHE SET champ_physique = ? WHERE idS=?"
                var = (champ_physique, cl)
                c.execute(sql, var)
                db.commit()
                c.close()
                db.close()
                await rep.delete()
                await q.delete()
                await ctx.send(f"Le champ {new} a bien été ajouté !")
                await self.presence_membre(ctx, "ajouté", new, 0, part)
                return
            else:
                await q.delete()
                await ctx.send("Annulation", delete_after=30)
                c.close()
                db.close()
                return
        elif reaction.emoji == "👀":
            sql = "SELECT champ_general, champ_physique FROM FICHE WHERE idS=?"
            c.execute(sql, (cl,))
            champs = c.fetchone()
            gen_msg = "".join(champs[0]).split(",")
            gen_msg = ", ".join(gen_msg)
            phys_msg = "".join(champs[1]).split(",")
            phys_msg = ", ".join(phys_msg)
            msg_full = f"**Général** : \n {gen_msg} \n\n **Physique** : \n {phys_msg}\n"
            await q.delete()
            await ctx.send(f"Fiche actuelle : \n {msg_full}")
            c.close()
            db.close()
            return
        else:
            await q.delete()
            await ctx.send("Annulation", delete_after=30)
            c.close()
            db.close()
            return
        c.close()
        db.close()

    @commands.has_permissions(administrator=True)
    @fiche.command(
        help="Permet de configurer le channel dans lequel sera envoyé les présentations des personnages.",
        brief="Insertion d'un channel pour envoyer les présentations validées.",
        usage="channel",
    )
    async def chan(self, ctx):
        def checkRep(message):
            return (
                message.author == ctx.message.author
                and ctx.message.channel == message.channel
            )

        def checkValid(reaction, user):
            return (
                ctx.message.author == user
                and q.id == reaction.message.id
                and (reaction.emoji == "✅" or reaction.emoji == "❌")
            )

        cl = ctx.guild.id
        db = sqlite3.connect("src/owlly.db", timeout=3000)
        c = db.cursor()
        q = await ctx.send(
            "Dans quel channel voulez-vous que soit envoyé les fiches à valider ?"
        )
        rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
        if rep.content.lower() == "stop":
            await q.delete()
            await rep.delete()
            await ctx.send("Annulation", delete_after=30)
            return
        fiche_validation = await self.search_chan(ctx, rep.content)
        if fiche_validation == "Error":
            await ctx.send("Erreur dans le channel.", delete_after=30)
            await q.delete()
            await rep.delete()
            return
        await rep.delete()
        await q.edit(
            content="Dans quel channel voulez-vous envoyer la présentation des PJ validés ?"
        )
        rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
        if rep.content.lower() == "stop":
            await q.delete()
            await rep.delete()
            await ctx.send("Annulation", delete_after=30)
            return
        fiche_pj = await self.search_chan(ctx, rep.content)
        if fiche_pj == "Error":
            await ctx.send("Erreur dans le channel.", delete_after=30)
            await q.delete()
            await rep.delete()
            return
        await rep.delete()
        await q.edit(content="Voulez-vous configurer le channel des PNJ ?")
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for(
            "reaction_add", timeout=300, check=checkValid
        )
        if reaction.emoji == "✅":
            await q.clear_reactions()
            await q.edit(
                content="Dans quel channel voulez-vous que soit envoyé les fiches des PNJ ?"
            )
            rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
            fiche_pnj = await self.search_chan(ctx, rep.content)
            fiche_pnj = fiche_pnj.id
            if fiche_pnj == "Error":
                await ctx.send("Erreur dans le channel.", delete_after=30)
                await q.delete()
                await rep.delete()
                return
        else:
            fiche_pnj = 0
        await q.edit(content="Validation des modification....")
        sql = "UPDATE FICHE SET fiche_validation=?, fiche_pj=?, fiche_pnj=? WHERE idS=?"
        var = (fiche_validation.id, fiche_pj.id, fiche_pnj, cl)
        c.execute(sql, var)
        db.commit()
        c.close()
        db.close()
        await q.edit(content="Modification validée !")


def setup(bot):
    bot.add_cog(adminfiche(bot))
