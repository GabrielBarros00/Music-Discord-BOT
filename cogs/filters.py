import wavelink
from discord.ext import commands
from wavelink import (Equalizer, Filter, Karaoke, LowPass, Rotation, Timescale,
                      Vibrato)

from utils import get_wavelink_player


class Filters(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.command(aliases=['eq', 'bass'])
    async def equalizer(self, ctx: commands.Context, *, num: int | float):
        """
        Set Equalizer bass on Player.

        Parameters:
        - num (int | float): The bass level between 0 to 100.

        Example usage:
        !equalizer 50
        """
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        if not num >= 0 or not num <= 100:
            await ctx.send('**`Please, give a number between 0 to 100 in Equalizer command.`**')
        else:
            vc._filter.equalizer = Equalizer(name="BASS", bands=[(0, float(num / 100)), (1, float(num / 100)), (2, float(num / 100))])
            await vc.set_filter(vc._filter)
            await ctx.send('**`Equalizer modified!`**')
    
    @commands.command()
    async def karaoke(self, ctx: commands.Context):
        """
        Set Karaoke mode on Player.

        Parameters:

        Example usage:
        !karaoke
        """
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        if not vc._filter.karaoke:
            vc._filter.karaoke = Karaoke()
            await ctx.send('**`Karaoke enabled!`**')
        else:
            vc._filter.karaoke = None
            await ctx.send('**`Karaoke disabled!`**')
        await vc.set_filter(vc._filter)
    
    @commands.command()
    async def vibrato(self, ctx: commands.Context, *, num: int | float):
        """
        Set Vibrato on Player.

        Parameters:
        - num (int | float): The vibrato value between 0 to 140.

        Example usage:
        !vibrato 75
        """
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        if not num >= 0 or not num <= 140:
            await ctx.send('**`Please, give a number between 0 to 140 in Vibrato command.`**')
        else:
            vibrato_value = num/100
            vc._filter.vibrato = Vibrato(frequency=vibrato_value, depth=vibrato_value/14)
            await vc.set_filter(vc._filter)
            await ctx.send('**`Vibrato modified!`**')
    
    @commands.command()
    async def pitch(self, ctx: commands.Context, *, num: int | float):
        """
        Set Pitch on Player.

        Parameters:
        - num (int | float): The pitch value between 0 to 10 (Default: 1).

        Example usage:
        !pitch 2.5
        """
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        if not num >= 0 or not num <= 10:
            await ctx.send('**`Please, give a number between 0 to 10 in Pitch command. Eg: pitch 0.5 or pitch 3.2 | Default: 1`**')
        else:
            vc._filter.timescale = Timescale(pitch=num)
            await vc.set_filter(vc._filter)
            await ctx.send('**`Pitch modified!`**')
    
    @commands.command(aliases=["3d", "3dsound", "3d_sound"])
    async def rotation(self, ctx: commands.Context, *, num: int | float):
        """
        Set Rotation/3D Audio on Player.

        Parameters:
        - num (int | float): The rotation speed between 0 to 100.

        Example usage:
        !rotation 40
        """
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        if not num >= 0 or not num <= 100:
            await ctx.send('**`Please, give a number between 0 to 100 in Rotation command.`**')
        else:
            vc._filter.rotation = Rotation(speed=num/100)
            await vc.set_filter(vc._filter)
            await ctx.send('**`Rotation modified!`**')
    
    @commands.command(aliases=["low_pass", "lp"])
    async def lowpass(self, ctx: commands.Context, *, num: int | float):
        """
        Set LowPass on Player.

        Parameters:
        - num (int | float): The smoothing value between 0 to 100.

        Example usage:
        !lowpass 40
        """
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        if not num >= 0 or not num <= 100:
            await ctx.send('**`Please, give a number between 0 to 100 in LowPass command.`**')
        else:
            vc._filter.low_pass = LowPass(smoothing=num)
            await vc.set_filter(vc._filter)
            await ctx.send('**`LowPass modified!`**')
    
    @commands.command(aliases=["reset_filters"])
    async def resetfilters(self, ctx: commands.Context):
        """
        Reset all filters on Player.

        Parameters:
        - ctx (commands.Context): The command message context.

        Example usage:
        !resetfilters
        """
        vc: wavelink.Player = await get_wavelink_player(ctx=ctx)
        await vc.set_filter(Filter())
        await ctx.send('**`All filters reseted!`**')


async def setup(bot: commands.Bot):
    await bot.add_cog(Filters(bot))
