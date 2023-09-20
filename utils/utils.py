import discord
import wavelink
from discord.ext import commands
from dotenv import dotenv_values


def get_env() -> dict:
    return dict(dotenv_values(".env"))
    
async def get_wavelink_player(ctx: commands.Context):
    try:
        vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
    except discord.ClientException:
        vc: wavelink.Player = ctx.voice_client
    return vc
