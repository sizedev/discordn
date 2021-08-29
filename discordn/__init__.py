__version__ = "1.2.2"

from . import bot, command, embed, member, client, messageable, snowflake, tasks, voiceclient, errors


def patch():
    embed.patch()
    command.patch()
    member.patch()
    bot.patch()
    client.patch()
    messageable.patch()
    snowflake.patch()
    tasks.patch()
    voiceclient.patch()
    errors.patch()
