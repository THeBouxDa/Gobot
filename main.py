from typing import TYPE_CHECKING, Final

import discord

import modules.intents
from modules.bot import BussyBot
from modules.resources.configs import secrets_config as secrets
from modules.utils.logging_utils import setup_logging

token = secrets["token"]
test_guild_id = secrets["test_guild_ids"].get("stream")

if TYPE_CHECKING:
    assert test_guild_id is not None


setup_logging()

test_guild: Final = discord.Object(id=test_guild_id)
intents = modules.intents.personalized()

client = BussyBot(intents, test_guild)


def main() -> None:
    client.run(token, log_handler=None, reconnect=True)


if __name__ == "__main__":
    main()
