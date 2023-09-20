import asyncio

import discord
import wavelink
from discord.ext import commands
from wavelink.ext import spotify
from wavelink.filters import Filter

from constants import CACHED_BOT_DICT
from utils import database_manager, get_env, get_wavelink_player


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

@bot.before_invoke
async def before_command(ctx: commands.Context):
    if ctx.command.cog_name == "Filters":
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        if not vc._filter:
            await vc.set_filter(Filter())
    if ctx.command.cog_name == "Player":
        if not CACHED_BOT_DICT.get(ctx.guild.id):
            CACHED_BOT_DICT.update({ctx.guild.id: {}})

for cog_file in cogs_files:
    asyncio.run(bot.load_extension(f"cogs.{cog_file}"))

bot.run(env["BOT_TOKEN"])
