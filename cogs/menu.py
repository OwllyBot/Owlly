import discord
from discord.ext import commands, tasks
from discord.utils import get
from typing import Optional
import sqlite3
import re
from discord import Colour
from discord.ext.commands import ColourConverter
from cogs.Menu_fonction import config_creators as cfg

class menu(commands.Cog, name="Créateur", description="Permet de créer les messages pour créer des channels dans les catégories."):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.has_permissions(administrator=True)
    @commands.command(aliases=['tick'], name="Ticket", brief="Débute la configuration des tickets", help="Permet de créer la configuration des tickets avec divers paramètres, notamment ceux le numéros dans le nom, ainsi que le moment où ce numéros va se reset.", description="Configuration pour une seule catégorie.")
    async def ticket(self, ctx):
        emoji = ["1️⃣", "2️⃣", "3️⃣"]
        def checkValid(reaction, user):
            return ctx.message.author == user and q.id == reaction.message.id and str(reaction.emoji) in emoji
        embed=discord.Embed(title="Menu des tickets", color=Colour.Blurple())
        embed.add_field(name="1️⃣", value="Créer un nouveau créateur de ticket.")
        embed.add_field(name="2️⃣", value="Modifier un créateur de ticket.")
        embed.add_field(name="3️⃣", value="Afficher la liste des paramètres d'un ticket.")
        q=await ctx.send(embed=embed)
        q.add_reaction("1️⃣")
        q.add_reaction("2️⃣")
        q.add_reaction("3️⃣")
        reaction, user=await self.bot.wait_for("reaction_add", timeout=300, check=checkValid)
        if reaction.emoji == "1️⃣":
            cfg.create_ticket(ctx)

def setup(bot):
    bot.add_cog(menu(bot))
