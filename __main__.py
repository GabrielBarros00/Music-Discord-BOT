import asyncio
import logging
import sys

import discord
import wavelink
from discord.ext import commands
from wavelink.ext import spotify
from wavelink.filters import Filter

from utils import (EmptyNowPlayingManager, GuildManager, NowPlayingManager,
                   database_manager, get_env, get_nowplaying_manager,
                   get_wavelink_player)

logging.basicConfig(filename='history.log', level=logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)  # Adicionar manipulador para a saída padrão (console)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
console_handler.setFormatter(formatter)

# Adicionar o manipulador à raiz do logger
root_logger = logging.getLogger()
root_logger.addHandler(console_handler)


def get_prefix(bot, message: discord.Message):
    def get():
        return database_manager.get_values(int(message.guild.id), 'prefix')
    data = get()
    if data:
        return data["prefix"]
    else:
        database_manager.create_guild(guild_id=int(message.guild.id))
        get_prefix(bot=bot, message=message)

class Bot(commands.Bot):
    def __init__(self, env) -> None:
        self.env = env
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(intents=intents, command_prefix=get_prefix, case_insensitive=True)

    async def setup_hook(self) -> None:
        sc: spotify.SpotifyClient = spotify.SpotifyClient(
            client_id=self.env["SPOTIFY_CLIENT_ID"],
            client_secret=self.env["SPOTIFY_CLIENT_SECRET"]
        )

        node: wavelink.Node = wavelink.Node(uri=self.env["LAVALINK_URL"], password=self.env["LAVALINK_PASSWORD"])
        await wavelink.NodePool.connect(client=self, nodes=[node], spotify=sc)


cogs_files = ["player", "event_controller", "basic_commands", "queue", "filters"]

# async def main():
env = get_env()
bot = Bot(env)
bot.guild_manager = GuildManager()

@bot.before_invoke
async def before_command(ctx: commands.Context):
    np_manager: NowPlayingManager = get_nowplaying_manager(ctx, ctx.guild.id)
    if np_manager == EmptyNowPlayingManager:
        await np_manager.update_nowplaying(ctx)
    if ctx.command.cog_name == "Filters":
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        if not vc._filter:
            await vc.set_filter(Filter())

@bot.event
async def on_command_completion(ctx: commands.Context):
    if not ctx.command.name in ["queue", "disconnect"]:
        np_manager: NowPlayingManager = get_nowplaying_manager(ctx, ctx.guild.id)
        await np_manager.update_nowplaying(ctx)
    # Este código será executado após a conclusão de qualquer comando
    voicechannel_name = f"[{ctx.voice_client.channel}]" if ctx.voice_client else ""
    logging.info(f"[{ctx.guild.id}] {ctx.guild.name} ({ctx.message.channel.name}){voicechannel_name}: {ctx.message.content}")

for cog_file in cogs_files:
    asyncio.run(bot.load_extension(f"cogs.{cog_file}"))

bot.run(env["BOT_TOKEN"])
