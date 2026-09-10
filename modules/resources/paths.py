from pathlib import Path

root = Path.cwd()
private_dir = root / "private"
data_dir = root / "data"
logs_dir = root / "logs"
config_dir = root / "configs"
raw_dir = data_dir / "raw"
characters_dir = raw_dir / "characters"
database_path = data_dir / "test.db"
homepage_path = raw_dir / "homepage.html"
secrets_config_path = private_dir / "secrets.json"
logging_config_path = config_dir / "logging.json"
parsing_config_path = config_dir / "parsing.json"
rps_config_path = config_dir / "rps.json"
scraping_config_path = config_dir / "scraping.json"
commands_config_path = config_dir / "commands.json"
