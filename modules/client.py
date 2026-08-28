from typing import Final, Literal

import discord
from discord.ext import commands
import aiosqlite

from modules.commands import CommandsCog
from modules.tree_error_handler import on_tree_error



class BussyClient(commands.Bot):
    def __init__(self, intents, guild):
        super().__init__(command_prefix='!', intents=intents)
        self.test_guild = guild
        self.tree.on_error = on_tree_error


    async def on_ready(self):
        print(f'Logged on as {str(self.user).split('#')[0]}!')


    async def on_disconnect(self):
        print(f"Disconnected from Discord.")


    # TODO: Delete this by the end
    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')


    async def setup_hook(self) -> None:
        cog = CommandsCog(self)
        await self.add_cog(cog)
        
        
        self.tree.copy_global_to(guild=self.test_guild)
        await self.tree.sync(guild=self.test_guild)
        
        # TODO: Create game activity system.
        # await self.change_presence(activity=discord.Game(name="Goblin Sushi"))