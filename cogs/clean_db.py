from test import select_DB, up_DB
import discord
from discord.ext import commands, tasks
from discord import NotFound
import sqlite3

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True)


class DB_utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def clean_db(self, ctx):
        print("start clean")
        db = sqlite3.connect("owlly.db", timeout=3000)
        c = db.cursor()
        sql = "SELECT idM, channelM FROM TICKET WHERE idS=?"
        self.idS = ctx.guild.id
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
                sql_solo = "DELETE FROM SOLO_CATEGORY WHERE idM=?"
                c.execute(sql_solo, (k,))

        for k, v in catDict.items():
            chan = self.bot.get_channel(v)
            await chan.fetch_message(k)
            try:
                await chan.fetch_message(k)
            except NotFound:
                sql_solo = "DELETE FROM SOLO_CATEGORY WHERE idM=?"
                c.execute(sql_solo, (k,))
        db.commit()
        c.close()
        db.close()
        await ctx.send("DB cleanned !", delete_after=30)
        await ctx.message.delete()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        db = sqlite3.connect("owlly.db", timeout=3000)
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

    async def init_value(self, selection, base, id,var, idw):
        db = sqlite3.connect("owlly.db", timeout=3000)
        c = db.cursor()
        idw = str(idw)
        sql = "SELECT "+selection+" FROM "+base+" WHERE "+id+" = "+idw+""
        c.execute(sql)
        result = c.fetchone()
        if result is None:
            sql="UPDATE +base+ SET "+selection+" = "+var+" WHERE "+id+" = "+idw+""
            c.execute(sql)
            
        
            

def setup(bot):
    bot.add_cog(DB_utils(bot))
