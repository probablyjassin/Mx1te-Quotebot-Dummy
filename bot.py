import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=os.getenv("BOT_PREFIX"),
    intents=intents,
    application_id=int(os.getenv("APPLICATION_ID")),  # int statt str
)

GUILD_ID = int(
    os.getenv("GUILD_ID")
)  # Server für schnelle Slash Command-Synchronisation


# ------------------ Events ------------------
@bot.event
async def on_ready():
    print(f"✅ Eingeloggt als {bot.user}")

    # Slash Commands server-spezifisch synchronisieren
    guild = discord.Object(id=GUILD_ID)
    synced = await bot.tree.sync(guild=guild)
    print(f"🔄 {len(synced)} Slash Commands synchronisiert")


# ------------------ Cogs laden ------------------
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Cog geladen: {filename}")
            except Exception as e:
                print(f"❌ Fehler beim Laden von {filename}: {e}")


# ------------------ Admin-Befehle ------------------
@bot.command()
@commands.is_owner()
async def reload(ctx, extension: str = None):
    if extension:
        try:
            await bot.unload_extension(f"cogs.{extension}")
            await bot.load_extension(f"cogs.{extension}")
            await ctx.send(f"✅ `{extension}` neu geladen")
        except Exception as e:
            await ctx.send(f"❌ Fehler beim Laden von `{extension}`:\n{e}")
    else:
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                name = filename[:-3]
                try:
                    await bot.unload_extension(f"cogs.{name}")
                    await bot.load_extension(f"cogs.{name}")
                    await ctx.send(f"✅ `{name}` neu geladen")
                except Exception as e:
                    await ctx.send(f"❌ Fehler bei `{name}`:\n{e}")

    # Slash Commands synchronisieren
    guild = discord.Object(id=GUILD_ID)
    synced = await bot.tree.sync(guild=guild)
    await ctx.send(f"🔄 {len(synced)} Slash Commands synchronisiert.")


# ------------------ Bot starten ------------------
async def main():
    async with bot:
        await load_cogs()
        await bot.start(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    asyncio.run(main())
