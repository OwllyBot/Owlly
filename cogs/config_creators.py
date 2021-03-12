import discord
from discord.ext import commands, tasks
from discord.utils import get
from typing import Optional
import sqlite3
import re
from discord import Colour
intents = discord.Intents(messages=True, guilds=True,
                          reactions=True, members=True)

# ▬▬▬▬▬▬▬▬▬▬▬ SEARCH CAT NAME ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬


class config(commands.Cog, name="Créateurs", description="Permet de créer les messages pour créer des channels dans les catégories."):
    def __init__(self, bot):
        self.bot = bot

    def convertColor(self, ctx, color: Optional[discord.Color] = None):
        if color is None:
            return Colour.blurple()
        else:
            print(color)
            print(type(color))
            return color
    
    def checkImg(self, ctx, img):
        pattern = 'http(s?):\/\/www\.(.*)(png|jpg|jpeg|gif|gifv|)'
        result=re.match(pattern, img)
        if result:
            return (result.group(0))
        else:
            return "error"

    async def search_cat_name(self, ctx, name):
        emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
        def checkValid(reaction, user):
            return ctx.message.author == user and q.id == reaction.message.id and str(reaction.emoji) in emoji
        cat_list = []
        for cat in ctx.guild.categories:
            cat_list.append(cat.name)
        w = re.compile(f".*{name}.*", re.IGNORECASE)
        search = list(filter(w.match, cat_list))
        search_list = []
        lg = len(search)
        if lg == 0:
            return 12
        elif lg == 1:
            name = search[0]
            name = get(ctx.guild.categories, name=name)
            number = name.id
            return number
        elif lg > 1 and lg < 10:
            for i in range(0, lg):
                phrase = f"{emoji[i]} : {search[i]}"
                search_list.append(phrase)
            search_question = "\n".join(search_list)
            q = await ctx.send(f"Plusieurs catégories correspondent à ce nom. Pour choisir celle que vous souhaitez, cliquez sur le numéro correspondant :\n {search_question}")
            for i in range(0, lg):
                await q.add_reaction(emoji[i])
            select, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
            for i in range(0, lg):
                if str(select) == str(emoji[i]):
                    name = search[i]
                    mot = search[i]
            name = get(ctx.guild.categories, name=name)
            number = name.id
            await q.delete()
            await ctx.send(f"Catégorie : {mot} ✅ \n > Vous pouvez continuer l'inscription des channels. ", delete_after=30)
            return number
        else:
            await ctx.send("Il y a trop de correspondance ! Merci de recommencer la commande.", delete_after=30)
            return

    @commands.has_permissions(administrator=True)
    @commands.command(aliases=['tick'], name="Ticket", brief="Débute la configuration des tickets", help="Permet de créer la configuration des tickets avec divers paramètres, notamment ceux le numéros dans le nom, ainsi que le moment où ce numéros va se reset. Les tickets sont des channels dont le nom est fixé.", description="Configuration pour une seule catégorie.")
    async def ticket(self, ctx):
        def checkValid(reaction, user):
            return ctx.message.author == user and question.id == reaction.message.id and (
                str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌")
        def checkRep(message):
            return message.author == ctx.message.author and ctx.message.channel == message.channel
        guild = ctx.message.guild
        await ctx.message.delete()
        db = sqlite3.connect("owlly.db", timeout=3000)
        c = db.cursor()
        q = await ctx.send(f"Quel est le titre de l'embed ?")
        titre = await self.bot.wait_for("message", timeout=300, check=checkRep)
        typeM = titre.content
        if typeM == "stop":
            await ctx.send("Annulation !", delete_after=10)
            await titre.delete()
            await q.delete()
            return
        await q.edit(content=f"Quelle est sa description ?")
        desc = await self.bot.wait_for("message", timeout=300, check=checkRep)
        if desc.content == "stop":
            await ctx.send("Annulation !", delete_after=30)
            await desc.delete()
            await q.delete()
            return
        await desc.delete()
        await q.edit(content="Dans quel catégorie voulez-vous créer vos tickets ? Rappel : Seul un modérateur pourra les supprimer, car ce sont des tickets permanent.\n Vous pouvez utiliser le nom ou l'ID de la catégorie !")
        ticket_chan = await self.bot.wait_for("message", timeout=300, check=checkRep)
        ticket_chan_content = ticket_chan.content
        cat_name = "none"
        if ticket_chan_content == "stop":
            await ctx.send("Annulation !", delete_after=10)
            await q.delete()
            await ticket_chan.delete()
            return
        else:
            await ticket_chan.delete()
            if ticket_chan_content.isnumeric():
                ticket_chan_content = int(ticket_chan_content)
                cat_name = get(guild.categories, id=ticket_chan_content)
                if cat_name == "None":
                    await ctx.send("Erreur : Cette catégorie n'existe pas !", delete_after=30)
                    await q.delete()
                    return
            else:
                ticket_chan_content = await self.search_cat_name(ctx, ticket_chan_content)
                cat_name = get(guild.categories, id=ticket_chan_content)
                if ticket_chan_content == 12:
                    await ctx.send("Aucune catégorie portant un nom similaire existe, vérifier votre frappe.",delete_after=30)
                    await q.delete()
                    return
                else:
                    cat_name = get(guild.categories, id=ticket_chan_content)
        await q.edit(conten=f"Quelle couleur voulez vous utiliser ? \n 0 donne une couleur aléatoire.")
        color = await self.bot.wait_for("message", timeout=300, check=checkRep)
        col = color.content
        if col == "stop":
            await ctx.send("Annulation !", delete_after=30)
            await q.delete()
            await color.delete()
            return
        elif col == "0":
            col = Colour.random()
        else:
            col=self.convertColor(ctx, col)
        print(type(col))
        await color.delete()
        q.edit(content="Voulez-vous ajouter une image ?")
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
        if reaction.emoji == "✅":
            await q.clear_reactions()
            await q.edit(content="Merci d'envoyer l'image. \n**⚡ ATTENTION : LE MESSAGE EN REPONSE EST SUPPRIMÉ VOUS DEVEZ DONC UTILISER UN LIEN PERMANENT (hébergement sur un autre channel/serveur, imgur, lien google...)**")
            img = await self.bot.wait_for("message", timeout=300, check=checkRep)
            img_content = img.content
            if img_content == "stop":
                await ctx.send("Annulation !", delete_after=10)
                await q.delete()
                await img.delete()
                return
            else:
                img_content=self.checkImg(ctx, img_content)
                if img_content=="Error":
                    await ctx.send("Erreur ! Votre lien n'est pas une image valide.", delete_after=60)
                    await q.delete()
                    await img.delete()
                    return
                else:
                    img.delete()
        else:
            await q.clear_reactions()
            img_content = "none"
        await q.edit(content="Voulez-vous fixer un nombre de départ ?")
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
        if reaction.emoji == "✅":
            await q.clear_reactions()
            await q.edit(content="Merci d'indiquer le nombre de départ.")
            nb_dep = await self.bot.wait_for("message", timeout=300, check=checkRep)
            if nb_dep.content == "stop":
                await q.delete()
                await ctx.send("Annulation !", delete_after=10)
                await nb_dep.delete()
                return
            else:
                nb_dep_content = int(nb_dep.content)
                await nb_dep.delete()
        else:
            nb_dep_content = 0
        await q.edit(content="Voulez-vous fixer une limite ? C'est à dire que le ticket va se reset après ce nombre.")
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
        if reaction.emoji == "✅":
            await q.clear_reactions()
            await q.edit(content="Merci d'indiquer la limite.")
            limit = await self.bot.wait_for("message", timeout=300, check=checkRep)
            if limit.content == "stop":
                await ctx.send("Annulation !", delete_after=10)
                await q.delete()
                await limit.delete()
                return
            else:
                limit_content = int(limit.content)
                await limit.delete()
                mod_content = 0
                await q.edit(content="Voulez-vous, après la limite, augmenter d'un certain nombre le numéro ?")
                await q.add_reaction("✅")
                await q.add_reaction("❌")
                reaction, user = await self.bot.wait_for("reaction_add",timeout=300,check=checkValid)
                if reaction.emoji == "✅":
                    await q.clear_reactions()
                    await q.edit(content="Quel est donc ce nombre ?")
                    mod = await self.bot.wait_for("message",timeout=300,check=checkRep)
                    if mod.content == "stop":
                        await ctx.send("Annulation !", delete_after=10)
                        await mod.delete()
                        await q.delete()
                        return
                    else:
                        mod_content = int(mod.content)
                        await mod.delete()
                else:
                    await q.clear_reactions()
        else:
            limit_content = 0
            mod_content = 0
            await q.clear_reactions()
        guild = ctx.message.guild
        await q.edit(content=
            f"Vos paramètres sont : \n Titre : {typeM} \n Numéro de départ : {nb_dep_content} \n Intervalle entre les nombres (on se comprend, j'espère) : {mod_content} (0 => Pas d'intervalle) \n Limite : {limit_content} (0 => Pas de limite) \n Catégorie : {cat_name}. \n\n Confirmez-vous ces paramètres ?"
        )
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for("reaction_add",timeout=300,check=checkValid)
        if reaction.emoji == "✅":
            await q.clear_reactions()
            embed = discord.Embed(title=titre.content,description=desc.content,color=col)
            if img_content != "none":
                embed.set_image(url=img_content)
            await q.edit(content=
                "Vous pouvez choisir l'émoji de réaction en réagissant à ce message. Il sera sauvegardé et mis sur l'embed. Par défaut, l'émoji est : 🗒"
            )
            symb, user = await self.bot.wait_for("reaction_add", timeout=300)
            if symb.custom_emoji:
                if symb.emoji in guild.emojis:
                    symbole = str(symb.emoji)
                else:
                    symbole = "🗒"
            elif symb.emoji != "🗒":
                symbole = str(symb.emoji)
            else:
                symbole = "🗒"
            await q.delete()
            react = await ctx.send(embed=embed)
            await react.add_reaction(symbole)
            sql = "INSERT INTO TICKET (idM, channelM, channel, num, modulo, limitation, emote, idS) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            id_serveur = ctx.message.guild.id
            id_message = react.id
            chanM = ctx.channel.id
            var = (id_message, chanM, ticket_chan_content, nb_dep_content,mod_content, limit_content, symbole, id_serveur)
            c.execute(sql, var)
            db.commit()
            c.close()
            db.close()
        else:
            await ctx.send("Annulation !", delete_after=30)
            await q.delete()
            return

    @commands.has_permissions(administrator=True)
    @commands.command(aliases=['chan, Channel'], name="Channel", help="Permet de créer un message de création de channels dans une seule catégorie, à l'instar des tickets, sans les paramètres. En outre, les créateurs peuvent nommer leur channel, contrairement aux tickets.", brief="Similaire aux tickets, mais permettant de nommer le channel.", description="Configuration pour une seule catégorie.")
    async def channel(self, ctx):
        def checkValid(reaction, user):
            return ctx.message.author == user and q.id == reaction.message.id and (str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌")
        def checkRep(message):
            return message.author == ctx.message.author and ctx.message.channel == message.channel
        guild = ctx.message.guild
        await ctx.message.delete()
        db = sqlite3.connect("owlly.db", timeout=3000)
        c = db.cursor()
        q = await ctx.send(f"Quel est le titre de l'embed ?")
        rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
        typeM = rep.content
        if typeM == "stop":
            await ctx.send("Annulation !", delete_after=10)
            await rep.delete()
            await q.delete()
            return
        await q.edit(content="Quelle est sa description ?")
        rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
        if rep.content == "stop":
            await ctx.send("Annulation !", delete_after=10)
            await rep.delete()
            await q.delete()
            return
        else:
            desc=rep.content
        await rep.delete()
        await q.edit(content=
            "Dans quel catégorie voulez-vous créer vos channels ? Rappel : Seul un modérateur pourra les supprimer, car ce sont des channels permanents.\n Vous pouvez utiliser le nom ou l'ID de la catégorie !"
        )
        rep = await self.bot.wait_for("message",timeout=300,check=checkRep)
        ticket_chan_content = rep.content
        cat_name = "none"
        if ticket_chan_content == "stop":
            await ctx.send("Annulation !", delete_after=10)
            await q.delete()
            await rep.delete()
            return
        else:
            if ticket_chan_content.isnumeric():
                ticket_chan_content = int(ticket_chan_content)
                cat_name = get(guild.categories, id=ticket_chan_content)
                if ticket_chan_content == "None":
                    await ctx.send("Erreur : Cette catégorie n'existe pas !",delete_after=30)
                    await q.delete()
                    await rep.delete()
                    return
            else:
                ticket_chan_content = await self.search_cat_name(ctx, ticket_chan_content)
                if ticket_chan_content == 12:
                    await ctx.send("Aucune catégorie portant un nom similaire existe, vérifier votre frappe.",delete_after=30)
                    await q.delete()
                    await rep.delete()
                    return
                else:
                    cat_name = get(guild.categories, id=ticket_chan_content)
                    await rep.delete()
        await q.edit(conten=f"Quelle couleur voulez vous utiliser ? \n 0 donne une couleur aléatoire.")
        rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
        col = rep.content
        if col == "stop":
            await ctx.send("Annulation !", delete_after=30)
            await q.delete()
            await rep.delete()
            return
        elif col == 0:
            col = await Colour.random()
        else:
            col=await self.convertColor(ctx,col)
        await rep.delete()
        await q.edit(content="Voulez-vous ajouter une image ?")
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for("reaction_add",timeout=300,check=checkValid)
        if reaction.emoji == "✅":
            await q.clear_reactions()
            await q.edit(content=
                "Merci d'envoyer l'image. \n**⚡ ATTENTION : Le message sera supprimé après la configuration, vous devez donc utiliser un lien permanent (hébergement sur un autre channel/serveur, imgur, lien google...)**"
            )
            rep = await self.bot.wait_for("message",timeout=300,check=checkRep)
            img_content = rep.content
            if img_content == "stop":
                await ctx.send("Annulation !", delete_after=10)
                await q.delete()
                await rep.delete()
                return
            else:
                img_content = self.checkImg(ctx, img_content)
                if img_content=="Error":
                    await ctx.send("Erreur ! Votre lien n'est pas une image valide.", delete_after=60)
                    await q.delete()
                    await rep.delete()
                    return
                else:
                    await rep.delete()
        else:
            await q.clear_reactions()
            img_content = "none"
        guild = ctx.message.guild
        await q.edit(content=
            f"Vos paramètres sont : \n Titre : {typeM} \n Catégorie : {cat_name}. \n\n Confirmez-vous ces paramètres ?"
        )
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for("reaction_add",timeout=300,check=checkValid)
        if reaction.emoji == "✅":
            await q.clear_reactions()
            embed = discord.Embed(title=typeM,description=desc,color=col)
            if img_content != "none":
                embed.set_image(url=img_content)
            await q.edit(content=
                "Vous pouvez choisir l'émoji de réaction en réagissant à ce message. Il sera sauvegardé et mis sur l'embed. Par défaut, l'émoji est : 🗒"
            )
            symb, user = await self.bot.wait_for("reaction_add", timeout=300)
            if symb.custom_emoji:
                if symb.emoji in guild.emojis:
                    symbole = str(symb.emoji)
                else:
                    symbole = "🗒"
            elif symb.emoji != "🗒":
                symbole = str(symb.emoji)
            else:
                symbole = "🗒"
            await q.delete()
            react = await ctx.send(embed=embed)
            await react.add_reaction(symbole)
            sql = "INSERT INTO SOLO_CATEGORY (idM, channelM, category, idS, emote) VALUES (?, ?, ?, ?, ?)"
            id_serveur = ctx.message.guild.id
            id_message = react.id
            chanM = ctx.channel.id
            var = (id_message, chanM, ticket_chan_content, id_serveur, symbole)
            c.execute(sql, var)
            db.commit()
            c.close()
            db.close()
        else:
            await ctx.send("Annulation !", delete_after=30)
            await q.delete()
            return

    @commands.has_permissions(administrator=True)
    @commands.command(aliases=['cat', 'categories'], brief="Configuration d'un créateur pour plusieurs catégorie", help="Permet de créer divers channels dans plusieurs catégories qui seront recherchées sur le serveur. La configuration offre une option pour autoriser ou nom le nommage automatique des channels.", description="Pour plusieurs catégories, 9 au maximum.")
    async def category(self, ctx):
        def checkValid(reaction, user):
            return ctx.message.author == user and q.id == reaction.message.id and (str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌")
        def checkRep(message):
            return message.author == ctx.message.author and ctx.message.channel == message.channel
        emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
        db = sqlite3.connect("owlly.db", timeout=3000)
        c = db.cursor()
        chan = []
        q = await ctx.send(
            "Merci d'envoyer l'ID des catégories (ou leurs noms) que vous souhaitez utiliser pour cette configuration. \n Utiliser `stop` pour valider la saisie et `cancel` pour annuler la commande. "
        )
        while True:
            channels = await self.bot.wait_for("message", timeout=300, check=checkRep)
            await channels.add_reaction("✅")
            if channels.content.lower() == 'stop':
                await channels.delete()
                await ctx.send("Validation en cours !", delete_after=5)
                break
            elif channels.content.lower() == 'cancel':
                await channels.delete()
                await ctx.send("Annulation !", delete_after=30)
                await q.delete()
                return
            else:
                chan_search = channels.content
                if chan_search.isnumeric():
                    chan_search = int(chan_search)
                else:
                    chan_search = await self.search_cat_name(ctx, chan_search)
            chan.append(str(chan_search))
            await channels.delete(delay=10)
        if len(chan) >= 10:
            await ctx.send("Erreur ! Vous ne pouvez pas mettre plus de 9 catégories !",delete_after=30)
            await q.delete()
            return
        namelist = []
        guild = ctx.message.guild
        for i in range(0, len(chan)):
            number = int(chan[i])
            cat = get(guild.categories, id=number)
            if cat == "None":
                await ctx.send("Erreur : Cette catégorie n'existe pas !",delete_after=30)
                await q.delete()
                return
            phrase = f"{emoji[i]} : {cat}"
            namelist.append(phrase)
        msg = "\n".join(namelist)
        await q.delete()
        q=await ctx.send(f"Votre channel sera donc créé dans une des catégories suivantes :\n {msg} \n\n Le choix final de la catégories se fait lors des réactions. ")
        parameters_save = q.content
        await q.edit(content="Voulez-vous pouvoir nommer librement les channels créées ?")
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
        name_para = 0
        if reaction.emoji == "✅":
            name_para = 1
        else:
            name_para = 0
        await q.clear_reactions()
        await q.edit(content="Quel est le titre de l'embed ?")
        rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
        if rep.content == "stop":
            await ctx.send("Annulation !", delete_after=30)
            await q.delete()
            await rep.delete()
            return
        else:
            titre=rep.content
            await rep.add_reaction("✅")
            await rep.delete(delay=30)
        await q.edit(content="Quelle couleur voulez vous utiliser ?\n 0 donnera une couleur aléatoire")
        rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
        col = rep.content
        if col == "stop":
            await ctx.send("Annulation !", delete_after=30)
            await q.delete()
            await rep.delete()
            return
        elif col == "0":
            col = Colour.random()
        else:
            col=await self.convertColor(ctx, col)
            print('bite')
        print(type(col))
        print(col)
        await q.edit(content="Voulez-vous utiliser une image ?")
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
        if reaction.emoji == "✅":
            await q.clear_reactions()
            await q.edit(content=
                "Merci d'envoyer l'image. \n**⚡ ATTENTION : Le message sera supprimé après l'envoi, vous devez donc utiliser un lien permanent. (hébergement sur un autre channel/serveur, imgur, lien google...)**"
            )
            rep = await self.bot.wait_for("message", timeout=300, check=checkRep)
            img_content = rep.content
            if img_content == "stop":
                await ctx.send("Annulation !", delete_after=10)
                await q.delete()
                await rep.delete()
                return
            else:
                img_content = self.checkImg(ctx, img_content)
                if img_content == "Error":
                    await ctx.send("Erreur ! Votre lien n'est pas une image valide.", delete_after=60)
                    await q.delete()
                    await rep.delete()
                    return
                else:
                    await rep.delete()
        else:
            await q.clear_reactions()
            img_content = "none"
        embed = discord.Embed(title=titre, description=msg, color=col)
        if img_content != "none":
            embed.set_image(url=img_content)
        await q.edit(content=f"Les catégories dans lequel vous pourrez créer des canaux seront : {parameters_save} \n Validez-vous ses paramètres ?")
        await q.add_reaction("✅")
        await q.add_reaction("❌")
        reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
        if reaction.emoji == "✅":
            react = await ctx.send(embed=embed)
            for i in range(0, len(chan)):
                await react.add_reaction(emoji[i])
            category_list_str = ",".join(chan)
            sql = "INSERT INTO CATEGORY (idM, channelM, category_list, idS, config_name) VALUES (?,?,?,?,?)"
            id_serveur = ctx.message.guild.id
            id_message = react.id
            chanM = ctx.channel.id
            var = (id_message, chanM, category_list_str, id_serveur, name_para)
            c.execute(sql, var)
            db.commit()
            c.close()
            db.close()
            await q.delete()
        else:
            await ctx.send("Annulation !", delete_after=10)
            await q.delete()
            c.close()
            db.close()
            return


def setup(bot):
    bot.add_cog(config(bot))
