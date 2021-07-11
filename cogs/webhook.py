import discord
from discord.ext import commands
import sqlite3

class Personae (
    commands.cogs,
    name="Personae",
    description="Toutes les commandes afin de créer et gérer un personnage sous forme de webhook"):
    def __init__(self, bot):
        self.bot = bot
