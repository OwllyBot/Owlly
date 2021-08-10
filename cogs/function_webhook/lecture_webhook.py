import re
import sqlite3
import urllib.request

import discord


async def edit_webhook(message: discord.Message, idS, user):
    db = sqlite3.connect("src/owlly.db", timeout=3000)
    c = db.cursor()
    ref_id = message.reference.message_id
    ref_msg = await message.channel.fetch_message(ref_id)
    perso_name = ref_msg.author.name
    sql = "SELECT idDC WHERE (idS = ? AND idU=? AND Nom = ?)"
    var = (
        idS,
        user,
        perso_name,
    )
    c.execute(sql, var)
    perso_check = c.fetchone()
    if perso_check:
        id_edit = ref_msg.webhook_id
        if isinstance(id_edit, int):
            webhook = await message.channel.fetch_webhook(id_edit)
            await webhook.edit_message(id=ref_id, content=message.content)
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
        NPC = await message.channel.webhooks()
        OwllyE = False
        if len(NPC) > 0:
            # Webhook exists
            for i in NPC:
                if i.name == "OwllyNPC":
                    # OWLLYNPC exists
                    OwllyNPC = i  # Est un webhook
                    OwllyE = True
                    break
        if not OwllyE:
            OwllyNPC = await message.channel.create_webhook(
                name="OwllyNPC",
                avatar=(await bot.user.avatar_url.read()),
                reason="OwllyNPC doesn't exist yet !",
            )
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
