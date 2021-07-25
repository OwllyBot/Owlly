from test import select_DB, up_DB
import discord
from discord.ext import commands, tasks
from discord import NotFound
import sqlite3

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True)


class DB_utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.update_DB_Connect())

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def clean_db(self, ctx):
        print("start clean")
        db = sqlite3.connect("src/owlly.db", timeout=3000)
        c = db.cursor()
        sql = "SELECT idM, channelM FROM TICKET WHERE idS=?"
        idS = ctx.guild.id
        c.execute(sql, (idS,))
        ticket = c.fetchall()
        ticketDict = {}
        for i in range(0, len(ticket)):
            extra = {ticket[i][0]: ticket[i][1]}
            ticketDict.update(extra)
        sql = "SELECT idM, channelM FROM CATEGORY WHERE idS=?"
        c.execute(sql, (idS,))
        category = c.fetchall()
        catDict = {}
        for i in range(0, (len(category))):
            extra = {category[i][0]: category[i][1]}
            catDict.update(extra)

        for k, v in ticketDict.items():
            chan = self.bot.get_channel(v)
            await chan.fetch_message(k)
            try:
                await chan.fetch_message(k)
            except NotFound:
                sql_solo = "DELETE FROM TICKET WHERE idM=?"
                c.execute(sql_solo, (k,))

        for k, v in catDict.items():
            chan = self.bot.get_channel(v)
            await chan.fetch_message(k)
            try:
                await chan.fetch_message(k)
            except NotFound:
                sql_solo = "DELETE FROM CATEGORY WHERE idM=?"
                c.execute(sql_solo, (k,))
        db.commit()
        c.close()
        db.close()
        await ctx.send("DB cleanned !", delete_after=30)
        await ctx.message.delete()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        db = sqlite3.connect("src/owlly.db", timeout=3000)
        c = db.cursor()
        serv = ctx.guild.id
        sql = "SELECT prefix FROM SERVEUR WHERE idS = ?"
        c.execute(sql, (serv,))
        p = c.fetchone()
        p = p[0]
        if isinstance(error, discord.ext.commands.errors.CommandNotFound):
            await ctx.send(
                f"Commande inconnue ! \n Pour avoir la liste des commandes utilisables, utilise `{p}help` ou `{p}command`"
            )

    async def init_value(self, selection, base, id, var, idw):
        db = sqlite3.connect("src/owlly.db", timeout=3000)
        c = db.cursor()
        idw = str(idw)
        sql = (
            "SELECT " + selection + " FROM " + base + " WHERE " + id + " = " + idw + ""
        )
        c.execute(sql)
        result = c.fetchone()
        if result is None:
            sql = (
                "UPDATE +base+ SET "
                + selection
                + " = "
                + var
                + " WHERE "
                + id
                + " = "
                + idw
                + ""
            )
            c.execute(sql)

    async def update_DB_Connect(self):
        await self.bot.wait_until_ready()
        db = sqlite3.connect("src/owlly.db", timeout=3000)
        c = db.cursor()
        server = (
            "INSERT OR IGNORE INTO SERVEUR(prefix, idS, roliste, notes, "
            "rolerm, chanRP, maxDC, sticky, tag, tokenHRP, delete_hrp, delay_hrp) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
        )
        fiche = (
            "INSERT OR IGNORE INTO FICHE(ids, fiche_pj, fiche_pnj, "
            "fiche_validation, "
            "champ_general, champ_physique) VALUES(?,?,?,?,?,?)"
        )
        guilds_list = self.bot.guilds
        for i in guilds_list:
            i = i.id
            servvar = ("?", i, "0", 0, "0", "0", 0, 0, "0", "0", 0, 0)
            fichevar = (i, 0, 0, 0, "0", "0")
            c.execute(server, servvar)
            c.execute(fiche, fichevar)
        db.commit()
        c.close()
        db.close()

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        db = sqlite3.connect("src/owlly.db", timeout=3000)
        c = db.cursor()
        delete = channel.id
        sql = "SELECT created_by FROM AUTHOR WHERE created_by =?"
        c.execute(sql, (delete,))
        verif_ticket = c.fetchone()
        if verif_ticket is not None:
            sql = "SELECT num FROM TICKET WHERE idM = ?"
            c.execute(sql, verif_ticket)
            count = c.fetchone()
            if count > 0:
                count = int(count[0]) - 1
            else:
                count = 0
            sql = "UPDATE TICKET SET num = ? WHERE idM = ?"
            var = (count, (int(verif_ticket[0])))
            c.execute(sql, var)
        sql = "DELETE FROM AUTHOR WHERE channel_id = ?"
        c.execute(sql, (delete,))
        sql = "DELETE FROM TICKET WHERE channelM = ?"
        c.execute(sql, (delete,))
        sql = "DELETE FROM CATEGORY WHERE channelM = ?"
        c.execute(sql, (delete,))
        db.commit()
        c.close()
        db.close()

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        dep = int(member.id)
        idS = int(member.guild.id)
        db = sqlite3.connect("src/owlly.db", timeout=3000)
        c = db.cursor()
        sql = "DELETE FROM AUTHOR WHERE (UserID = ? AND idS = ?)"
        c.execute(
            sql,
            (
                dep,
                idS,
            ),
        )
        sql = "DELETE FROM DC WHERE (idS = ? AND idU=?)"
        c.execute(
            sql,
            (
                idS,
                dep,
            ),
        )
        caract = "DELETE FROM PERSO WHERE (idS = ? AND idP=?)"
        c.execute(
            sql,
            (
                idS,
                dep,
            ),
        )
        db.commit()
        c.close()
        db.close()

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        mid = payload.message_id
        serv = payload.guild_id
        db = sqlite3.connect("src/owlly.db", timeout=3000)
        c = db.cursor()
        sql = "SELECT idM FROM TICKET WHERE idS=?"
        c.execute(sql, (serv,))
        ticket_list = c.fetchall()
        ticket_list = list(sum(ticket_list, ()))
        sql = "SELECT idM FROM CATEGORY WHERE idS = ?"
        c.execute(sql, (serv,))
        cat_list = c.fetchall()
        cat_list = list(sum(cat_list, ()))

        for i in ticket_list:
            if i == mid:
                sql = "DELETE FROM TICKET WHERE idS=?"
                c.execute(sql, (serv,))
        for i in cat_list:
            if i == mid:
                sql = "DELETE FROM CATEGORY WHERE idS = ?"
                c.execute(sql, (serv,))

        db.commit()
        c.close()
        db.close()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        server = guild.id
        db = sqlite3.connect("src/owlly.db", timeout=3000)
        c = db.cursor()
        sql1 = "DELETE FROM AUTHOR WHERE idS = ?"
        sql2 = "DELETE FROM TICKET WHERE idS = ?"
        sql3 = "DELETE FROM CATEGORY WHERE idS = ?"
        sql4 = "DELETE FROM FICHE WHERE idS = ?"
        sql5 = "DELETE FROM DC WHERE idS = ?"
        sql6 = "DELETE FROM JEU WHERE idS = ?"
        sql7 = "DELETE FROM PERSO WHERE idS = ?"
        c.execute(sql1, (server,))
        c.execute(sql2, (server,))
        c.execute(sql3, (server,))
        c.execute(sql4, (server,))
        c.execute(sql5, (server,))
        c.execute(sql7, (server,))
        c.execute(sql6, (server,))
        sql = "DELETE FROM SERVEUR WHERE idS = ?"
        c.execute(sql, (server,))
        db.commit()
        c.close()
        db.close()


def setup(bot):
    bot.add_cog(DB_utils(bot))
