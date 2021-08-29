import logging

from discord.ext import commands


def getFullname(o):
    moduleName = o.__class__.__module__
    if moduleName == "builtins":
        moduleName = ""
    if moduleName:
        moduleName = f"{moduleName}."

    className = o.__class__.__name__
    fullname = f"{moduleName}{className}"
    return fullname


class FancyException(Exception):
    level = logging.WARNING

    def formatMessage(self):
        return None

    def formatUserMessage(self):
        return None

    def __repr__(self):
        return getFullname(self)

    def __str__(self):
        return self.formatMessage() or self.formatUserMessage() or repr(self)


class FancyContextException(Exception):
    level = logging.WARNING

    async def formatMessage(self, ctx):
        return None

    async def formatUserMessage(self, ctx):
        return None

    def __repr__(self):
        return getFullname(self)

    def __str__(self):
        return repr(self)


class ArgumentException(FancyContextException):
    async def formatUserMessage(self, ctx):
        return f"Please enter `{ctx.prefix}{ctx.invoked_with} {ctx.command.signature}`."


class AdminPermissionException(FancyContextException):
    async def formatMessage(self, ctx):
        usernick = ctx.author.display_name
        return f"{usernick} tried to run an admin command."

    async def formatUserMessage(self, ctx):
        usernick = ctx.author.display_name
        return f"{usernick} tried to run an admin command. This incident will be reported."


class MultilineAsNonFirstCommandException(FancyContextException):
    async def formatMessage(self, ctx):
        usernick = ctx.author.display_name
        return f"{usernick} tried to run a multi-line command in the middle of a sequence."

    async def formatUserMessage(self, ctx):
        return "You are unable to run a command that takes a multi-line argument in the middle of a batch command sequence. Please try running these commands seperately."


def patch():
    commands.errors.FancyException = FancyException
    commands.FancyException = FancyException
    commands.errors.FancyContextException = FancyContextException
    commands.FancyContextException = FancyContextException
    commands.errors.ArgumentException = ArgumentException
    commands.ArgumentException = ArgumentException
    commands.errors.AdminPermissionException = AdminPermissionException
    commands.AdminPermissionException = AdminPermissionException
    commands.errors.MultilineAsNonFirstCommandException = MultilineAsNonFirstCommandException
    commands.MultilineAsNonFirstCommandException = MultilineAsNonFirstCommandException
