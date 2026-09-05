import discord
from discord import Intents
from discord.ext import commands

from modules.commands import CommandsCog
from modules.database import Database
from modules.paths import data_dir
from modules.utils.logging_utils import get_logger

logger = get_logger(__name__)


class BussyClient(commands.Bot):
    def __init__(self, intents: Intents, test_guild: discord.Object) -> None:
        super().__init__(command_prefix="!", intents=intents)
        self.test_guild = test_guild
        # self.tree.on_error = on_tree_error

    async def on_ready(self) -> None:
        logger.success(f"Logged on as {str(self.user).split('#')[0]}!")

    async def on_disconnect(self) -> None:
        logger.warning("Disconnected from Discord.")

    async def setup_hook(self) -> None:
        self.db = Database(data_dir / "test.db")

        cog = CommandsCog(self)
        await self.add_cog(cog)

        self.tree.copy_global_to(guild=self.test_guild)
        await self.tree.sync()
        # await self.tree.sync(guild=self.test_guild)

        # TODO: Create game activity system.
        # await self.change_presence(activity=discord.Game(name="Goblin Sushi"))
