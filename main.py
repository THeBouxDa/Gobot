from typing import Final

import logging
import discord

from private.config import token, test_guild_id
from modules.client import BussyClient
import modules.intents



test_guild: Final = discord.Object(id=test_guild_id)
intents = modules.intents.personalized()
client = BussyClient(intents, test_guild)

log_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')


if __name__ == "__main__":
    client.run(token, log_handler=log_handler)