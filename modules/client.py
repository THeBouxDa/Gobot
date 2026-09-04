from typing import Final, Literal

import discord
import logging
from discord.ext import commands
import aiosqlite

from modules.commands import CommandsCog
# from modules.tree_error_handler import on_tree_error
from modules.database import Database

from configs.config import processed_dir

logger = logging.getLogger(__name__)


class BussyClient(commands.Bot):
    def __init__(self, intents, guild):
        super().__init__(command_prefix='!', intents=intents)
        self.test_guild = guild
        # self.tree.on_error = on_tree_error
        self.db = Database(processed_dir / "test.db")


    async def on_ready(self):
        logger.success(f'Logged on as {str(self.user).split('#')[0]}!') # type: ignore


    async def on_disconnect(self):
        logger.warning(f"Disconnected from Discord.")


    async def setup_hook(self) -> None:
        cog = CommandsCog(self.db)
        await self.add_cog(cog)
        
        
        self.tree.copy_global_to(guild=self.test_guild)
        await self.tree.sync()
        # await self.tree.sync(guild=self.test_guild)
        
        # TODO: Create game activity system.
        # await self.change_presence(activity=discord.Game(name="Goblin Sushi"))