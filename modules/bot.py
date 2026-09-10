import random
from typing import TYPE_CHECKING

import discord
from discord import Intents
from discord.ext import commands, tasks
from sqlalchemy.ext.asyncio import create_async_engine

# from sqlalchemy.pool import
from modules.cogs import DustloopCog, MiscCog
from modules.database import ConnectionManager
from modules.resources.configs import commands_config
from modules.resources.paths import database_path
from modules.utils.logging_utils import get_logger

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio.engine import AsyncEngine


logger = get_logger(__name__)


class BussyBot(commands.Bot):
    def __init__(self, intents: Intents, test_guild: discord.Object | None) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents,
            activity=self.get_random_activity(),
        )
        self.test_guild = test_guild

    async def on_ready(self) -> None:
        logger.success(f"Logged on as {str(self.user).split('#')[0]}!")

    async def on_disconnect(self) -> None:
        logger.warning("Disconnected from Discord.")

    async def setup_hook(self) -> None:
        db_url = f"sqlite+aiosqlite:///{database_path}"
        engine: AsyncEngine = create_async_engine(
            db_url,
            pool_size=10,
            max_overflow=10,
            pool_timeout=60,
            pool_recycle=7200,
            connect_args={"check_same_thread": False},
        )

        self.db = ConnectionManager(engine)

        await self.add_cog(MiscCog(self))
        await self.add_cog(DustloopCog(self))

        if self.test_guild:
            self.tree.copy_global_to(guild=self.test_guild)

        await self.tree.sync()
        self.set_random_activity_loop.start()

    @tasks.loop(hours=1)
    async def set_random_activity_loop(self) -> None:
        if self.is_ready():
            await self.change_presence(activity=self.get_random_activity())

    @set_random_activity_loop.before_loop
    async def wait_for_cache(self) -> None:
        await self.wait_until_ready()

    def get_random_activity(self) -> discord.BaseActivity:
        choice = random.choice(commands_config["game_activities"])
        title, url = next(iter(choice.items()))

        return discord.Activity(
            name=title,
            type=discord.ActivityType.playing,
            buttons=[{"label": "Play on Steam", "url": url}],
            platform="Steam",
        )
