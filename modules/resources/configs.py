import json
from typing import TYPE_CHECKING

from modules.resources import paths

if TYPE_CHECKING:
    from modules import config_types


with paths.commands_config_path.open(encoding="utf8") as file:
    commands_config: config_types.CommandConfig = json.load(file)

with paths.logging_config_path.open(encoding="utf8") as file:
    logging_config = json.load(file)

with paths.parsing_config_path.open(encoding="utf8") as file:
    parsing_config: config_types.ParserConfig = json.load(file)

with paths.rps_config_path.open(encoding="utf8") as file:
    rps_config: config_types.RPSConfig = json.load(file)

with paths.scraping_config_path.open(encoding="utf8") as file:
    scraping_config: config_types.ScraperConfig = json.load(file)

with paths.secrets_config_path.open(encoding="utf8") as file:
    secrets_config: config_types.SecretsConfig = json.load(file)
