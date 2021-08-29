import sys
import logging
import traceback
from datetime import datetime

import discord.utils
from discord import Client
from discord.ext import commands

logger = logging.getLogger(__package__)


def oauth_url(self, *args, **kwargs):
    return discord.utils.oauth_url(self.user.id, *args, **kwargs)


old_activity_getter = Client.activity.fget


def activity_getter(self):
    if not self.guilds:
        return old_activity_getter(self)
    return self.guilds[0].me.activity


activity = property(fget=activity_getter, fset=Client.activity.fset)


old_dispatch = Client.dispatch


def dispatch(self, event_name, *args, **kwargs):
    new_event_name = None

    if event_name == "ready":
        has_readied = getattr(self, "_has_readied", False)
        if not has_readied:
            new_event_name = "first_ready"
            self._load_end = datetime.now()
            self._has_readied = True
        else:
            new_event_name = "reconnect_ready"

    old_dispatch(self, event_name, *args, **kwargs)
    if new_event_name:
        old_dispatch(self, new_event_name, *args, **kwargs)


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


old_run = Client.run


def run(self, *args, **kwargs):
    self._load_start = datetime.now()
    return old_run(self, *args, **kwargs)


def load_time_getter(self):
    start = getattr(self, "_load_start", None)
    end = getattr(self, "_load_end", None)
    if start is None or end is None:
        return None
    return end - start


load_time = property(fget=load_time_getter)


def patch():
    Client.oauth_url = oauth_url
    Client.activity = activity
    Client.on_error = on_error
    Client.dispatch = dispatch
    Client.run = run
    Client.load_time = load_time
