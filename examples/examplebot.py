import discord
import discordn

discordn.patch()


class ExampleBot(discord.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")
        print(f"Invite url: {self.oauth_url()}")

    async def on_message(self, m):
        print(f"Message from {m.author}: {m.content}")


bot = ExampleBot()
bot.run("my token goes here")
