import aiohttp
import discord
from discord import app_commands
from discord.ext import commands


class Predictions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_base = bot.api_base_url

    @app_commands.command(
        name="predict",
        description="Prevê o resultado de uma partida de futebol",
    )
    @app_commands.describe(
        home_team="Time da casa (ex: Brasil)",
        away_team="Time visitante (ex: Argentina)",
    )
    async def predict(
        self,
        interaction: discord.Interaction,
        home_team: str,
        away_team: str,
    ):
        await interaction.response.defer()

        async with aiohttp.ClientSession() as session:
            params = {"home_team": home_team, "away_team": away_team}
            url = f"{self.api_base}/api/v1/predictions/predict"

            try:
                async with session.get(url, params=params) as resp:
                    if resp.status == 404:
                        data = await resp.json()
                        await interaction.followup.send(f"❌ {data['detail']}")
                        return

                    if resp.status != 200:
                        await interaction.followup.send(
                            "❌ Erro ao consultar a API. Tente novamente mais tarde."
                        )
                        return

                    data = await resp.json()

                home_name = data["home_team"]
                away_name = data["away_team"]
                home_prob = data["home_win_probability"]
                draw_prob = data["draw_probability"]
                away_prob = data["away_win_probability"]
                score = data["most_likely_score"]
                confidence = data["confidence"]

                embed = discord.Embed(
                    title="⚽ Previsão da Partida",
                    color=0x00FF00,
                )
                embed.add_field(name="🏠 Time da Casa", value=home_name, inline=True)
                embed.add_field(name="✈️ Time Visitante", value=away_name, inline=True)
                embed.add_blank_field(inline=False)

                bar_home = _progress_bar(home_prob, 100)
                bar_draw = _progress_bar(draw_prob, 100)
                bar_away = _progress_bar(away_prob, 100)

                probs = (
                    f"🏠 **{home_name}**: {home_prob:.1f}%\n{bar_home}\n\n"
                    f"🤝 **Empate**: {draw_prob:.1f}%\n{bar_draw}\n\n"
                    f"✈️ **{away_name}**: {away_prob:.1f}%\n{bar_away}"
                )
                embed.add_field(name="📊 Probabilidades", value=probs, inline=False)
                embed.add_blank_field(inline=False)

                embed.add_field(
                    name="🎯 Placar Mais Provável",
                    value=f"**{score}**",
                    inline=True,
                )
                embed.add_field(
                    name="⚡ Confiança",
                    value=f"{confidence:.1f}%",
                    inline=True,
                )

                embed.set_footer(text="Tatuzinho — Football Analytics")
                embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/54/54647.png")

                await interaction.followup.send(embed=embed)

            except (aiohttp.ClientError, ValueError, KeyError, TypeError) as e:
                await interaction.followup.send(
                    f"❌ Erro ao processar a resposta da API: {str(e)}"
                )
                return


def _progress_bar(value: float, max_value: float, width: int = 10) -> str:
    filled = round((value / max_value) * width)
    filled = max(0, min(filled, width))
    empty = width - filled
    return "█" * filled + "░" * empty


async def setup(bot: commands.Bot):
    await bot.add_cog(Predictions(bot))
