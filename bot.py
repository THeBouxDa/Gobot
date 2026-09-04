from typing import Final
from pathlib import Path

from logging.handlers import QueueHandler
import discord
import aiosqlite
import asyncio

from private.config import token, test_guild_id
from modules.client import BussyClient
import modules.intents
from modules.database import Database
from modules.utils.logging_util import setup_logging


setup_logging()

cwd: Path = Path.absolute(Path.cwd())
db_path: Path = Path.joinpath(cwd, 'data', 'processed', "test.db")
test_guild: Final = discord.Object(id=test_guild_id)
intents = modules.intents.personalized()

database = Database(db_path)
client = BussyClient(intents, test_guild)



if __name__ == "__main__":
    client.run(token, log_handler=None, reconnect=True)

    
    
    pass