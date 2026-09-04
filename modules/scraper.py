import asyncio
import logging
import re
import time
from collections.abc import AsyncIterator, Iterable
from pathlib import Path
from typing import Final

import requests
import requests.exceptions as rex
from bs4 import BeautifulSoup

from configs.config import (
    characters_dir,
    db_bound_keys,
    excluded_moves,
    headers,
    homepage_path,
    ignored_sections,
    processed_dir,
    raw_group_pattern,
    raw_property_pattern,
    raw_section_pattern,
)
from modules.character import Character, Move
from modules.database import Database
from modules.utils.logging_util import setup_logging
from modules.utils.util import sanitize

setup_logging()

type HTML_Document = str

MAX_RETRIES: int = 3
domain_url: Final[str] = "https://dustloop.com"
homepage_url: Final[str] = f"{domain_url}/w/GGST"
image_url_prefix: Final[str] = f"{domain_url}/w/File:"
character_data_url: Final[str] = (
    f"{domain_url}/wiki/index.php?title=GGST/{{character}}&action=edit"
)

logger = logging.getLogger(__name__)


def move_filter(move: Move) -> bool:
    output: bool = True
    if move.get_prop("name") in excluded_moves:
        return False

    if move.get_prop("section") in ignored_sections:
        return False

    return output


def file_parser(url: str) -> str:
    return url.replace(" ", "_")


def tag_fixer(string: str) -> str:
    return string.replace("&lt;", "<").replace("&gt;", ">")


def line_breaker(string: str) -> str:
    string = tag_fixer(string)
    return string.replace("<br/>", "\n").replace("<br>", "\n")


def input_parser(input: str) -> str:
    result = input.upper()

    # Leo Whitefang requires this special exception
    if result == "[S/H] H/S":
        result = "[S]H;[H]S"
    elif (match := re.search(r"(\w(?:\/\w)+)", result)) is not None:
        pattern = match.group(1)
        replacements = pattern.split("/")
        result = ";".join([result.replace(pattern, r) for r in replacements])

    return result


def _fetch_data_sync(url: str) -> HTML_Document:

    for retries in range(MAX_RETRIES):
        if retries > 0:
            logger.warning("Failed request, retrying to fetch %s", url)
            time.sleep(2**retries)

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            logger.debug("Scraped %s", url)
            return response.text

        except rex.Timeout:
            logger.exception("Timeout error for page %s", url)

        except rex.ConnectionError:
            logger.exception("Connection dropped/refused for %s", url)

        except rex.HTTPError as e:
            if (
                e.response is None
                or 400 <= (status_code := e.response.status_code) < 500  # noqa: PLR2004
            ):
                logger.exception("Serious HTTP Error, aborting %s")
                raise rex.HTTPError(
                    "Something serious occurred while requesting, check logs!", url
                )
            elif 500 <= status_code < 600:
                logger.exception("Server Error %s for %s", status_code, url)

        except rex.RequestException as e:
            logger.exception("Unspecified network error for %s", url)

    # if we got to this point, the request failed more than MAX_RETRIES
    logger.error("Max number of retries exceeded, aborting requests for %s", url)
    raise rex.RequestException(
        "Something serious occurred while requesting, check logs!"
    )


def _store_data_sync(filepath: Path, data: str):
    filepath.write_text(data, encoding="utf8")
    logger.success("Stored page: %s", filepath)  # type: ignore


def _load_data_sync(path: Path) -> str:
    data = path.read_text(encoding="utf8")
    logger.debug("File was read: %s", str(path))

    return data


async def fetch_data(url: str, delay: float = 0) -> HTML_Document:
    await asyncio.sleep(delay)
    return await asyncio.to_thread(_fetch_data_sync, url)


async def store_data(filepath: Path, data: str):
    await asyncio.to_thread(_store_data_sync, filepath, data)


async def load_data(path: Path) -> str:
    return await asyncio.to_thread(_load_data_sync, path)


