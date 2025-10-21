import os
import discord
from discord import app_commands
from discord.ext import commands

QUOTE_CHANNEL_ID = int(os.getenv("QUOTE_CHANNEL_ID"))


class quotes(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @app_commands.command(
        name="quote",
        description="Postet eine Nachricht oder mehrere Nachrichten in den Quote-Channel",
    )
    @app_commands.describe(
        messages="Die Message-Links, die zitiert werden sollen (getrennt durch Leerzeichen)"
    )
    async def quote(self, interaction: discord.Interaction, messages: str):
        channel = self.bot.get_channel(QUOTE_CHANNEL_ID)
        if not channel:
            await interaction.response.send_message(
                "❌ Quote-Channel nicht gefunden.", ephemeral=True
            )
            return

        message_links = messages.split()
        success, failed = [], []

        for link in message_links:
            try:
                parts = link.split("/")
                _, channel_id, message_id = (
                    int(parts[-3]),
                    int(parts[-2]),
                    int(parts[-1]),
                )
                msg_channel = self.bot.get_channel(channel_id)
                msg = await msg_channel.fetch_message(message_id)

                embed = discord.Embed(
                    description=(
                        msg.content if msg.content else "*(Keine Textnachricht)*"
                    ),
                    color=discord.Color.gold(),
                )
                embed.set_author(
                    name=msg.author.display_name, icon_url=msg.author.display_avatar.url
                )
                embed.add_field(name="Original", value=f"[Jump to message]({link})")

                for attachment in msg.attachments:
                    if attachment.content_type and attachment.content_type.startswith(
                        "image"
                    ):
                        embed.set_image(url=attachment.url)
                    else:
                        embed.add_field(
                            name="Anhang",
                            value=f"[{attachment.filename}]({attachment.url})",
                            inline=False,
                        )

                await channel.send(embed=embed)
                success.append(link)
            except Exception as e:
                print(f"Fehler bei {link}: {e}")
                failed.append(link)

        reply_text = ""
        if success:
            reply_text += f"✅ Erfolgreich zitiert:\n" + "\n".join(success) + "\n"
        if failed:
            reply_text += f"❌ Fehler bei:\n" + "\n".join(failed)

        await interaction.response.send_message(reply_text, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(quotes(bot))
