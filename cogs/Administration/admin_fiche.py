import os
import sqlite3
import ast
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
        db_utils = self.bot.get_cog("DB_utils")
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
            recherche = db_utils.db_check("champ_autre", "FICHE", "idS", cl)
            if recherche:
                q = await ctx.send("Voulez-vous supprimer une partie du champ autre ?")
                await q.add_reaction("✅")
                await q.add_reaction("❌")
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=300, check=checkValid
                )
                if reaction.emoji == "✅":
                    check = await utils.delete_autre(ctx, self.bot, cl)
                else:
                    check = await utils.delete_part(ctx, cl, self.bot)
            if check[0] == "Deleted":
                await self.presence_membre(ctx, "supprimé", check[1], 0, 0)
        elif reaction.emoji == "3️⃣":  # Edition
            await q.delete()
            edit = await utils.edit_champ(ctx, cl, self.bot)
            if edit[0] == "Edited":
                save = edit[1]
                champ = edit[2]
                part = edit[3]
                await self.presence_membre(ctx, "édité", save, champ, part)
            return
        elif reaction.emoji == "4️⃣":  # Ajout
            await q.delete()
            sql = "SELECT champ_general, champ_physique, champ_autre FROM FICHE WHERE idS=?"
            c.execute(sql, (cl,))
            champs = c.fetchone()
            gen_msg = "".join(champs[0]).split(",")
            gen_msg = ", ".join(gen_msg)
            phys_msg = "".join(champs[1]).split(",")
            phys_msg = ", ".join(phys_msg)
            autre = ast.literal_eval(champs[2])
            autre_msg = utils.dict_form(autre)
            msg_full = f"**Général** : \n {gen_msg} \n\n **Physique** : \n {phys_msg}\n\n {autre}"
            q = await ctx.send(
                f"__**Fiche actuelle**__ :\n {msg_full}\n Dans quelle partie voulez-vous ajouter votre champ ? \n 1️⃣ GÉNÉRALE \n 2️⃣ PHYSIQUE \n 3️⃣ AUTRE"
            )
            await q.add_reaction("1️⃣")
            await q.add_reaction("2️⃣")
            await q.add_reaction("3️")
            await q.add_reaction("❌")
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=300, check=checkValid
            )
            if reaction.emoji == "1️⃣":
                new = await utils.ajout_champ_norm(ctx, "champ_general", cl, self.bot)
                part = "general"
                await self.presence_membre(ctx, "ajouté", new, 0, part)
            elif reaction.emoji == "2️⃣":
                new = await utils.ajout_champ_norm(ctx, "champ_physique", cl, self.bot)
                part = "physique"
                await self.presence_membre(ctx, "ajouté", new, 0, part)
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
