from random import shuffle

import discord
import wavelink
from discord.ext import commands
from wavelink.ext import spotify
from wavelink.ext.spotify import SpotifySearchType

from utils import (NowPlayingEmbed, NowPlayingManager, Play, database_manager,
                   get_nowplaying_manager, get_wavelink_player)


class Player(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.command(aliases=["p", "pnext", "playnext"])
    async def play(self, ctx: commands.Context, *, search: str) -> None:
        """
        Play command.

        Accepts YouTube, Spotify, SoundCloud, Twitch, and others (Remote Stream)...

        Parameters:
        - search (str): The search term or link of the song to play.

        Example usage:
        !play Despacito
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
                await vc.play(vc.queue.get(), volume=database_manager.get_values(ctx.guild.id, "volume")["volume"], populate=bool(database_manager.get_values(ctx.guild.id, "auto_queue")["auto_queue"]))
        
        auto_shuffle = database_manager.get_values(int(ctx.guild.id), 'auto_shuffle')["auto_shuffle"]
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        
        IsSpotifyTrack = spotify.decode_url(search)
        
        if IsSpotifyTrack:
            if IsSpotifyTrack.type is  SpotifySearchType.playlist:
                track: spotify.SpotifyTrack = await GetAllSpotify_Songs(spotify.SpotifyTrack.iterator(query=search))
            else:
                track: spotify.SpotifyTrack = await spotify.SpotifyTrack.search(query=search)
        else:
            track: wavelink.YouTubeTrack = await wavelink.YouTubeTrack.search(search)
        
        play = Play(track, ctx)
        
        embed = await play.embed
        track = play.track
        
        if ctx.message.embeds:
            await ctx.message.delete()
        else:
            await ctx.message.delete()
            
        await ctx.send(embed=embed)
        
        await play_track(track)
        
    
    @commands.command(aliases=['dc', 'stop'])
    async def disconnect(self, ctx: commands.Context) -> None:
        """
        Disconnect/Stop player command.

        Parameters:

        Example usage:
        !disconnect
        """
        if not ctx.voice_client:
            # We can't disconnect, if we're not connected.
            await ctx.send('Not connected currently.')
        else:            
            vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
            
            vc.queue.reset()
            guild_id = int(ctx.guild.id)
            np_manager: NowPlayingManager = get_nowplaying_manager(self, guild_id)
            last_np_message = np_manager.last_np_message
            if last_np_message:
                try:
                    await last_np_message.delete()
                except discord.NotFound:
                    pass
                last_np_message: discord.Message = None
            np_manager.reset_all()
            await vc.disconnect()
            await ctx.send('*⃣ | Disconnected.')
    
    @commands.command(aliases=['retomar'])
    async def resume(self, ctx: commands.Context):
        """
        Resume the current song.

        Parameters:

        Example usage:
        !resume
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
    
    @commands.command(aliases=['pausar'])
    async def pause(self, ctx: commands.Context):
        """
        Pause the current song.

        Parameters:

        Example usage:
        !pause
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
    
    @commands.command()
    async def seek(self, ctx: commands.Context, *, seconds: int):
        """
        Jump to a specific time in the current track.

        Parameters:
        - seconds (int): The time in seconds to jump to in the current track.

        Example usage:
        !seek 60
        """
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
    
    @commands.command(aliases=['vol', 'volume', 'changevolume'])
    async def change_volume(self, ctx: commands.Context, *, vol: float = None):
        """
        Change the player volume.

        Parameters:
        - vol (float, int ,optional): The desired volume in percentage (1 to 1000).

        Example usage:
        !change_volume 50
        """
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        if not vol:
            await ctx.send(f'**`Current volume:`** **{vc.volume}%**')
        elif not 0 < vol < 1001:
            await ctx.send('Invalid Volume arguments, the volume needs to be between 1 and 1000.')
        elif not isinstance(vol, (float, int)):
            await ctx.send('Invalid Volume arguments, the volume needs to be and Integer.')
        else:
            await vc.set_volume(vol)
            database_manager.update_values(int(ctx.guild.id), volume=vol)
            await ctx.send(f'**`{ctx.author.name}`**: Definiu o volume para **{vol}%**')
    
    @commands.command(aliases=["pularpara", "skipto"])
    async def skip_to(self, ctx: commands.Context, *, index: int):
        """
        Skip to a specific song in the queue.

        Parameters:
        - index (int): The index of the song in the queue to skip to.

        Example usage:
        !skip_to 3
        """
        index = int(index)
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
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
    
    @commands.command(aliases=["pular"])
    async def skip(self, ctx: commands.Context):
        """
        Skip the current song.

        Parameters:

        Example usage:
        !skip
        """
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        if not vc.queue.is_empty or vc.current:
            auto_queue = bool(database_manager.get_values(int(vc.guild.id), "auto_queue")["auto_queue"])
            await ctx.send(f'**`{ctx.author.name}`**: Skipped **{vc.current.title}**.')
            if vc.queue.is_empty:
                if auto_queue:
                    await vc.stop()
                else:
                    ctx.command.ignore_execution = True
                    await ctx.invoke(self.bot.get_command("disconnect"))
            else:
                await vc.stop()
        else:
            await ctx.send("**`Queue is empty!`**")
    
    # Temporariamente desativado.
    # TODO: Verificar o por que não funciona.
    # @commands.command(aliases=["loop_all", "loop_song", "loopall", "loopsong"])
    # async def loop(self, ctx: commands.Context, *, loop: str =None):
    #     """
    #     Set the loop mode.

    #     Parameters:
    #     - loop (str, optional): The desired loop mode (all, single, or off).

    #     Example usage:
    #     !loop all
    #     """
    #     vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
    #     if loop:
    #         loop = loop.lower().strip()
    #         if loop in ["all", "queue"]:
    #             vc.queue.loop = False
    #             vc.queue.loop_all = True
    #             await ctx.send(f'**`{ctx.author.name}`**: Definiu o loop para: **QUEUE**')
    #         elif loop == ["single", "song"]:
    #             vc.queue.loop_all = False
    #             vc.queue.loop = True
    #             await ctx.send(f'**`{ctx.author.name}`**: Definiu o loop para: **SONG**')
    #         elif loop == ["off", "disable", "disabled"]:
    #             vc.queue.loop = False
    #             vc.queue.loop = False
    #             await ctx.send(f'**`{ctx.author.name}`**: Loop status: **DESATIVADO**')
    #     else:
    #         if not vc.queue.loop and not vc.queue.loop_all:
    #             vc.queue.loop = True
    #             vc.queue.loop_all = False
    #             await ctx.send(f'**`{ctx.author.name}`**: Definiu o loop para: **SONG**')
    #         elif vc.queue.loop and not vc.queue.loop_all:
    #             vc.queue.loop = False
    #             vc.queue.loop_all = True
    #             await ctx.send(f'**`{ctx.author.name}`**: Definiu o loop para: **QUEUE**')
    #         elif vc.queue.loop_all and not vc.queue.loop:
    #             vc.queue.loop = False
    #             vc.queue.loop = False
    #             await ctx.send(f'**`{ctx.author.name}`**: Loop status: **DESATIVADO**')
    
    @commands.command(aliases=['now_playing', 'np'])
    async def nowplaying(self, ctx: commands.Context):
        """
        Show the current song.

        Parameters:

        Example usage:
        !nowplaying
        """
        # Criando uma variavel para gerenciar o player do bot.
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        if vc.current:
            embed = NowPlayingEmbed(vc, None)
            np_manager: NowPlayingManager = get_nowplaying_manager(self, ctx.guild.id)
            message = await ctx.send(embed=embed)
            np_manager.last_np_message = message
    
async def setup(bot: commands.Bot):
    await bot.add_cog(Player(bot))
