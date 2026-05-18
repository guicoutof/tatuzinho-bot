import asyncio
import os

import aiohttp
from aiohttp import web
import discord
from discord.ext import commands
from urllib.parse import urlparse

from discord_bot.config import DISCORD_BOT_TOKEN, API_BASE_URL, PROXY_URL


class TatuzinhoBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        kwargs = {}
        if PROXY_URL:
            kwargs["proxy"] = PROXY_URL
            parsed = urlparse(PROXY_URL)
            if parsed.username and parsed.password:
                kwargs["proxy_auth"] = aiohttp.BasicAuth(
                    parsed.username, parsed.password
                )
        super().__init__(command_prefix="!", intents=intents, **kwargs)
        self.api_base_url = API_BASE_URL

    async def setup_hook(self):
        await self.load_extension("discord_bot.cogs.predictions")
        await self.tree.sync()

    async def on_ready(self):
        print(f"✅ Bot logado como {self.user}")


async def run_health_server():
    app = web.Application()
    app.router.add_get("/health", lambda r: web.Response(text="ok"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", "8080")))
    await site.start()
    print(f"✅ Health server rodando na porta {os.getenv('PORT', '8080')}")
    await asyncio.Event().wait()


async def main():
    if not DISCORD_BOT_TOKEN:
        print("❌ DISCORD_BOT_TOKEN não configurado")
        exit(1)

    bot = TatuzinhoBot()

    await asyncio.gather(
        run_health_server(),
        bot.start(DISCORD_BOT_TOKEN),
    )


asyncio.run(main())
