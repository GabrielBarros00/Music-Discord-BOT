import asyncio
from datetime import timedelta

import discord
import wavelink
from discord.ext import commands
from wavelink import (Node, TrackEventPayload, TrackEventType,
                      WebsocketClosedPayload)

from constants import CACHED_BOT_DICT


async def update_nowplaying(guild_id: int, player: wavelink.Player):
    INFOS_DICT: dict = CACHED_BOT_DICT.get(guild_id)
    if INFOS_DICT:
        delete_old: bool = INFOS_DICT.get("DeleteOLD")
        last_ctx: commands.Context = INFOS_DICT.get("LastCTX")
        last_np_message: discord.Message = INFOS_DICT.get("LastNPMessage")
        
        if delete_old and last_np_message:
            try:
                await last_np_message.delete()
            except discord.NotFound:
                pass
            INFOS_DICT["DeleteOLD"] = False
            CACHED_BOT_DICT[guild_id]["LastCTX"] = None
            last_np_message: discord.Message = None
        if delete_old and not last_np_message:
            INFOS_DICT["DeleteOLD"] = False
            CACHED_BOT_DICT[guild_id]["LastCTX"] = None
            
        if last_np_message or not last_np_message:
            embed = discord.Embed(color=discord.Color.green())
            if not player.current.is_stream:
                current_time = str(timedelta(seconds=int(round(player.position/1000, 2))))
                total_time = str(timedelta(seconds=int(round(player.current.duration/1000, 2))))
                embed.title = f'Now Playing: **`{current_time} of {total_time}`**'
            else:
                embed.title = f'Now Playing:'
            embed.description = f'[{player.current.title}]({player.current.uri})'
            
            if not last_np_message and last_ctx:
                message = await last_ctx.send(embed=embed)
                CACHED_BOT_DICT[guild_id]["LastNPMessage"] = message
            else:
                try:
                    await last_np_message.edit(embed=embed)
                except discord.NotFound:
                    CACHED_BOT_DICT[guild_id]["LastNPMessage"] = None
                    CACHED_BOT_DICT[guild_id]["LastCTX"] = None
                except AttributeError:
                    CACHED_BOT_DICT[guild_id]["LastNPMessage"] = None
                    CACHED_BOT_DICT[guild_id]["LastCTX"] = None

class EventsController(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: Node) -> None:
        # print(f"Node {node.id} is ready!")
        pass
    
    @commands.Cog.listener()
    async def on_wavelink_track_event(self, payload: TrackEventPayload) -> None:
        # print(f"Track Event: {dict(payload.__dict__)}")
        if payload.event == TrackEventType.START:
            vc : wavelink.Player = payload.player
            guild_id = int(payload.player.guild.id)
            await update_nowplaying(guild_id, vc)
    
    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: TrackEventPayload) -> None:
        # print(f"Track Started: {dict(payload.__dict__)}")
        pass
    
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: TrackEventPayload) -> None:
        # print(f"Track Ended: {dict(payload.__dict__)}")
        vc : wavelink.Player = payload.player
        if vc.queue.is_empty:
            await asyncio.sleep(5)
            guild_id = int(payload.player.guild.id)
            INFOS_DICT: dict = CACHED_BOT_DICT.get(guild_id)
            last_np_message: discord.Message = INFOS_DICT.get("LastNPMessage")
            
            if last_np_message:
                try:
                    await last_np_message.delete()
                except discord.NotFound:
                    pass
                INFOS_DICT["DeleteOLD"] = False
                last_np_message: discord.Message = None
            await vc.disconnect()
    
    @commands.Cog.listener()
    async def on_wavelink_websocket_closed(self, payload: WebsocketClosedPayload) -> None:
        # print(f"Websocket connection closed: {dict(payload.__dict__)}")
        pass
    
    @commands.Cog.listener()
    async def on_wavelink_stats_update(self, data: dict) -> None:
        # print(f"Stats Update: {data}")
        pass
    
    @commands.Cog.listener()
    async def on_wavelink_player_update(self, data: dict) -> None:
        # print(f"Player Update: {data}")
        guild_id = int(data["guildId"])
        if CACHED_BOT_DICT.get(guild_id):
            if CACHED_BOT_DICT[guild_id].get("Player"):
                player: wavelink.Player = CACHED_BOT_DICT[guild_id]["Player"]
                if not int(player.position/1000) == 0:
                    await update_nowplaying(guild_id, player)

        
async def setup(bot: commands.Bot):
    await bot.add_cog(EventsController(bot))
