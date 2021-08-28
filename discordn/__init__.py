__version__ = "1.0.0"

from discordn import bot, command, embed, member, client, messageable, snowflake, voiceclient


def patch():
    embed.patch()
    command.patch()
    member.patch()
    bot.patch()
    client.patch()
    messageable.patch()
    snowflake.patch()
    voiceclient.patch()
