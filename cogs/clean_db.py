import discord
from discord.ext import commands, tasks
from discord.utils import get
from discord import CategoryChannel
import os
import sqlite3
intents = discord.Intents(messages=True, guilds=True,reactions=True, members=True)

class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.id_message = None

    @commands.command()
    async def clean_db (self, ctx):
        print("start clean")
        db = sqlite3.connect("owlly.db", timeout=3000)
        c = db.cursor()
        c.execute("SELECT idM, channelM FROM TICKET")
        ticket=c.fetchall()
        ticketDict={}
        for i in range(0,len(ticket)):
            extra={ticket[i][0] : ticket[i][1]}
            ticketDict.update(extra)
        c.execute("SELECT idM, channelM FROM CATEGORY")
        category=c.fetchall()
        catDict={}
        for i in range(0,(len(category))):
            extra={category[i][0] : category[i][1]}
            catDict.update(extra)
        for k, v in ticketDict.items():
            print(type(v))
            chan=self.bot.get_channel(v)
            await chan.fetch_message(k)
            self.id_message=k
        for k, v in catDict.items():
            chan = self.bot.get_channel(v)
            await chan.fetch_message(k)
            self.id_message=k
        c.close()
        db.close()
        print("cleaned")
        await ctx.send("Nettoyé !", delete_after=30)
        await ctx.delete()

    @clean_db.error
    async def clean_db_handler(self,error):
        db = sqlite3.connect("owlly.db", timeout=3000)
        c = db.cursor()
        if isinstance(error, discord.NotFound):
            sql_ticket="DELETE FROM TICKET WHERE idM = ?"
            sql_category = "DELETE FROM TICKET WHERE idM = ?"
            c.execute(sql_ticket, self.id_message)
            c.execute(sql_category, self.id_message)
            c.close()
            db.close()
def setup(bot):
  bot.add_cog(CommandErrorHandler(bot))
