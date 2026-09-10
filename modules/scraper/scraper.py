import asyncio
import re
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup

from modules.resources.configs import parsing_config, scraping_config
from modules.resources.paths import (
    characters_dir,
    homepage_path,
)
from modules.scraper.character import Character
from modules.scraper.move import Move
from modules.utils import parsing_utils as parser
from modules.utils.aio_utils import (
    fetch_batch,
    fetch_data,
    load_batch,
    load_data,
    store_data,
)
from modules.utils.logging_utils import get_logger

if TYPE_CHECKING:
    from modules.database import ConnectionManager

logger = get_logger(__name__)


group_pattern = parsing_config["raw_group_pattern"]
property_pattern = parsing_config["raw_property_pattern"]
section_pattern = parsing_config["raw_section_pattern"]


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
        url = f"{scraping_config['domain_url']}{link.attrs['href']!s}"
        data_url = scraping_config["character_data_url_template"].format(safe_name)
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


def select_moves(file: str, char_name: str) -> list[Move]:  # noqa: C901
    moves: list[Move] = []
    soup = BeautifulSoup(file, "html.parser")
    raw = soup.select_one("textarea#wpTextbox1")

    if raw is None or raw.string is None:
        msg = f"Raw for {char_name} is broken!"
        raise TypeError(msg)

    # Remove all comments, ensure all pipes are on a newline, and start from normal moves
    raw = raw.string
    raw = re.sub(r"<!--.*?-->", "", raw, flags=re.DOTALL)
    raw = re.sub(f"(?<!\n){re.escape('|')}", f"\n{'|'}", raw)
    raw = raw.split("==Normal Moves==")[1].splitlines()

    category: str = ""
    section: str = "Normal Moves"
    data: dict[str, str] = {}
    for line in raw:
        # ignore moves in ignored section

        match = re.search(section_pattern, line)
        if match is not None:
            section = match.group(1)
            if section in parsing_config["ignored_sections"]:
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

            for key in parsing_config["db_bound_keys"]:
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
    homepage: str = await fetch_data(scraping_config["homepage_url"])
    characters: list[Character] = select_characters(homepage)
    urls = [char.data_url for char in characters]

    # tasks: list[asyncio.Task[None]] = []
    tasks: list[asyncio.Task] = [
        asyncio.create_task(store_data(homepage_path, homepage))
    ]
    async for index, doc in fetch_batch(urls, delay=1):
        char = characters[index]
        tasks.append(asyncio.create_task(store_data(char.data_path, doc)))

    await asyncio.gather(*tasks)


# code to run if starting as script or rebuilding
async def launch(db: ConnectionManager, *, scrape: bool) -> None:
    """
    Launches an update for the database.

    If parameter scrape is False, it will rebuild from locally stored data,
    else it will request files from dustloop
    """

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

    logger.checkpoint("All characters' moves inserted successfully.")


if __name__ == "__main__":
    from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

    from modules.database import ConnectionManager
    from modules.resources.paths import database_path
    from modules.utils.logging_utils import get_logger, setup_logging

    setup_logging()

    db_url = f"sqlite+aiosqlite:///{database_path}"
    engine: AsyncEngine = create_async_engine(
        db_url,
        pool_size=10,
        max_overflow=10,
        pool_timeout=60,
        pool_recycle=7200,
        connect_args={"check_same_thread": False},
    )

    db = ConnectionManager(engine)
    asyncio.run(launch(db, scrape=False))
