import asyncio
from datetime import datetime, timedelta

import discord
import pytz
import wavelink
from discord.ext import commands
from wavelink import (Node, TrackEventPayload, TrackEventType,
                      WebsocketClosedPayload)

from utils import (EmptyNowPlayingManager, NowPlayingEmbed, NowPlayingManager,
                   database_manager, get_nowplaying_manager,
                   get_wavelink_player)


async def update_nowplaying(self, guild_id: int, event: [TrackEventType] = None):
    np_manager: NowPlayingManager = get_nowplaying_manager(self, guild_id)
    if not np_manager == EmptyNowPlayingManager and hasattr(np_manager.player, "current"):
        delete_old = np_manager.delete_old
        _player = np_manager.player
        last_ctx = np_manager.ctx
        last_np_message = np_manager.last_np_message
        
        
        if last_np_message:
            if last_np_message.created_at + timedelta(hours=1) < datetime.now(tz=pytz.UTC):
                delete_old = last_np_message
        
        if delete_old:
            try:
                await delete_old.delete()
            except discord.NotFound:
                pass
            np_manager._delete_old = False
        
        if not _player:
            _player = await get_wavelink_player(last_ctx)
        
        embed = await NowPlayingEmbed(_player, event).embed
        
        if not last_np_message or delete_old:
            message = await last_ctx.send(embed=embed)
        else:
            message = await last_np_message.edit(embed=embed)
        np_manager.last_np_message = message

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
            # vc : wavelink.Player = payload.player
            guild_id = int(payload.player.guild.id)
            await update_nowplaying(self, guild_id, payload.event)
    
    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: TrackEventPayload) -> None:
        # print(f"Track Started: {dict(payload.__dict__)}")
        pass
    
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: TrackEventPayload) -> None:
        # print(f"Track Ended: {dict(payload.__dict__)}")
        vc : wavelink.Player = payload.player
        auto_queue = database_manager.get_values(int(vc.guild.id), "auto_queue")["auto_queue"]
        if vc.queue.is_empty and not auto_queue:
            await asyncio.sleep(5)
            guild_id = int(payload.player.guild.id)
            np_manager: NowPlayingManager = get_nowplaying_manager(self, guild_id)
            last_np_message = np_manager.last_np_message
            
            if last_np_message:
                try:
                    await last_np_message.delete()
                except discord.NotFound:
                    pass
            np_manager.reset_all()
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
        np_manager: NowPlayingManager = get_nowplaying_manager(self, guild_id)
        player = np_manager.player
        if player:
            if not int(player.position/1000) == 0:
                await update_nowplaying(self, guild_id)

        
async def setup(bot: commands.Bot):
    await bot.add_cog(EventsController(bot))
