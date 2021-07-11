import discord
from discord.ext import commands
import sqlite3
from cogs.webhook import gestionWebhook as gestion
from cogs.webhook import lecture_webhook as lecture
from cogs.webhook import menu_webhook as menu
#REPO PUBLIQUE

class Personae(
    commands.cogs,
    name="Personae",
    description="Toutes les commandes afin de créer et gérer un personnage sous forme de webhook",
):
    def __init__(self, bot):
        self.bot = bot
