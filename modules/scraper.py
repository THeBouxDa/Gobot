import asyncio
import json
import re

from bs4 import BeautifulSoup

from modules.character import Character
from modules.database import Database
from modules.json_types import Parser, ScraperSettings
from modules.move import Move
from modules.paths import (
    characters_dir,
    data_dir,
    homepage_path,
    parsing_config,
    scraping_config,
)
from modules.utils import parsing_utils as parser
from modules.utils.aio_utils import (
    fetch_batch,
    fetch_data,
    load_batch,
    load_data,
    store_data,
)
from modules.utils.logging_utils import get_logger, setup_logging

logger = get_logger(__name__)

with scraping_config.open(encoding="utf8") as file:
    scraping: ScraperSettings = json.load(file)

with parsing_config.open(encoding="utf8") as file:
    parsing: Parser = json.load(file)

group_pattern = parsing["raw_group_pattern"]
property_pattern = parsing["raw_property_pattern"]
section_pattern = parsing["raw_section_pattern"]


def select_characters(homepage: str) -> list[Character]:
    soup = BeautifulSoup(homepage, "html.parser")
    container_rows = soup.select(".home-card > div.add-hover-effect")

    links = []
    characters: list[Character] = []
    for row in container_rows:
        row_links = row.find_all("a")
        links.extend(row_links)

    for link in links:
        name = str(link.attrs["title"])
        safe_name = parser.sanitize(name)
        url = f"{scraping['domain_url']}{link.attrs['href']!s}"
        data_url = scraping["character_data_url"].format(character=safe_name)
        data_path = characters_dir / f"{safe_name}.html"

        characters.append(
            Character(
                name=name,
                safe_name=safe_name,
                page_url=url,
                data_url=data_url,
                data_path=data_path,
            )
        )

        logger.debug("Character [%s] found", name)

    return characters


def select_moves(file: str, char_name: str) -> list[Move]:
    moves: list[Move] = []
    soup = BeautifulSoup(file, "html.parser")
    raw = soup.select_one("textarea#wpTextbox1")

    if raw is None or raw.string is None:
        msg = f"Raw for {char_name} is broken!"
        raise TypeError(msg)

    raw = raw.string
    raw = raw.split("==Normal Moves==")[1].splitlines()

    category: str = ""
    section: str = "Normal Moves"
    data: dict[str, str] = {}
    for line in raw:
        # ignore moves in ignored section
        match = re.search(section_pattern, line)
        if match is not None:
            section = match.group(1)
            if section in parsing["ignored_sections"]:
                continue

        # store the group upon encountering a new one
        match = re.search(group_pattern, line)
        if match is not None:
            category = match.group(1)

        # Upon meeting this, start collecting into dict
        if line == "{{MoveData-GGST":
            data = {"category": category, "section": section}

        match = re.search(property_pattern, line)
        if match is not None:
            prop, val = (x.strip() for x in line.lstrip("|").split("=", 1))
            val = parser.line_breaker(val)

            if prop == "input":
                val = parser.input_parser(val)
            elif prop in {"images", "hitboxes"}:
                val = parser.file_parser(val)

            data[prop] = val
            data["char_name"] = char_name

            for key in parsing["db_bound_keys"]:
                if data.get(key) is None:
                    data[key] = ""

        if line == "}}":
            moves.append(Move(data))

    return moves


async def build_characters() -> list[Character]:
    """
    There's a bit of repetition, in the case of a scrape
    we store files just to load them again from storage...
    ultimately I cannot be asked to address such a minor
    concern, given the non-blocking nature of these IO operations,
    the small quantity of files, and the infrequent use of the scraper
    (file count will never exceed character count in the game)
    """

    homepage: str = await load_data(homepage_path)
    characters: list[Character] = select_characters(homepage)

    char_paths = [char.data_path for char in characters]

    # as files are read, process the moves
    async for index, file in load_batch(char_paths):
        char = characters[index]

        valid_moves = filter(parser.move_filter, select_moves(file, char.name))
        logger.debug("Moves found for: [%s]", char.name)
        char.set_moves(list(valid_moves))

    return characters


async def fetch_all_and_store() -> None:
    homepage: str = await fetch_data(scraping["homepage_url"])
    characters: list[Character] = select_characters(homepage)
    urls = [char.data_url for char in characters]

    # tasks: list[asyncio.Task[None]] = []
    tasks: list[asyncio._CoroutineLike] = []
    async for index, doc in fetch_batch(urls, delay=1):
        char = characters[index]
        tasks.append(store_data(char.data_path, doc))

    await asyncio.gather(*tasks)


# code to run if starting as script or rebuilding
async def launch(db: Database, *, scrape: bool) -> None:
    """
    Launches an update for the database.
    if parameter scrape is False, it will rebuild from locally stored data,
    else it will request files from dustloop
    """

    async def load_and_pair(char: Character, index: int) -> int:
        await db.insert_character(char)
        return index

    if scrape:
        await fetch_all_and_store()

    task = asyncio.create_task(build_characters())
    await db.clear_tables()
    await db.create_tables()
    characters = await task

    await db.insert_characters(characters)

    async with asyncio.TaskGroup() as group:
        for char in characters:
            group.create_task(db.insert_moves(char.moves))


if __name__ == "__main__":
    setup_logging()
    db = Database(data_dir / "test.db")
    asyncio.run(launch(db, scrape=False))
