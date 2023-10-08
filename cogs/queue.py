import asyncio

import discord
import wavelink
from discord.ext import commands

from utils import (NowPlayingManager, database_manager, get_nowplaying_manager,
                   get_wavelink_player)


class Queue(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.command()
    async def clear(self, ctx: commands.Context):
        """
        Clears the current queue list.

        Parameters:

        Example usage:
        !clear
        """
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        queue = vc.queue
        if queue.is_empty:
            await ctx.send("**`Queue is empty!`**")
        else:
            queue.clear()
            await ctx.send(f'**`{ctx.author.name}`**: Cleared the Queue!')
    
    @commands.command(aliases=["clearhistory"])
    async def clear_history(self, ctx: commands.Context):
        """
        Clears the current queue history.

        Parameters:

        Example usage:
        !clearhistory
        """
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        vc.queue.history.clear()
        await ctx.send("**`Queue history cleared!`**")
    
    @commands.command(aliases=["queuereset"])
    async def queue_reset(self, ctx: commands.Context):
        """
        Resets the queue completely, clearing all queue and remaining configs.

        Parameters:

        Example usage:
        !queuereset
        """
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        vc.queue.reset()
        await ctx.send("**`Queue history cleared!`**")
    
    @commands.command(aliases=['misturar'])
    async def shuffle(self, ctx: commands.Context):
        """
        Randomizes the current queue.

        Parameters:

        Example usage:
        !shuffle
        """
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        queue = vc.queue
        if queue.is_empty:
            await ctx.send("**`Queue is empty!`**")
        else:
            # Randomizando a fila de músicas no player.
            queue.shuffle()
            await ctx.send(f'**`{ctx.author.name}`**: Shuffled all the songs!')
    
    @commands.command(aliases=['autoqueue'])
    async def auto_queue(self, ctx: commands.Context):
        """
        Sets if the queue will be populated with similar songs based on YouTube or Spotify recommendations.

        Parameters:

        Example usage:
        !autoqueue
        """
        current_autoqueue = database_manager.get_values(int(ctx.guild.id), 'auto_queue')["auto_queue"]
        database_manager.update_values(int(ctx.guild.id), auto_queue=not current_autoqueue)
        await ctx.send(f'The Auto Queue is now set to **{not current_autoqueue}**')
    
    @commands.command(aliases=['movetrack', 'move'])
    async def move_track(self, ctx: commands.Context, pos1: int, pos2: int):
        """
        Moves a track to a specific position in the queue.

        Parameters:
        - pos1 (int): The current position of the track.
        - pos2 (int): The target position to move the track to.

        Example usage:
        !move 3 1
        """
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        queue = vc.queue
        if pos1 <= 0 or pos2 <= 0:
            await ctx.send('Invalid Move Track arguments, the position number needs to be bigger than 0.')
        elif pos1 - 1 > queue.count or pos2 > queue.count:
            await ctx.send('Invalid Move Track arguments, the position number can\'t be bigger than queue lenght.')
        elif pos1 == pos2:
            await ctx.send('Invalid Move Track arguments, the positions numbers can\'t be the same.')
        else:
            track = queue._queue[pos1 - 1]
            await ctx.send(f'**`{ctx.author.name}`**: Moved **{track.title}** to **{pos2}st** in Queue.')
            del queue._queue[pos1-1]
            queue._queue.insert(pos2 - 1, track)
    
    @commands.command(aliases=['auto_shuffle', 'toggleshuffle', 'toggle_autoshuffle'])
    async def autoshuffle(self, ctx: commands.Context):
        """
        Sets if playlists will be shuffled before being added to the queue.

        Parameters:

        Example usage:
        !autoshuffle
        """
        current_autoshuffle = database_manager.get_values(int(ctx.guild.id), 'auto_shuffle')["auto_shuffle"]
        database_manager.update_values(int(ctx.guild.id), auto_shuffle=not current_autoshuffle)
        await ctx.send(f'The Auto Shuffle is now set to **{not current_autoshuffle}**')
    
    @commands.command(aliases=["remover", "remove"])
    async def remove_track(self, ctx: commands.Context, *, pos: int):
        """
        Removes a specific track in the queue by specifying its position.

        Parameters:
        - pos (int): The position of the track to be removed.

        Example usage:
        !remove 2
        """
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        if int(pos) - 1 >= vc.queue.count or int(pos) <= 0:
            await ctx.send('Invalid Remove Track arguments, the position number needs to be an valid song.')
        else:
            index = int(pos)-1
            await ctx.send(f'**`{ctx.author.name}`**: Removed **{vc.queue._queue[index].title}** from the Queue.')
            del vc.queue._queue[index]
    
    @commands.command(aliases=['q'])
    async def queue(self, ctx: commands.Context):
        """
        Shows the current queued songs.

        Parameters:

        Example usage:
        !queue
        """
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        queue = vc.queue
        if queue.is_empty:
            await ctx.send("**`Queue is empty!`**")
            np_manager: NowPlayingManager = get_nowplaying_manager(self, ctx.guild.id)
            await np_manager.update_nowplaying(ctx)
        else:
            # Verificando a quantidade real de músicas na fila.
            num_songs_in_queue = len(queue)
            
            # Definindo a quantidade de músicas a serem mostradas (máximo 10).
            next_songs = min(num_songs_in_queue, 10)
            
            # Enviando a fila de músicas no chat.
            embed = discord.Embed(color=discord.Color.gold())
            embed.title = f'**1 to {next_songs} OF {num_songs_in_queue} Tracks**'
            song_list = list(queue)[:next_songs]
            embed.description = '\n'.join(f'{song_list.index(name) + 1} - **{name}**' for name in song_list)
            queue_msg = await ctx.send(embed=embed)
            np_manager: NowPlayingManager = get_nowplaying_manager(self, ctx.guild.id)
            await np_manager.update_nowplaying(ctx)
            
            if num_songs_in_queue > next_songs:
                buttons = [u"\u23EA", u"\u2B05", u"\u27A1", u"\u23E9"]
                for button in buttons:
                    await queue_msg.add_reaction(button)
                current = 0

                while True:
                    queue = vc.queue
                    try:
                        reaction, user = await self.bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in buttons, timeout=60.0)
                    except asyncio.TimeoutError:
                        await queue_msg.clear_reactions()
                        break
                    else:
                        previous_page = current
                        if reaction.emoji == u"\u23EA":
                            current = 0

                        elif reaction.emoji == u"\u2B05":
                            if current > 0:
                                current -= next_songs

                        elif reaction.emoji == u"\u27A1":
                            if current + next_songs < num_songs_in_queue:
                                current += next_songs

                        elif reaction.emoji == u"\u23E9":
                            if num_songs_in_queue > next_songs:
                                current = str(num_songs_in_queue)
                                if int(current[-1]) == 0:
                                    current = int(f"{int(current[:-1])-1}0")
                                else:
                                    current = int(f"{int(current[:-1])}0")
                        await queue_msg.remove_reaction(reaction.emoji, ctx.author)
                        if current != previous_page:
                            if current + next_songs > num_songs_in_queue:
                                embed.title = f'**{current+1} to {num_songs_in_queue} OF {num_songs_in_queue} Tracks**'
                            else:
                                embed.title = f'**{current+1} to {current+next_songs} OF {num_songs_in_queue} Tracks**'
                            song_list = list(queue)[current: current + next_songs]
                            embed.description = '\n'.join(f'{list(queue).index(name) + 1} - **{name}**' for name in song_list)
                            await queue_msg.edit(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Queue(bot))
