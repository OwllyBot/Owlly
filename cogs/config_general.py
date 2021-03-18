import discord
from discord.ext import commands, tasks
import sqlite3
import re
intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True)

class CogAdmins(commands.Cog, name="Configuration générale", description="Permet d'enregistrer quelques paramètres pour le bot."):
  def __init__ (self, bot):
    self.bot = bot
    
  @commands.command(name="set_prefix", help="Permet de changer le prefix du bot.", brief="Changement du prefix.")
  @commands.has_permissions(administrator=True)
  async def set_prefix(self, ctx, prefix):
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    sql = "UPDATE SERVEUR SET prefix = ? WHERE idS = ?"
    var = (prefix, ctx.guild.id)
    c.execute(sql, var)
    await ctx.send(f"Prefix changé pour {prefix}")
    db.commit()
    c.close()
    db.close()
      
  @commands.command(aliases=['lexique_config'], help="Permet de configurer le channel dans lequel la commande `search` va faire ses recherches.", brief="Configuration de la recherche de message dans un channel.")
  @commands.has_permissions(administrator=True)
  async def notes_config(self, ctx, chan:discord.TextChannel):
    server = ctx.guild.id
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    sql="UPDATE SERVEUR SET notes=? WHERE idS=?"
    chanID=chan.id
    var=(chanID,server)
    c.execute(sql,var)
    db.commit()
    c.close()
    db.close()
    await ctx.send(f"Le channels des notes est donc {chan}", delete_after=30)
    await ctx.message.delete()
    
  @commands.has_permissions(administrator=True)
  @commands.command(name="Roliste", help="Assignation des rôles assignés par défaut par la commande `member`.", brief="Enregistrement de rôles pour la commande member.", usage="@mention/ID des rôles à enregistrer", aliases=['role_config', 'roliste_config', 'assign'])
  async def roliste(self, ctx, *role: discord.Role):
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    sql = "UPDATE SERVEUR SET roliste = ? WHERE idS = ?"
    role_list=[]
    if (len(role)) > 1:
      for i in role :
        role_list.append(str(i.id))
    else:
      role_str = str(role[0].id)
    role_str= ",".join((role_list))
    var = (role_str, ctx.guild.id)
    c.execute(sql, var)
    phrase=[]
    for i in role:
      phrase.append(i.name)
    phrase=", ".join(phrase)
    await ctx.send(f"Les rôles {phrase} ont bien été enregistré dans la base de données")
    db.commit()
    c.close()
    db.close()


  @commands.has_permissions(administrator=True)
  @commands.command(aliases=["count", "edit_count"], brief="Permet de changer le compteur des ticket", help="Permet de reset, ou changer manuellement le numéro d'un créateur de ticket.", usage="nombre id_message_createur")
  async def recount(self, ctx, arg, ticket_id):
    await ctx.message.delete()
    db = sqlite3.connect("owlly.db", timeout=3000)
    c = db.cursor()
    search_db = "SELECT num FROM TICKET WHERE idM=?"
    sql = "UPDATE TICKET SET num = ? WHERE idM=?"
    search_regex_arg = re.search(
        '(?:(?P<channel_id>[0-9]{15,21})-)?(?P<message_id>[0-9]{15,21})$',
        str(arg))
    if search_regex_arg is None:
        search_regex_arg = re.search(
            '(?:(?P<channel_id>[0-9]{15,21})-)?(?P<message_id>[0-9]{15,21})$',
            str(ticket_id))
        if search_regex_arg is None:
            await ctx.send(
                "Aucun de vos arguments ne correspond à l'ID du message du créateur de ticket...",
                delete_after=30)
            c.close()
            db.close()
            return
        else:
            arg = int(arg)
            ticket_id = int(ticket_id)
    else:
        silent = int(ticket_id)
        ticket_id = int(arg)
        arg = silent
    c.execute(search_db, (ticket_id, ))
    search = c.fetchone()
    if search is None:
        await ctx.send("Aucun ne ticket ne possède ce numéro.")
        c.close()
        db.close()
        return
    else:
        var = (arg, (ticket_id))
        c.execute(sql, var)
        db.commit()
        c.close()
        db.close()
        await ctx.send(f"Le compte a été fixé à : {arg}")  

def setup(bot):
  bot.add_cog(CogAdmins(bot))
