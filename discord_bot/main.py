import discord
from discord.ext import commands

from discord_bot.config import DISCORD_BOT_TOKEN, API_BASE_URL


class TatuzinhoBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        self.api_base_url = API_BASE_URL

    async def setup_hook(self):
        await self.load_extension("discord_bot.cogs.predictions")
        await self.tree.sync()

    async def on_ready(self):
        print(f"✅ Bot logado como {self.user}")


if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN:
        print("❌ DISCORD_BOT_TOKEN não configurado")
        exit(1)
    bot = TatuzinhoBot()
    bot.run(DISCORD_BOT_TOKEN)
