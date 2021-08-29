import sys
import logging
import traceback

import discord.utils
from discord import Client
from discord.ext import commands

logger = logging.getLogger("discordn")


def oauth_url(self, *args, **kwargs):
    return discord.utils.oauth_url(self.user.id, *args, **kwargs)


old_activity_getter = Client.activity.fget


def activity_getter(self):
    if not self.guilds:
        return old_activity_getter(self)
    return self.guilds[0].me.activity


activity = property(fget=activity_getter, fset=Client.activity.fset)


def formatTraceback(err) -> str:
    return "".join(traceback.format_exception(type(err), err, err.__traceback__))


async def on_error(self, event, *args, **kwargs):
    """|coro|

    The default error handler provided by the client.

    By default this prints to :data:`sys.stderr` however it could be
    overridden to have a different implementation.
    Check :func:`~discord.on_error` for more details.
    """
    _, error, _ = sys.exc_info()
    # Get actual error
    err = getattr(error, "original", error)
    # DigiException handling
    if isinstance(err, commands.FancyException):
        message = err.formatMessage()
        if message is not None:
            logger.log(err.level, message)
            logger.error(formatTraceback(error))
    elif isinstance(err, commands.FancyContextException):
        message = str(err)
        if message is not None:
            logger.log(err.level, message)
            logger.error(formatTraceback(error))
    else:
        logger.error(f"Ignoring exception in {event}")
        logger.error(formatTraceback(error))


def patch():
    Client.oauth_url = oauth_url
    Client.activity = activity
    Client.on_error = on_error
