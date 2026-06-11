import asyncio
import logging
import os
from urllib.parse import urlparse

import aiohttp
from aiohttp import web
import discord
from discord.ext import commands

from discord_bot.config import DISCORD_BOT_TOKEN, API_BASE_URL, PROXY_URL

logger = logging.getLogger("tatuzinho")


class TatuzinhoBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        kwargs = {"reconnect": True}
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
        await self.load_extension("discord_bot.cogs.teams")
        await self.tree.sync()

    async def on_ready(self):
        logger.info("Bot logado como %s", self.user)

    async def on_disconnect(self):
        logger.warning("Bot desconectado do Discord")

    async def on_resumed(self):
        logger.info("Bot reconectou ao Discord")


async def run_health_server():
    app = web.Application()
    app.router.add_get("/health", lambda r: web.Response(text="ok"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", "8080")))
    await site.start()
    logger.info("Health server rodando na porta %s", os.getenv("PORT", "8080"))
    return runner


async def watchdog(bot: commands.Bot, interval: int = 30, timeout: int = 120):
    disconnected_since = None
    while True:
        await asyncio.sleep(interval)

        if bot.is_closed():
            logger.critical("Bot fechado. Reiniciando processo...")
            os._exit(1)

        if not bot.is_ready():
            now = asyncio.get_event_loop().time()
            if disconnected_since is None:
                disconnected_since = now
            elif now - disconnected_since > timeout:
                logger.critical(
                    "Bot desconectado por mais de %ds. Reiniciando...", timeout
                )
                os._exit(1)
        else:
            disconnected_since = None


async def run_bot():
    bot = TatuzinhoBot()
    watchdog_task = asyncio.create_task(watchdog(bot))
    try:
        await bot.start(DISCORD_BOT_TOKEN)
    finally:
        watchdog_task.cancel()
        if not bot.is_closed():
            await bot.close()


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    if not DISCORD_BOT_TOKEN:
        logger.error("DISCORD_BOT_TOKEN nao configurado")
        exit(1)

    await run_health_server()

    retry_delay = 10
    while True:
        try:
            await run_bot()
        except (
            discord.LoginFailure,
            discord.ConnectionClosed,
            aiohttp.ClientError,
            OSError,
        ) as e:
            logger.error(
                "Erro de conexao: %s. Tentando novamente em %ds...", e, retry_delay
            )
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 120)
            continue
        except KeyboardInterrupt:
            break
        else:
            break


if __name__ == "__main__":
    asyncio.run(main())
