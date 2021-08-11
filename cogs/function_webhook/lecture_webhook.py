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
    sql = "SELECT sticky from SERVEUR WHERE idS=?"
    c.execute(sql, (idS,))
    sticky = c.fetchone()
    web = False
    webcontent = message.content
    if sticky:
        sticky = sticky[0]
    else:
        sticky = "0"
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
    sql = "SELECT idDC WHERE (idS = ? AND idU=? AND Nom = ?)"
    var = (idS, idU, message.author.name)
    c.execute(sql, var)
    perso_check = c.fetchone()
    if perso_check:
        await message.delete()
    c.close()
    c.close()
