import json
from typing import TYPE_CHECKING, Final

import discord

import modules.intents
from modules.client import BussyClient
from modules.json_types import Secrets
from modules.paths import secrets_path
from modules.utils.logging_utils import setup_logging

with secrets_path.open(encoding="utf8") as file:
    secrets: Secrets = json.load(file)

token = secrets.get("token")
test_guild_id = secrets["test_guild_ids"].get("nexus")

if TYPE_CHECKING:
    assert test_guild_id is not None


setup_logging()

test_guild: Final = discord.Object(id=test_guild_id)
intents = modules.intents.personalized()

client = BussyClient(intents, test_guild)


def main() -> None:
    client.run(token, log_handler=None, reconnect=True)


if __name__ == "__main__":
    main()
