from copy import copy
import traceback
import logging

import discord.errors
from discord.ext.commands.bot import BotBase
from discord.ext.commands import Cog
from discord.ext import commands

logger = logging.getLogger(__package__)


old_init = BotBase.__init__


def init(self, *args, extensions=(), cogs=(), **kwargs):
    old_init(self, *args, **kwargs)

    for p in extensions:
        self.load_extension(p)
    for p in cogs:
        self.load_extension(p)


class BadMultilineCommand(commands.errors.CommandError):
    """A multiline command is being run in the middle of a list of commands"""
    pass


def find_one(iterable):
    try:
        return next(iterable)
    except StopIteration:
        return None


async def process_commands(self, message):
    if message.author.bot:
        return

    # F*** smart quotes.
    message.content = message.content.replace("“", "\"")
    message.content = message.content.replace("”", "\"")
    message.content = message.content.replace("’", "'")
    message.content = message.content.replace("‘", "'")

    contexts = []

    ctx = await self.get_context(message)

    # No command found, invoke will handle it
    if not ctx.command:
        await self.invoke(ctx)
        return

    # One multiline command (command string starts with a multiline command)
    if ctx.command.multiline:
        await self.invoke(ctx)
        return

    # Multiple commands (first command is not multiline)
    lines = message.content.split("\n")
    messages = []
    for line in lines:
        msg = copy(message)
        msg.content = line
        messages.append(msg)
    contexts = [await self.get_context(msg) for msg in messages]

    # If at least one of the lines does not start with a prefix, then ignore all the lines
    not_command = find_one(ctx for ctx in contexts if ctx.invoked_with is None)
    if not_command:
        return

    # If at least one of the lines don't match to a command, then throw an error for that command
    bad_command = find_one(ctx for ctx in contexts if ctx.command is None)
    if bad_command:
        await self.invoke(bad_command)
        return

    # If at least one of the lines is a multi-line command (these are only allowed as the first command)
    multiline_command = find_one(ctx for ctx in contexts if ctx.command.multiline)
    if multiline_command:
        username = multiline_command.author.display_name
        await multiline_command.command.dispatch_error(multiline_command, commands.errors.BadMultilineCommand(f"{username} tried to run a multi-line command in the middle of a sequence."))
        return

    # If all the lines have a command, then run them in order
    for ctx in contexts:
        await self.invoke(ctx)


def formatTraceback(err) -> str:
    return "".join(traceback.format_exception(type(err), err, err.__traceback__))


class Emojis:
    info = ":information_source:"
    warning = ":warning:"
    error = ":no_entry:"


async def on_command_error(self, ctx, exception):
    """|coro|

    The default command error handler provided by the bot.

    By default this prints to :data:`sys.stderr` however it could be
    overridden to have a different implementation.

    This only fires if you do not specify any listeners for command error.
    """
    if self.extra_events.get('on_command_error', None):
        return

    if hasattr(ctx.command, 'on_error'):
        return

    cog = ctx.cog
    if cog:
        if Cog._get_overridden_method(cog.cog_command_error) is not None:
            return

    # Get actual error
    err = getattr(exception, "original", exception)

    emojis = on_command_error.emojis

    # If we got some bad arguments, use a generic argument exception error
    if isinstance(err, commands.BadUnionArgument) or isinstance(err, commands.MissingRequiredArgument) or isinstance(err, commands.BadArgument):
        err = commands.ArgumentException()

    if isinstance(err, commands.NotOwner):
        err = commands.AdminPermissionException()

    if isinstance(err, commands.BadMultilineCommand):
        err = commands.MultilineAsNonFirstCommandException()

    if isinstance(err, commands.FancyContextException):
        # DigiContextException handling
        message = await err.formatMessage(ctx)
        if message is not None:
            logger.log(err.level, message)
        userMessage = await err.formatUserMessage(ctx)
        if userMessage is not None:
            await ctx.send(f"{emojis.warning} {userMessage}")
    elif isinstance(err, commands.FancyException):
        # DigiException handling
        message = err.formatMessage()
        if message is not None:
            logger.log(err.level, message)
        userMessage = err.formatUserMessage()
        if userMessage is not None:
            await ctx.send(f"{emojis.warning} {userMessage}")
    elif isinstance(err, commands.CommandNotFound):
        pass
    elif isinstance(err, commands.MissingRequiredArgument):
        await ctx.send(f"{emojis.warning} Missing required argument(s) for `{ctx.prefix}{ctx.command}`.")
    elif isinstance(err, commands.ExpectedClosingQuoteError):
        await ctx.send(f"{emojis.warning} Mismatched quotes in command.")
    elif isinstance(err, commands.InvalidEndOfQuotedStringError):
        await ctx.send(f"{emojis.warning} No space after a quote in command. Are your arguments smushed together?")
    elif isinstance(err, commands.UnexpectedQuoteError):
        await ctx.send(f"{emojis.warning} Why is there a quote here? I'm confused...")
    elif isinstance(err, commands.CheckFailure):
        await ctx.send(f"{emojis.error} You do not have permission to run this command.")
    elif isinstance(err, commands.CommandOnCooldown):
        await ctx.send(f"{emojis.info} You're using that command too fast! Try again in a moment.")
    elif isinstance(err, discord.errors.ClientException):
        await ctx.send(f"{emojis.error} {err.args[0]}")
    else:
        # Default command error handling
        await ctx.send(f"{emojis.error} Something went wrong.")
        logger.error(f"Ignoring exception in command {ctx.command}:")
        logger.error(formatTraceback(exception))


on_command_error.emojis = Emojis


async def on_message_edit(self, before, after):
    # run editted commands
    if before.content == after.content:
        return
    await self.process_commands(after)


def patch():
    commands.errors.BadMultilineCommand = BadMultilineCommand
    commands.BadMultilineCommand = BadMultilineCommand
    BotBase.__init__ = init
    BotBase.process_commands = process_commands
    BotBase.on_command_error = on_command_error
    BotBase.on_message_edit = on_message_edit
