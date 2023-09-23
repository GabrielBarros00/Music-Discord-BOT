from datetime import timedelta

from discord import Color, Embed, Message
from discord.ext import commands
from wavelink import Player, TrackEventType

from exceptions import CurrentNotPlaying
from .utilities import get_wavelink_player


class EmptyNowPlayingManager:
    def __init__(self) -> None:
        super(NowPlayingManager).__init__()

class NowPlayingEmbed:
    def __init__(self, player, event: [TrackEventType]) -> None:
        if not isinstance(player, Player):
            raise TypeError(f"You need to pass the Player class from WaveLink to generate a Embed, not a {type(player)}.")
        if event and not isinstance(event, TrackEventType):
            raise TypeError(f"In event you need to pass a TrackEventType, not a {type(event)}")
        self.player: Player = player
        self._embed = Embed(color=Color.pink())
        self._event = event

    @property
    def is_playing(self):
        return bool(self.player.current)

    @property
    def is_stream(self):
        if not self.is_playing:
            raise CurrentNotPlaying("Player aren't current playing something.")
        return self.player.current.is_stream
    
    def __set_title(self):
        if not self.is_stream:
            if self._event is TrackEventType.START:
                current_time = str(timedelta(seconds=int(0)))
            else:
                current_time = str(timedelta(seconds=int(round(self.player.position/1000, 2))))
            total_time = str(timedelta(seconds=int(round(self.player.current.duration/1000, 2))))
            self._embed.title = f'Now Playing: **`{current_time} of {total_time}`**'
        else:
            self._embed.title = f'Now Playing:'
    
    def __set_description(self):
        self._embed.description = f'[{self.player.current.title}]({self.player.current.uri})'

    async def __set_thumbnail(self):
        player: Player = self.player
        if player.current:
            if callable(getattr(player.current, "fetch_thumbnail")):
                self._embed.set_image(url=await player.current.fetch_thumbnail())
                
    @property
    async def embed(self):
        self.__set_title()
        self.__set_description()
        await self.__set_thumbnail()
        return self._embed

class NowPlayingMessage:
    def __init__(self) -> None:
        self._ctx = None
        self._last_np_message: Message = None
    
    @property
    def ctx(self) -> commands.Context:
        return self._ctx
    
    @ctx.setter
    def ctx(self, new_ctx: commands.Context):
        if not isinstance(new_ctx, commands.Context):
            raise TypeError(f"The new CTX needs to be an Context class from discord, not a {type(new_ctx)}.")
        self._ctx = new_ctx
    
    @property
    def last_np_message(self) -> Message:
        return self._last_np_message

    @last_np_message.setter
    def last_np_message(self, message: Message):
        if not isinstance(message, Message):
            raise TypeError(f"Delete Old property needs to be a Message class from discord, not a {type(message)}.")
        self._last_np_message = message

class NowPlayingManager(NowPlayingMessage):
    def __init__(self,
                cogs_to_consider: list[str] = ["Player", "Queue", "Filters"]
                ) -> None:
        self._delete_old: commands.Context = None
        
        self._player: Player = None
        self._valid_cogs = cogs_to_consider
        super().__init__()
    
    @property
    def player(self) -> Player:
        return self._player
    
    @player.setter
    def player(self, player: commands.Context | Player):
        if not isinstance(player, (commands.Context, Player)):
            raise TypeError(f"Player needs to be Context class from discord or Player class from WaveLink, not a {type(player)}.")
        self._player = player
    
    @property
    def delete_old(self) -> Message:
        return self._delete_old
    
    @delete_old.setter
    def delete_old(self, ctx: Message | bool):
        if not isinstance(ctx, (Message, bool)):
            raise TypeError(f"Delete Old property needs to be a Message class from discord or a bool, not a {type(ctx)}.")
        self._delete_old = ctx
    
    async def update_nowplaying(self, ctx: commands.Context):
        if not self.ctx:
            self.ctx = ctx
        player = await get_wavelink_player(ctx)
        if not self.player:
            self.player = player
        # Check if a newer message is sended to bot current channel.
        if self.last_np_message and ctx.channel.id == self.last_np_message.channel.id:
            if ctx.message.created_at > self.last_np_message.created_at:
                if ctx.command.cog_name in self._valid_cogs:
                    self.delete_old = self.last_np_message
                    self.ctx = ctx

    def reset_all(self):
        self._ctx = None
        self._delete_old = False
        self._player = None
        self._last_np_message = None

class GuildManager:
    def __init__(self):
        self.guild_managers = {}

    def get_manager(self, guild_id):
        if guild_id not in self.guild_managers:
            self.guild_managers[guild_id] = NowPlayingManager()
        return self.guild_managers[guild_id]

    def remove_manager(self, guild_id):
        if guild_id in self.guild_managers:
            del self.guild_managers[guild_id]