async def fetch_batch(
    urls: Iterable[str], delay: float
) -> AsyncIterator[tuple[int, HTML_Document]]:

    async def fetch_and_pair(url: str, delay: float, id: int) -> tuple[int, str]:
        mult = id + 1
        content = await fetch_data(url, delay * mult)
        return id, content

    tasks = [
        asyncio.create_task(fetch_and_pair(url, delay, id))
        for id, url in enumerate(urls)
    ]

    for completed_task in asyncio.as_completed(tasks):
        id, content = await completed_task
        yield id, content


async def store_batch(info: Iterable[tuple[Path, str]]) -> None:
    tasks = [store_data(*i) for i in info]
    await asyncio.gather(*tasks, return_exceptions=True)


async def load_batch(paths: Iterable[Path]) -> AsyncIterator[tuple[int, str]]:

    # wrapper function to return path paired with the contents
    async def load_and_pair(path: Path, id: int) -> tuple[int, str]:
        content = await load_data(path)
        return id, content

    # immediately start all the file reads
    tasks = [
        asyncio.create_task(load_and_pair(path, id)) for id, path in enumerate(paths)
    ]

    # yield results as soon as they complete
    for completed_task in asyncio.as_completed(tasks):
        id, content = await completed_task
        yield id, content


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
        safe_name = sanitize(name)
        url = f"{domain_url}{str(link.attrs['href'])}"
        data_url = character_data_url.format(character=safe_name)
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
        raise Exception

    raw = raw.string
    raw = raw.split("==Normal Moves==")[1].splitlines()

    category: str = ""
    section: str = "Normal Moves"
    data: dict[str, str] = {}
    for line in raw:
        # ignore moves in ignored section
        match = re.search(raw_section_pattern, line)
        if match is not None:
            section = match.group(1)
            if section in ignored_sections:
                continue

        # store the group upon encountering a new one
        match = re.search(raw_group_pattern, line)
        if match is not None:
            category = match.group(1)

        # Upon meeting this, start collecting into dict
        if line == "{{MoveData-GGST":
            data = {"category": category, "section": section}

        match = re.search(raw_property_pattern, line)
        if match is not None:
            prop, val = (x.strip() for x in line.lstrip("|").split("=", 1))
            val = line_breaker(val)

            if prop == "input":
                val = input_parser(val)
            elif prop == "images" or prop == "hitboxes":
                val = file_parser(val)

            data[prop] = val
            data["char_name"] = char_name

            for key in db_bound_keys:
                if data.get(key) is None:
                    data[key] = ""

        if line == "}}":
            moves.append(Move(data))

    return moves


async def build_characters() -> list[Character]:
    """There's a bit of repetition, in the case of a scrape
    we store files just to load them again from storage...
    ultimately I cannot be asked to address such a minor
    concern, given the non-blocking nature of these IO operations,
    the small quantity of files, and the infrequent use of the scraper
    (file count will never exceed character count in the game)"""

    homepage: str = await load_data(homepage_path)
    characters: list[Character] = select_characters(homepage)

    char_paths = [char.data_path for char in characters]

    # as files are read, process the moves
    async for cid, file in load_batch(char_paths):
        char = characters[cid]

        valid_moves = filter(move_filter, select_moves(file, char.name))
        logger.debug("Moves found for: [%s]", char.name)
        char.set_moves(list(valid_moves))

    return characters


async def fetch_all_and_store() -> None:
    homepage: str = await fetch_data(homepage_url)
    characters: list[Character] = select_characters(homepage)
    urls = (char.data_url for char in characters)

    # tasks: list[asyncio.Task[None]] = []
    tasks: list[asyncio._CoroutineLike] = []
    async for id, doc in fetch_batch(urls, delay=1):
        char = characters[id]
        tasks.append(store_data(char.data_path, doc))

    await asyncio.gather(*tasks)


# code to run if starting as script or rebuilding
async def launch(db: Database, scrape: bool) -> None:
    """Launches an update for the database.
    if parameter scrape is False, it will rebuild from locally stored data,
    else it will request files from dustloop
    """

    async def load_and_pair(char: Character, id: int) -> int:
        await db.insert_character(char)
        return id

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
    db = Database(processed_dir / "test.db")
    asyncio.run(launch(db, scrape=False))
