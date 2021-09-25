import re
import sqlite3

import discord


async def edit_webhook(bot, message: discord.Message, idS, user):
    db = sqlite3.connect("src/owlly.db", timeout=3000)
    c = db.cursor()
    ref_id = message.reference.message_id
    ref_msg = message.reference.resolved
    perso_name = ref_msg.author.name
    sql = "SELECT idDC FROM DC WHERE (idS = ? AND idU=? AND Nom = ?)"
    var = (
        idS,
        user,
        perso_name,
    )
    c.execute(sql, var)
    perso_check = c.fetchone()
    if perso_check and isinstance(ref_msg, discord.Message):
        webhook = await get_bot_webhook(bot, message.channel)
        await webhook.edit_message(message_id=ref_id, content=message.content)
        await message.delete()
        return
    c.close()
    db.close()


async def delete_HRP(message: discord.Message, idS):
    db = sqlite3.connect("src/owlly.db", timeout=3000)
    c = db.cursor()
    sql = "SELECT delay_HRP FROM SERVEUR WHERE idS=?"
    c.execute(sql, (idS,))
    delay = c.fetchone()
    if delay:
        delay = delay[0]
    if delay != 0:
        await message.delete(delay=delay)
        return
    c.close()
    db.close()

async def get_bot_webhook(bot, channel : discord.TextChannel):
    """Returns the Owlly webhook used for personae in a text channel.
    If there isn't one, it creates the webhook and returns it."""
    channel_webhooks = await channel.webhooks()
    OwllyNPC = None
    if len(channel_webhooks) :
        # Webhook exists
        for i in channel_webhooks:
            if i.user == bot.user:
                # A Webhook created by the bot exists
                OwllyNPC = i
                break
    if not OwllyNPC:
        OwllyNPC = await channel.create_webhook(
            name="OwllyNPC",
            avatar=(await bot.user.avatar_url.read()),
            reason="OwllyNPC doesn't exist yet !",
        )
    return OwllyNPC


async def switch_persona(bot, message: discord.Message, idS, user):
    db = sqlite3.connect("src/owlly.db", timeout=3000)
    c = db.cursor()
    sql = "SELECT token FROM DC WHERE (idS=? AND idU=?)"
    var = (
        idS,
        user,
        )
    c.execute(sql, var)
    perso = [x[0] for x in c.fetchall()]
    sql = "SELECT sticky,tokenHRP from SERVEUR WHERE idS=?"
    c.execute(sql, (idS,))
    serv_sql = c.fetchone()
    if serv_sql:
        sticky = serv_sql[0]
        HRP = serv_sql[1]
    else:
        sticky = "0"
        HRP = ""
    web = False
    webcontent = message.content
    # Disable character if char active
    disabled = "\!" + HRP  # Each message start with "!tokenHRP will disable active character
    regHRP = re.compile(disabled, re.DOTALL)
    if regHRP.match(message.content) and sticky == 1:  # Disable all sticky char
        sql = "UPDATE DC SET Active = ? WHERE (idS=? AND idU=?)"
        var = (0, idS, user)
        c.executemany(sql, var)
        db.commit()
        c.close()
        db.close()
        return
    for snippet in perso:
        reg = re.compile(snippet, re.DOTALL)
        if reg.match(message.content):
            sql = "SELECT Nom, Avatar FROM DC WHERE (idS=? AND idU=? AND Token = ?)"
            var = (
                idS,
                user,
                snippet,
                )
            c.execute(sql, var)
            char = c.fetchone()
            if char:
                char = [x for x in char]
                web = True
                send = reg.match(message.content)
                webcontent = send.group(1)
                if sticky == "1":
                    sql = (
                        "UPDATE DC SET Active = ? WHERE (idS=? AND idU=? AND Token =?)"
                    )
                    var = (1, idS, user, snippet)
                    c.execute(sql, var)
                    # Disable other active
                    sql = "UPDATE DC SET Active = ? WHERE (idS = ? AND idU=? AND Active = ?)"
                    var = (0, idS, user, 1)
                    c.executemany(sql, var)
                break
    if not web and sticky == "1":
        sql = "SELECT Nom, Avatar FROM DC WHERE (idS = ? AND idU=? AND Active=?)"
        var = (
            idS,
            user,
            1,
        )
        c.execute(sql, var)
        char = c.fetchone()
        if char:
            web = True
            char = [x for x in char]
    if web:
        OwllyNPC = await get_bot_webhook(bot, message.channel)
        await OwllyNPC.send(
            content=webcontent,
            username=char[0],
            avatar_url=char[1],
            allowed_mentions=discord.AllowedMentions.all()
        )
        await message.delete()
        db.commit()
        c.close()
        db.close()


async def delete_persona(idS, idU, message: discord.Message):
    db = sqlite3.connect("src/owlly.db", timeout=3000)
    c = db.cursor()
    sql = "SELECT idDC FROM DC WHERE (idS = ? AND idU=? AND Nom = ?)"
    var = (idS, idU, message.author.name)
    c.execute(sql, var)
    perso_check = c.fetchone()
    if perso_check:
        await message.delete()
    c.close()
    c.close()
