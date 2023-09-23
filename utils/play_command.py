from random import choice

from discord.ext.commands import Context
from discord import Color, Embed
from wavelink.ext.spotify import SpotifyTrack
from wavelink.tracks import (SoundCloudPlaylist, SoundCloudTrack,
                             YouTubePlaylist, YouTubeTrack)


class SpotifyPlaylist:
    pass

class Play:
    def __init__(self, track: SpotifyTrack | YouTubeTrack | YouTubePlaylist | SoundCloudPlaylist | SoundCloudTrack, ctx: Context) -> None:
        self._track = track
        self._ctx = ctx
        self._embed = Embed(color=Color.green())
    
    @property
    async def embed(self):
        await self.__generate_embed()
        return self._embed
    
    @property
    def track_type(self):
        if isinstance(self._track, YouTubePlaylist):
            return YouTubePlaylist
        elif isinstance(self._track, SoundCloudPlaylist) and len(self._track.tracks) > 1:
            return SoundCloudPlaylist
        elif isinstance(self._track, list) and isinstance(self._track[0], SpotifyTrack) and len(self._track) > 1:
            return SpotifyPlaylist
        elif isinstance(self._track, list) and isinstance(self._track[0], SpotifyTrack) and len(self._track) == 1:
            return SpotifyTrack
        elif isinstance(self._track[0], SoundCloudTrack):
            return SoundCloudTrack
        elif isinstance(self._track[0], YouTubeTrack):
            return YouTubeTrack

    def __set_title(self):
        if self.track_type in [YouTubePlaylist, SoundCloudPlaylist, SpotifyPlaylist]:
            self._embed.title = "Playlist Enqueued."
        else:
            self._embed.title = "Track Enqueued."
    
    def __set_description(self):
        if self.track_type in [YouTubePlaylist, SoundCloudPlaylist]:
            self._embed.description = f'{self._track.name} - {len(self._track.tracks)} tracks'
        elif self.track_type == SpotifyPlaylist:
            self._embed.description = f'Total songs: {len(self._track)}'
        elif self.track_type == SpotifyTrack:
            self._embed.description = f'{self._track[0].title}'
        else:
            self._embed.description = f'[{self._track[0].title}]({self._track[0].uri})'
    
    async def __set_thumbnail(self):
        if self.track_type == YouTubePlaylist:
            self._embed.set_image(url=await self._track.tracks[self._track.selected_track].fetch_thumbnail())
        elif self.track_type == SpotifyTrack:
            self._embed.set_image(url=choice(self._track).images[0])
        elif self.track_type == YouTubeTrack:
            self._embed.set_image(url=await self._track[0].fetch_thumbnail())
    
    def __set_footer(self):
        self._embed.set_footer(
            text=f"Added by: {self._ctx.author.display_name}",
            icon_url=self._ctx.author.avatar.url
            )
    
    def __set_timestamp(self):
        self._embed.timestamp = self._ctx.message.created_at
    
    async def __generate_embed(self):
        self.__set_title()
        self.__set_description()
        await self.__set_thumbnail()
        self.__set_footer()
        self.__set_timestamp()
    
    @property
    def track(self):
        if self.track_type in [YouTubePlaylist, SoundCloudPlaylist]:
            return self._track.tracks
        elif self.track_type == SpotifyPlaylist:
            return self._track
        else:
            return self._track[0]
