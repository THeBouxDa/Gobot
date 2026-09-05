import asyncio
import json
import time
from collections.abc import AsyncIterator, Iterable
from enum import Enum
from pathlib import Path

import requests
import requests.exceptions as rex

from modules.json_types import ScraperSettings
from modules.paths import scraping_config
from modules.utils.logging_utils import get_logger

type HTML_Document = str


class StatusClasses(Enum):
    SUCCESS = 200
    REDIRECTION = 300
    CLIENT_ERROR = 400
    SERVER_ERROR = 500


with scraping_config.open(encoding="utf8") as file:
    scraper_settings: ScraperSettings = json.load(file)

MAX_RETRIES: int = 3

logger = get_logger(__name__)


def _fetch_data_sync(url: str) -> HTML_Document:

    for retries in range(MAX_RETRIES):
        if retries > 0:
            logger.warning("Failed request, retrying to fetch %s", url)
            time.sleep(2**retries)

        try:
            response = requests.get(url, headers=scraper_settings["headers"], timeout=5)
            response.raise_for_status()
        except rex.Timeout:
            logger.exception("Timeout error for page %s", url)
        except rex.ConnectionError:
            logger.exception("Connection dropped/refused for %s", url)
        except rex.HTTPError as error:
            if (
                error.response is None
                or StatusClasses.CLIENT_ERROR.value
                <= (status_code := error.response.status_code)
                < StatusClasses.SERVER_ERROR.value
            ):
                logger.exception("Serious HTTP Error, aborting %s")
                raise rex.HTTPError(
                    "Something serious occurred while requesting, check logs!", url
                ) from error
            if status_code >= StatusClasses.SERVER_ERROR.value:
                logger.exception("Server Error %s for %s", status_code, url)
        except rex.RequestException:
            logger.exception("Unspecified network error for %s", url)
        else:
            logger.debug("Scraped %s", url)
            return response.text
    # if we got to this point, the request failed more than MAX_RETRIES
    logger.error("Max number of retries exceeded, aborting requests for %s", url)
    raise rex.RequestException(
        "Something serious occurred while requesting, check logs!"
    )


def _store_data_sync(filepath: Path, data: str) -> None:
    filepath.write_text(data, encoding="utf8")
    logger.success("Stored page: %s", filepath)


def _load_data_sync(path: Path) -> str:
    data = path.read_text(encoding="utf8")
    logger.debug("File was read: %s", str(path))

    return data


async def fetch_data(url: str, delay: float = 0) -> HTML_Document:
    await asyncio.sleep(delay)
    return await asyncio.to_thread(_fetch_data_sync, url)


async def store_data(filepath: Path, data: str) -> None:
    await asyncio.to_thread(_store_data_sync, filepath, data)


async def load_data(path: Path) -> str:
    return await asyncio.to_thread(_load_data_sync, path)


async def fetch_batch(
    urls: Iterable[str], delay: float
) -> AsyncIterator[tuple[int, HTML_Document]]:

    async def fetch_and_pair(url: str, delay: float, index: int) -> tuple[int, str]:
        mult = index + 1
        content = await fetch_data(url, delay * mult)
        return index, content

    tasks = [
        asyncio.create_task(fetch_and_pair(url, delay, index))
        for index, url in enumerate(urls)
    ]

    for completed_task in asyncio.as_completed(tasks):
        index, content = await completed_task
        yield index, content


async def store_batch(info: Iterable[tuple[Path, str]]) -> None:
    tasks = [store_data(*i) for i in info]
    await asyncio.gather(*tasks, return_exceptions=True)


async def load_batch(paths: Iterable[Path]) -> AsyncIterator[tuple[int, str]]:

    # wrapper function to return path paired with the contents
    async def load_and_pair(path: Path, index: int) -> tuple[int, str]:
        content = await load_data(path)
        return index, content

    # immediately start all the file reads
    tasks = [
        asyncio.create_task(load_and_pair(path, index))
        for index, path in enumerate(paths)
    ]

    # yield results as soon as they complete
    for completed_task in asyncio.as_completed(tasks):
        index, content = await completed_task
        yield index, content
