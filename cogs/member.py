import discord
from discord.ext import commands
from discord.utils import get
import unicodedata
import os
import sqlite3
from discord.ext.commands import TextChannelConverter as tcc
from discord.ext.commands import CommandError
import sqlite3
import os.path
import pyimgur

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True)
CLIENT_ID = os.environ.get("CLIENT_ID")
im = pyimgur.Imgur(CLIENT_ID)


class Personnage(object):
    def __init__(self, champ):
        self.champ = champ

    def __str__(self):
        return str(self.champ)


class memberUtils(commands.Cog, name="Membre", description="Des commandes gérants les membres."):
    def __init__(self, bot):
        self.bot = bot

    async def search_chan(self, ctx, chan: str):
        chan = str(chan)
        try:
            chan = await commands.TextChannelConverter().convert(ctx, chan)
            return chan
        except CommandError:
            chan = "Error"
            return chan

    @commands.Cog.listener()
    async def on_member_join(self, Member):
        name = Member.name
        normal_name = unicodedata.normalize("NFKD", name)
        await Member.edit(nick=normal_name)

    @commands.command(
        usage="@mention *role",
        brief="Donne divers rôles.",
        help="Permet de donner des rôles à un membre, ainsi que les rôles qui ont été inscrits dans la base. Si les rôles n'existent pas, le bot les crée avant.",
    )
    @commands.has_permissions(manage_nicknames=True)
    async def member(self, ctx, user: discord.Member, *role: str):
        fi = self.bot.get_cog("Fiche")
        chartype = "pj"
        addRole = []
        infoNew = []
        db = sqlite3.connect("owlly.db", timeout=3000)
        c = db.cursor()
        sql = "SELECT roliste FROM SERVEUR WHERE idS=?"
        c.execute(sql, (ctx.guild.id,))
        defaut = c.fetchone()
        if defaut is not None:
            defaut = ",".join(defaut)
            defaut = defaut.split(",")
            for i in defaut:
                rol_save = i
                try:
                    i = get(ctx.guild.roles, id=int(i))
                    await user.add_roles(i)
                except AttributeError:
                    await ctx.send(
                        f"Attention, le rôle {rol_save} a été supprimé, il ne peut donc pas être rajouté sur le joueur !"
                    )
                    pass
        for i in role:
            i = i.replace("<", "")
            i = i.replace(">", "")
            i = i.replace("@", "")
            i = i.replace("&", "")
            if i.isnumeric():
                i = int(i)
                roleCheck = get(ctx.guild.roles, id=i)
            else:
                roleCheck = get(ctx.guild.roles, name=i)
            if roleCheck is None:
                NewRole = await ctx.guild.create_role(name=i, mentionable=True)
                await NewRole.edit(position=17)
                addRole.append(NewRole)
                infoNew.append(NewRole.name)
            else:
                if str(i).isnumeric():
                    i = get(ctx.guild.roles, id=i)
                else:
                    i = get(ctx.guild.roles, name=i)
                addRole.append(i)
        roleInfo = []
        for plus in addRole:
            await user.add_roles(plus)
            roleInfo.append(plus.name)
        roleInfo = ", ".join(roleInfo)
        if (len(infoNew)) > 0:
            infoNew = "\n ◽".join(infoNew)
            roleInfo = roleInfo + " " + infoNew
        # remove role
        sql = "SELECT rolerm FROM SERVEUR where idS= ?"
        c.execute(sql, (ctx.guild.id,))
        rm_role = c.fetchone()
        if rm_role is not None:
            rm_role = ",".join(rm_role)
            rm_role = rm_role.split(",")
            role_rm_info = ""
            for i in rm_role:
                try:
                    i = get(ctx.guild.roles, id=int(i))
                    await user.remove_roles(i)
                    role_rm_info = i.name + ", "
                except AttributeError:
                    pass
            role_rm_info = f", et les rôles {role_rm_info} lui ont été retiré."
        else:
            role_rm_info = ""
        await ctx.send(
            f"{user.mention} est devenu un membre du serveur ! Il·Elle a donc reçu les rôles : {roleInfo}{role_rm_info}",
            delete_after=60,
        )

        await ctx.message.delete()
        await ctx.send(f"Début de la création de la fiche ! \n {user.mention} regardez vos DM !")
        pres = await fi.start_presentation(ctx, user, chartype)
        if pres == "done":
            idS = ctx.guild.id
            fiche, img = await fi.forme(ctx, user, chartype, idS)
            await fi.validation(ctx, fiche, img, chartype, user)


    @commands.command(
       usage="@mention *role",
       brief="Permet de rajouter des rôles à un membres",
       help="Permet à un administrateur de rajouter des roles rapidements.",
       aliases=["setrr", "give_role"])
    @commands.has_permissions(manage_nicknames=True)
    async def set_role (self, ctx, user: discord.Member, *role: str):
        addRole = []
        infoNew = []
        for i in role:
            i = i.replace("<", "")
            i = i.replace(">", "")
            i = i.replace("@", "")
            i = i.replace("&", "")
            if i.isnumeric():
                i = int(i)
                roleCheck = get(ctx.guild.roles, id=i)
            else:
                roleCheck = get(ctx.guild.roles, name=i)
            if roleCheck is None:
                NewRole = await ctx.guild.create_role(name=i, mentionable=True)
                await NewRole.edit(position=17)
                addRole.append(NewRole)
                infoNew.append(NewRole.name)
            else:
                if str(i).isnumeric():
                    i = get(ctx.guild.roles, id=i)
                else:
                    i = get(ctx.guild.roles, name=i)
                addRole.append(i)
        roleInfo = []
        for plus in addRole:
            await user.add_roles(plus)
            roleInfo.append(plus.name)
        roleInfo = ", ".join(roleInfo)
        if (len(infoNew)) > 0:
            infoNew = "\n ◽".join(infoNew)
            roleInfo = roleInfo + " " + infoNew
        await ctx.send(
            f"{user.mention} a reçu de nouveau rôle : {roleInfo}",
            delete_after=60,
            )
    @commands.command(
        usage="@mention",
        brief="Lance la création d'une fiche",
        help="Permet à un joueur ayant sa fiche valider de faire sa présentation.",
        aliases=["add_pj", "validation", "add_pres", "add_presentation"],
    )
    @commands.has_permissions(manage_nicknames=True)
    async def pj(self, ctx, member: discord.Member):
        fi = self.bot.get_cog("Fiche")
        chartype = "pj"
        await ctx.send(f"{member.mention} check tes DM ! 📧")
        await ctx.message.delete()
        pres = await fi.start_presentation(ctx, member, chartype)
        if pres == "done":
            fiche, img = await fi.forme(ctx, member, chartype, ctx.guild.id)
            await fi.validation(ctx, fiche, img, chartype, member)

    @commands.command(
        usage="@mention",
        brief="Lance la création d'une fiche PNJ",
        help="Permet à un joueur ayant sa fiche PNJ validée de faire sa présentation.",
        aliases=["add_pnj", "validation_pnj"],
    )
    @commands.has_permissions(manage_nicknames=True)
    async def pnj(self, ctx, member: discord.Member):
        fi = self.bot.get_cog("Fiche")
        chartype = "pnj"
        await ctx.send(f"{member.mention} check tes DM ! 📧")
        pres = await fi.start_presentation(ctx, member, chartype)
        await ctx.message.delete()
        if pres == "done":
            fiche, img = await fi.forme(ctx, member, chartype, ctx.guild.id)
            await fi.validation(ctx, fiche, img, chartype, member)


def setup(bot):
    bot.add_cog(memberUtils(bot))
