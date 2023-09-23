import logging

import discord
from discord.ext import commands

from utils import database_manager


class BasicCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        logging.info(f'Logged in {self.bot.user} | {self.bot.user.id}')
        await self.bot.change_presence(
                                    activity=discord.Game(name="Mention me to see the server prefix."),
                                    status=discord.Status.online
                                )
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if self.bot.user.mentioned_in(message) and len(message.mentions) == 1 and message.content.strip() == message.mentions[0].mention:
            prefix = self.bot.command_prefix(bot=self.bot, message=message)
            await message.reply(f"""BOT Prefix: **`{prefix}`**\nTo change the prefix, you can use: **`{prefix}changeprefix new_prefix`** (It must be a server admin)""")
    
    @commands.Cog.listener()
    async def on_guild_join(guild):  # when the bot joins the guild
        # generate_configs(str(guild.id))
        pass
    
    @commands.Cog.listener()
    async def on_guild_remove(guild):  # when the bot is removed from the guild
        # delete_server(guild)
        pass
    
    @commands.command(aliases=['change_prefix'])
    @commands.has_permissions(administrator=True)  # ensure that only administrators can use this command
    async def changeprefix(self, ctx: commands.Context, prefix: str):  # command: c>changeprefix ...
        """
        Change Bot prefix.
        """
        database_manager.update_values(int(ctx.guild.id), prefix=str(prefix))
        await ctx.send(f'New prefix is now: **{prefix}**')

async def setup(bot: commands.Bot):
    await bot.add_cog(BasicCommands(bot))
