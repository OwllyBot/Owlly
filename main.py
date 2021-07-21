import discord
from discord.ext import commands
from discord.utils import get
import os
import sqlite3
from pretty_help import PrettyHelp
from discord.ext.commands.help import HelpCommand
from pygit2 import Repository

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True)

# ▬▬▬▬▬▬▬▬▬▬▬ PREFIX ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬


def getprefix(bot, message):
    if message.guild is not None:
        db = sqlite3.connect("src/owlly.db", timeout=3000)
        c = db.cursor()
        prefix = "SELECT prefix FROM SERVEUR WHERE idS = ?"
        c.execute(prefix, (int(message.guild.id),))
        prefix = c.fetchone()
        if prefix is None:
            prefix = "?"
            sql = "INSERT INTO SERVEUR (prefix, idS) VALUES (?,?)"
            var = ("?", message.guild.id)
            c.execute(sql, var)
            db.commit()
        else:
            prefix = prefix[0]
        c.close()
        db.close()
        return prefix
    else:
        prefix = "?"
        return prefix


# ▬▬▬▬▬▬▬▬▬▬▬ COGS ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬


initial_extensions = [
    "cogs.clean_db",
    "cogs.utils",
    "cogs.chan_admin",
    "cogs.author_cmd",
    "cogs.member",
    "cogs.config_general",
    "cogs.error_handler",
    "cogs.fiche",
    "cogs.Administration.admin_fiche",
    "cogs.webhook",
]
repo_name = Repository(".").head.shorthand
bot = commands.Bot(
    command_prefix=getprefix,
    intents=intents,
    activity=discord.Game("ouvrir des portes !"),
)
if __name__ == "__main__":
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(e)

color = discord.Color.blurple()
ending = "Pour voir l'aide sur une commande, utilisez {help.clean_prefix}command\n De même, pour une catégorie, utilisez {help.clean_prefix}categorie."
bot.help_command = PrettyHelp(
    color=color, index_title="Owlly - Aide", ending_note=ending, active_time=300
)


@bot.event
async def on_raw_reaction_add(payload):
    emoji_cat = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    action = payload.emoji
    db = sqlite3.connect("src/owlly.db", timeout=3000)
    c = db.cursor()
    idS = payload.guild_id
    mid = payload.message_id
    channel = bot.get_channel(payload.channel_id)
    msg = await channel.fetch_message(mid)
    user = bot.get_user(payload.user_id)
    guild = discord.utils.find(lambda g: g.id == idS, bot.guilds)

    def checkRep(message):
        return message.author == user and channel == message.channel

    sql = "SELECT channel FROM TICKET WHERE (idS = ? AND idM=?)"
    c.execute(
        sql,
        (
            idS,
            mid,
        ),
    )
    emoji_ticket = c.fetchone()
    sql = "SELECT category_list, config_name FROM CATEGORY WHERE (idS=? AND idM=?)"
    c.execute(
        sql,
        (
            idS,
            mid,
        ),
    )
    catego = c.fetchone()
    create = False

    # SELECT TICKET
    if (emoji_ticket is not None) and (user.bot is False):
        emoji_ticket = emoji_ticket[0]
        chan_create = emoji_ticket
        await msg.remove_reaction(action, user)
        sql = "SELECT num FROM TICKET WHERE idM=?"
        c.execute(sql, (mid,))
        nb = c.fetchone()[0]
        if nb != "Aucun" and nb.isnumeric():
            nb = int(nb)
            sql = "SELECT modulo, limitation FROM TICKET WHERE idM= ?"
            c.execute(sql, (mid,))
            limitation_options = c.fetchall()
            limitation_options = list(sum(limitation_options, ()))
            for i in range(0, len(limitation_options)):
                mod = limitation_options[0]
                limit = limitation_options[1]
            nb += 1
            if limit > 0:
                if mod > 0:
                    if (nb % mod) > limit:
                        nb = (nb + mod) - limit
                else:
                    if nb > limit:
                        nb = 0
        sql = "SELECT name_auto FROM TICKET WHERE idM=?"
        c.execute(sql, (mid,))
        para_name = c.fetchone()[0]
        if para_name == "1":
            q = await channel.send("Merci d'indiquer le nom de la pièce")
            chan_rep = await bot.wait_for("message", timeout=300, check=checkRep)
            await q.delete()
            chan_name = chan_rep.content
            if chan_name == "stop":
                await channel.send("Annulation de la création.", delete_after=30)
                await chan_rep.delete()
            else:
                chan_name = f"{chan_name}"
        elif para_name == "2":
            perso = payload.member.nick
            if nb.isnumeric():
                chan_name = f"{nb} {perso}"
            else:
                chan_name = f"{perso}"
        else:
            perso = payload.member.nick
            if nb.ismeric():
                chan_name = f"{nb} {para_name} {perso}"
            else:
                chan_name = f"{para_name} {perso}"
        if nb.isnumeric():
            sql = "UPDATE TICKET SET num = ? WHERE idM = ?"
            var = (nb, mid)
            c.execute(sql, var)
        create = True

    # ========== SELECT CATEGORY ==============
    elif (catego is not None) and (user.bot is False):
        await msg.remove_reaction(action, user)
        cat = catego[0].split(",")
        config = catego[1]
        for i in range(0, len(emoji_cat)):
            if str(action) == emoji_cat[i]:
                chan_create = int(cat[i])
        category_name = get(guild.categories, id=chan_create)
        if config == 1:
            question = await channel.send(
                f"Catégorie {category_name} sélectionnée. \n Merci d'indiquer le nom de la pièce"
            )
            chan_rep = await bot.wait_for("message", timeout=300, check=checkRep)
            await question.delete()
            chan_name = chan_rep.content
            if chan_name == "stop":
                await channel.send("Annulation de la création.", delete_after=10)
                await chan_rep.delete()
                return
            else:
                chan_name = f"{chan_name}"
                await chan_rep.delete()
        else:
            chan_name = f"{payload.member.nick}"
        create = True
    # ===== CREATION ====
    if create:
        category_name = get(guild.categories, id=chan_create)
        await channel.send(
            f"Création du channel {chan_name} dans {category_name}.", delete_after=30
        )
        category = bot.get_channel(chan_create)
        new_chan = await category.create_text_channel(chan_name)
        overwrite = discord.PermissionOverwrite()
        await new_chan.set_permissions(user, manage_channels=True, manage_messages=True)
        sql = (
            "INSERT INTO AUTHOR (channel_id, userID, idS, created_by) VALUES (?,?,?,?)"
        )
        var = (new_chan.id, user.id, idS, payload.message_id)
        c.execute(sql, var)
        db.commit()
        c.close()
        db.close()


if repo_name == "main":
    token = os.environ.get("DISCORD_BOT_TOKEN")
else:
    token = os.environ.get("DISCORD_BOT_TOKEN_TESTING")
    print(token)
print(token)
bot.run(token)
