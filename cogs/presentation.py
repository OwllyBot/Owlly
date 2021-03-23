import discord
from discord.colour import Color
from discord.ext import commands, tasks
from discord.utils import get
from typing import Optional
import sqlite3
import re
from discord import Colour
import os.path


class presentation (commands.Cog, name="Présentation", description="Permet de débuter la présentation d'un personnage suite à la validation d'une fiche."):
	def __init__(self, bot):
		self.bot = bot

	async def start_presentation (self, bot, ctx, member : discord.Member):
		'''
		- Ouvre un fichier ou crée un fichier (member.name)
		- Remplie le fichier avec template par défaut
		- Lecture ligne par ligne du fichier : Arrêt quand rencontre du caractère `$`
			- Récupère le nom du champ ⇒ Pose la question au joueur
			- Remplissage
		- Si timeout, ou "stop" : Enregistrement + fermeture
		- Si cancel : Suppression 
		- Si validation : Renvoie vers fiche-validation
		'''
	 	def checkRep(message):
			return message.author == member and isinstance(message.channel, discord.DMChannel)
		if os.path.isfile(f'/fiche/{member.name}.txt'):
			f=open(f'{member.name}.txt', "r+")
		else:
			f=open(f"{member.name}.txt","w+")
			template = f"──────༺ Présentation ༻──────\n**__Nom__** : $\n**__Prénom__** : $\n**__Surnom__** : $\n**__Âge__** : $\n**__Date de naissance__** : $\n**__Sexe__** : $\n**__Race__** : $\n**__Métier__** : $\n\n──────༺Physique༻──────\n**__Yeux__** : $\n**__Cheveux__** : $\n**__Taille__** : $\n**__Poids__** : $\n**__Peau__** : $\n**__Marques__** : $\n\n__**Description :__** $\n\n⋆⋅⋅⋅⊱∘──────∘⊰⋅⋅⋅⋆*Auteur* : {member.mention}\n lien : $\n"
			f.write(template)
		for line in f:
			if "$" in line:
				s=re.search("(nom|prénom|surnom|âge|date de naissance|sexe|race|métier|yeux|cheveux|taille|poids|peau|marques|description|lien)", line, flags=re.IGNORECASE)
				if s.match is not None:
					champ=s.group()
					q=await member.send(f"{champ} ?")
					rep=await bot.wait_for("message", timeout=300, check=checkRep)
					if rep.content.lower() == "cancel":
						await member.send("Annulation")
						os.remove(f"{member.name}.txt")
						return
					elif rep.content.lower() == "stop":
						await member.send("Mise en pause")
						f.close()
					else:
						f.write(f"__{champ.capitalize()}__** : {rep.content}")
