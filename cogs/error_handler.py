import discord
import traceback
import sys
from discord.ext import commands
import asyncio
import inspect


class CommandErrorHandler(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		"""The event triggered when an error is raised while invoking a command.
		Parameters
		------------
		ctx: commands.Context
						The context used for command invocation.
		error: commands.CommandError
						The Exception raised.
		"""

		# This prevents any commands with local handlers being handled here in on_command_error.
		if hasattr(ctx.command, 'on_error'):
			return

		# This prevents any cogs with an overwritten cog_command_error being handled here.
		cog = ctx.cog
		if cog:
			if cog._get_overridden_method(cog.cog_command_error) is not None:
				return

		ignored = (commands.CommandNotFound, )

		# Allows us to check for original exceptions raised and sent to CommandInvokeError.
		# If nothing is found. We keep the exception passed to on_command_error.
		error = getattr(error, 'original', error)

		# Anything in ignored will return and prevent anything happening.
		if isinstance(error, ignored):
			return

		if isinstance(error, commands.DisabledCommand):
			await ctx.send(f'{ctx.command} a été désactivé.')

		elif isinstance(error, commands.NoPrivateMessage):
			try:
				await ctx.author.send(f'{ctx.command} ne peut pas être utilisé dans des messages privés.')
			except discord.HTTPException:
				pass
		elif isinstance(error, commands.BadArgument):
			await ctx.send('Mauvais argument !')

		elif isinstance(error, commands.MissingRequiredArgument):
			await ctx.send(f"Le paramètre `{error.param.name}` est absent !")

		elif isinstance(error, asyncio.TimeoutError):
			await ctx.send("Vous avez mis trop de temps à répondre, annulation...", delete_after=30)

		else:
			# All other Errors not returned come here. And we can just print the default TraceBack.
			print('Ignoring exception in command {}:'.format(
				ctx.command), file=sys.stderr)
			traceback.print_exception(
				type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
	bot.add_cog(CommandErrorHandler(bot))
