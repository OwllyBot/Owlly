import discord
from discord.colour import Color
from discord.ext import commands, tasks
from discord.utils import get
from typing import Optional
import sqlite3
import re
from discord import Colour


class presentation (commands.Cog, name="Présentation", description="Permet de débuter la présentation d'un personnage suite à la validation d'une fiche."):
	def __init__(self, bot):
		self.bot = bot

	async def start_presentation (self, ctx):
		pass

