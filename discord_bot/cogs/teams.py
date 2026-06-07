import aiohttp
import discord
from discord import app_commands
from discord.ext import commands


def _format_name(name: str) -> str:
    words = name.split()
    return " ".join(word.capitalize() for word in words)


class Teams(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_base = bot.api_base_url

    @app_commands.command(
        name="teams",
        description="Lista todos os times disponíveis no Tatuzinho",
    )
    async def list_teams(self, interaction: discord.Interaction):
        await interaction.response.defer()

        async with aiohttp.ClientSession() as session:
            url = f"{self.api_base}/api/v1/teams"

            try:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await interaction.followup.send(
                            "❌ Erro ao consultar a API. Tente novamente mais tarde."
                        )
                        return

                    data = await resp.json()

                names = []
                for item in data:
                    raw = item.get("name_pt_br") or item.get("name", "?")
                    names.append(_format_name(raw))

                if not names:
                    await interaction.followup.send("📭 Nenhum time encontrado.")
                    return

                names.sort()

                group_size = (len(names) + 2) // 3
                groups = [names[i:i + group_size] for i in range(0, len(names), group_size)]

                embed = discord.Embed(title="⚽ Times Disponíveis", color=0x00FF00)

                labels = ["🇦", "🇧", "🇨"]
                for i, group in enumerate(groups):
                    value = "\n".join(f"• {name}" for name in group)
                    embed.add_field(name=labels[i] if i < 3 else "\u200b", value=value, inline=True)

                embed.set_footer(text=f"Total: {len(names)} times")
                embed.set_thumbnail(
                    url="https://cdn-icons-png.flaticon.com/512/54/54647.png"
                )

                await interaction.followup.send(embed=embed)

            except (
                aiohttp.ClientError,
                ValueError,
                KeyError,
                TypeError,
                AttributeError,
                discord.HTTPException,
            ) as e:
                await interaction.followup.send(
                    f"❌ Erro: {type(e).__name__}: {str(e)}"
                )
            except Exception:
                try:
                    await interaction.followup.send(
                        "❌ Erro inesperado. Verifique os logs."
                    )
                except Exception:
                    pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Teams(bot))
