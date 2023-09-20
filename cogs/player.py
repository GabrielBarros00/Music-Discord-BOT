from datetime import timedelta
from random import shuffle, choice

import discord
import wavelink
from discord.ext import commands
from wavelink.ext import spotify
from wavelink.ext.spotify import SpotifySearchType

from constants import CACHED_BOT_DICT
from utils import database_manager, get_wavelink_player


class Player(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.command(aliases=["p", "pnext", "playnext"])
    async def play(self, ctx: commands.Context, *, search: str) -> None:
        """
        Play command.
        
        Accepts Youtube, Spotify, SoundCloud, Twitch and Others(Remote Stream)...
        """
        async def GetAllSpotify_Songs(iterator: iter):
            tracks = list()
            async for track in iterator:
                tracks.append(track)
            return tracks
        
        def reversed_queue(tracks):
            return tracks[::-1]
        
        play_next = ctx.invoked_with in ["pnext", "playnext"]
        async def play_track(track):
            if auto_shuffle and isinstance(track, list):
                shuffle(track)
            if play_next:
                if isinstance(track, list):
                    for song in reversed_queue(track):
                        vc.queue.put_at_front(song)
                else:
                    vc.queue.put_at_front(track)
            else:
                if isinstance(track, list):
                    for song in track:
                        await vc.queue.put_wait(song)
                else:
                    await vc.queue.put_wait(track)
            if not vc.is_playing():
                await vc.play(vc.queue.get(), volume=database_manager.get_values(ctx.guild.id, "volume")["volume"], populate=database_manager.get_values(ctx.guild.id, "auto_queue")["auto_queue"])
        
        auto_shuffle = database_manager.get_values(int(ctx.guild.id), 'auto_shuffle')["auto_shuffle"]
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        vc.autoplay = True
        IsSpotifyTrack = spotify.decode_url(search)
        
        if IsSpotifyTrack:
            if IsSpotifyTrack.type is  SpotifySearchType.playlist:
                track: spotify.SpotifyTrack = await GetAllSpotify_Songs(spotify.SpotifyTrack.iterator(query=search))
            else:
                track: spotify.SpotifyTrack = await spotify.SpotifyTrack.search(query=search)
        else:
            track: wavelink.YouTubeTrack = await wavelink.YouTubeTrack.search(search)
        
        embed = discord.Embed(color=discord.Color.green())
        if isinstance(track, (wavelink.YouTubePlaylist, wavelink.SoundCloudPlaylist)):
            embed.title = 'Playlist Enqueued!'
            embed.description = f'{track.name} - {len(track.tracks)} tracks'
            if not wavelink.SoundCloudPlaylist:
                embed.set_image(url=await track.tracks[track.selected_track].fetch_thumbnail())
            track = track.tracks
            embed.description = f'Total songs: {len(track)}'                
        elif isinstance(track, list):
            if isinstance(track[0], spotify.SpotifyTrack):
                if len(track) > 1:
                    embed.title = 'Playlist Enqueued!'
                    embed.description = f'Total songs: {len(track)}'
                    embed.set_image(url=choice(track).images[0])
                else:
                    track = track[0]
                    embed.title = 'Track Enqueued'
                    embed.description = f'{track.title}'
                    embed.set_image(url=track.images[0])
            else:
                embed.title = 'Track Enqueued'
                track = track[0]
                embed.set_image(url=await track.fetch_thumbnail())
                embed.description = f'[{track.title}]({track.uri})'
        
        await play_track(track)
        if ctx.message.embeds:
            await ctx.message.delete()
        else:
            await ctx.message.delete(delay=5)
        message = await ctx.send(embed=embed)
        
        CACHED_BOT_DICT[ctx.guild.id]["LastCTX"] = ctx
        CACHED_BOT_DICT[ctx.guild.id]["Player"] = vc
        CACHED_BOT_DICT[ctx.guild.id]["DeleteOLD"] = True
    
    @commands.command(aliases=['dc', 'stop'])
    async def disconnect(self, ctx: commands.Context) -> None:
        """
        Disconnect/Stop player command.
        """
        if not ctx.voice_client:
            # We can't disconnect, if we're not connected.
            await ctx.send('Not connected currently.')
        else:            
            vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
            
            vc.queue.reset()
            if vc.queue.is_empty:
                guild_id = int(ctx.guild.id)
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
            await ctx.send('*⃣ | Disconnected.')
        CACHED_BOT_DICT[ctx.guild.id]["DeleteOLD"] = True
    
    @commands.command(aliases=['retomar'])
    async def resume(self, ctx: commands.Context):
        """
        Resume the current song.
        """
        self.canal_atual = ctx.channel.id
        # Criando uma variavel para gerenciar o player do bot.
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        
        if not vc.current:
            await ctx.send("**`I'm not playing anything!`**")
        # Verificando se o player não está pausado. Caso verdadeiro, será enviado uma mensagem alertando que não está pausado.
        elif not vc.is_paused:
            await ctx.send("**`The player isn\'t paused!`**")
        else:
            # Caso esteja pausado. Será despausado o player.
            await vc.resume()
            await ctx.send(f'**`{ctx.author.name}`**: Resumed the song!')
        CACHED_BOT_DICT[ctx.guild.id]["DeleteOLD"] = True
    
    @commands.command(aliases=['pausar'])
    async def pause(self, ctx: commands.Context):
        """
        Pause the current song.
        """
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        # verificar se há musicas tocando para pausar ou não
        if not vc.current:
            await ctx.send("**`I'm not playing anything!`**")
        # Verificando se o player ja está pausado, para que caso esteja pausado, seja retomada a música.
        elif vc.is_paused():
            await vc.resume()
            await ctx.send(f'**`{ctx.author.name}`**: Resumed the song!')
        # Caso não esteja pausado, será pausado a música.
        else:
            await vc.pause()
            await ctx.send(f'**`{ctx.author.name}`**: Paused the song!')
        CACHED_BOT_DICT[ctx.guild.id]["DeleteOLD"] = True
    
    @commands.command()
    async def seek(self, ctx: commands.Context, *, seconds: int):
        """Jump to a specific time in the current track"""
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        if vc.is_playing and not vc.is_paused():
            if not vc.current.is_seekable:
                await ctx.send("**`I can't jump in a specific time. Maybe the currently song is a live?`**")
            if vc.current.duration <= seconds * 1000:
                await ctx.send(
                    f"**`I can't jump in this specific time. This song have {int(vc.current.duration / 1000)} seconds.`**")
            await vc.seek(seconds * 1000)
            await ctx.send(f'**`Jumped to {seconds} seconds in the song.`**')
        else:
            await ctx.send("**`I'm not playing anything!`**")
        CACHED_BOT_DICT[ctx.guild.id]["DeleteOLD"] = True
    
    @commands.command(aliases=['vol', 'volume', 'changevolume'])
    async def change_volume(self, ctx: commands.Context, *, vol: float):
        """Change the player volume.
        Parameters
        ------------
        volume: int [Required]
            The volume to set the player to in percentage. This must be between 1 and 1000.
        """
        if not 0 < vol < 1001:
            CACHED_BOT_DICT[ctx.guild.id]["DeleteOLD"] = True
            await ctx.send('Invalid Volume arguments, the volume needs to be between 1 and 1000.')
        elif not isinstance(vol, (float, int)):
            CACHED_BOT_DICT[ctx.guild.id]["DeleteOLD"] = True
            await ctx.send('Invalid Volume arguments, the volume needs to be and Integer.')
        else:
            vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
            
            await vc.set_volume(vol)
            database_manager.update_values(int(ctx.guild.id), volume=vol)
            await ctx.send(f'**`{ctx.author.name}`**: Definiu o volume para **{vol}%**')
        CACHED_BOT_DICT[ctx.guild.id]["DeleteOLD"] = True
    
    @commands.command(aliases=["pularpara", "skipto"])
    async def skip_to(self, ctx: commands.Context, *, index: int):
        """
        Skip to a specific song in the queue.
        """
        index = int(index)
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        CACHED_BOT_DICT[ctx.guild.id]["DeleteOLD"] = True
        if index <= 0:
            await ctx.send(f'**`Invalid SkipTo arguments, the index can\'t be lower than 0`**')
        elif index == 1:
            await ctx.send(f'**`{ctx.author.name}`**: Skiped to **{vc.queue._queue[0].title}**.')
            await vc.stop()
        elif index - 1 >= vc.queue.count:
            await ctx.send(f'**`Invalid SkipTo arguments, the index can\'t be bigger than queue lenght`**')
        else:
            await ctx.send(f'**`{ctx.author.name}`**: Skiped to **{vc.queue._queue[index-1].title}**.')
            for _ in range(index-1):
                del vc.queue._queue[0]
            await vc.stop()
        CACHED_BOT_DICT[ctx.guild.id]["DeleteOLD"] = True
    
    @commands.command(aliases=["pular"])
    async def skip(self, ctx: commands.Context):
        """
        Skip the current song.
        """
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        if not vc.queue.is_empty or vc.current:
            await ctx.send(f'**`{ctx.author.name}`**: Skiped **{vc.current.title}**.')
            await vc.stop()
        else:
            await ctx.send("**`Queue is empty!`**")
        CACHED_BOT_DICT[ctx.guild.id]["DeleteOLD"] = True
    
    @commands.command(aliases=["loop_all", "loop_song", "loopall", "loopsong"])
    async def loop(self, ctx: commands.Context, *, loop: str =None):
        """
        Set the loop mode.
        """
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        if loop:
            loop = loop.lower().strip()
            if loop in ["all", "queue"]:
                vc.queue.loop = False
                vc.queue.loop_all = True
                await ctx.send(f'**`{ctx.author.name}`**: Definiu o loop para: **QUEUE**')
            elif loop == ["single", "song"]:
                vc.queue.loop_all = False
                vc.queue.loop = True
                await ctx.send(f'**`{ctx.author.name}`**: Definiu o loop para: **SONG**')
            elif loop == ["off", "disable", "disabled"]:
                vc.queue.loop = False
                vc.queue.loop = False
                await ctx.send(f'**`{ctx.author.name}`**: Loop status: **DESATIVADO**')
        else:
            if not vc.queue.loop and not vc.queue.loop_all:
                vc.queue.loop = True
                vc.queue.loop_all = False
                await ctx.send(f'**`{ctx.author.name}`**: Definiu o loop para: **SONG**')
            elif vc.queue.loop and not vc.queue.loop_all:
                vc.queue.loop = False
                vc.queue.loop_all = True
                await ctx.send(f'**`{ctx.author.name}`**: Definiu o loop para: **QUEUE**')
            elif vc.queue.loop_all and not vc.queue.loop:
                vc.queue.loop = False
                vc.queue.loop = False
                await ctx.send(f'**`{ctx.author.name}`**: Loop status: **DESATIVADO**')
        CACHED_BOT_DICT[ctx.guild.id]["DeleteOLD"] = True
    
    @commands.command(aliases=['now_playing', 'np'])
    async def nowplaying(self, ctx: commands.Context):
        """Show the current song."""
        # Criando uma variavel para gerenciar o player do bot.
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        if vc.current:
            embed = discord.Embed(color=discord.Color.green())
            if not vc.current.is_stream:
                current_time = str(timedelta(seconds=int(vc.position/1000)))
                total_time = str(timedelta(seconds=int(vc.current.duration/1000)))
                embed.title = f'Now Playing: **`{current_time} of {total_time}`**'
            else:
                embed.title = f'Now Playing:'
            embed.description = f'[{vc.current.title}]({vc.current.uri})'
            message = await ctx.send(embed=embed)
    
            CACHED_BOT_DICT[ctx.guild.id]["DeleteOLD"] = True
            CACHED_BOT_DICT[ctx.guild.id]["LastCTX"] = ctx
            CACHED_BOT_DICT[ctx.guild.id]["LastNPMessage"] = message
            CACHED_BOT_DICT[ctx.guild.id]["Player"] = vc

    
async def setup(bot: commands.Bot):
    await bot.add_cog(Player(bot))
