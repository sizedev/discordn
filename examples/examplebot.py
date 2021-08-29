import os

import discord
import discord.ext.commands
import discordn

discordn.patch()


class ExampleBot(discord.ext.commands.Bot):
    async def on_first_ready(self):
        await super().on_first_ready()
        print(f"Logged on as {self.user}!")
        print(f"Invite url: {self.oauth_url()}")
        print(f"Load Time: {self.load_time}")

    def on_disconnect(self):
        print("disconnected")


bot = ExampleBot(command_prefix="$")


@bot.command()
async def test(ctx, ducks: int):
    await ctx.send("Hello")


token = os.environ["DISCORD_TOKEN"]
bot.run(token)
