import discord
from discord.ext import commands, tasks
from discord.utils import get
from discord import CategoryChannel
from discord import NotFound
import os
import sqlite3
intents = discord.Intents(messages=True, guilds=True,reactions=True, members=True)


class DB_utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def clean_db(self, ctx):
        print("start clean")
        db = sqlite3.connect("owlly_test.db", timeout=3000)
        c = db.cursor()
        sql=("SELECT idM, channelM FROM TICKET WHERE idS=?")
        self.idS=ctx.guild.id
        idS=ctx.guild.id
        c.execute(sql, (idS,))
        ticket = c.fetchall()
        ticketDict = {}
        for i in range(0, len(ticket)):
            extra = {ticket[i][0]: ticket[i][1]}
            ticketDict.update(extra)
        sql=("SELECT idM, channelM FROM CATEGORY WHERE idS=?")
        c.execute(sql, (idS,))
        category = c.fetchall()
        catDict = {}
        for i in range(0, (len(category))):
            extra = {category[i][0]: category[i][1]}
            catDict.update(extra)
        sql=("SELECT idM, channelM FROM SOLO_CATEGORY WHERE idS=?")
        c.execute(sql, (idS,))
        solo=c.fetchall()
        soloDict={}
        for i in range (0, (len(solo))):
            estra={solo[i][0] : solo[i][1]}
            soloDict.update(estra)
        for k, v in soloDict.items():
            chan = self.bot.get_channel(v)
            print(chan)
            try:
                await chan.fetch_message(k)
            except NotFound:
                sql_solo="DELETE FROM SOLO_CATEGORY WHERE idM=?"
                c.execute(sql_solo, (k,))
        for k, v in ticketDict.items():
            chan = self.bot.get_channel(v)
            await chan.fetch_message(k)
            try:
                await chan.fetch_message(k)
            except NotFound:
                sql_solo="DELETE FROM SOLO_CATEGORY WHERE idM=?"
                c.execute(sql_solo, (k,))
        for k, v in catDict.items():
            chan = self.bot.get_channel(v)
            await chan.fetch_message(k)
            try:
                await chan.fetch_message(k)
            except NotFound:
                sql_solo="DELETE FROM SOLO_CATEGORY WHERE idM=?"
                c.execute(sql_solo, (k,))
        db.commit()
        c.close()
        db.close()
        await ctx.send("DB cleanned !", delete_after=30)
        await ctx.message.delete()

def setup(bot):
  bot.add_cog(DB_utils(bot))
