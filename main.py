from typing import Final
from pathlib import Path

import logging
import discord
import aiosqlite
import asyncio

from private.config import token, test_guild_id
from modules.client import BussyClient
import modules.intents
from movelist_model import Database



# loop = asyncio.get_event_loop()
cwd: Path = Path.absolute(Path.cwd())
db_path: Path = Path.joinpath(cwd, 'example.db')
test_guild: Final = discord.Object(id=test_guild_id)
intents = modules.intents.personalized()

database = Database(db_path)
client = BussyClient(intents, test_guild)
log_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')


if __name__ == "__main__":
    client.run(token, log_handler=log_handler, reconnect=True)
    # asyncio.run(database.create_tables())