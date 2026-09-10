import hashlib
import re
import urllib.parse
from typing import TYPE_CHECKING

from modules.resources.configs import parsing_config, scraping_config
from modules.utils.logging_utils import get_logger

if TYPE_CHECKING:
    from modules.scraper.move import Move


logger = get_logger(__name__)


def move_filter(move: Move) -> bool:
    output: bool = True
    if (
        move.get_prop("name") in parsing_config["excluded_moves"]
        or move.get_prop("section") in parsing_config["ignored_sections"]
    ):
        output = False

    return output


def file_parser(files_string: str) -> str:
    result: str = files_string.strip().replace(" ", "_")

    if files_string != "":
        files = [file.strip().replace(" ", "_") for file in files_string.split(";")]
        files = [
            generate_dustloop_image_url(file)
            for file in files
            if len(file) > 0 and "GGST" in file
        ]
        result = ";".join(files)

    return result


def generate_dustloop_image_url(filename: str) -> str:
    """Generates the dustloop url for image files"""

    logger.debug("Generating URL for file: [%s]", filename)
    normalized = filename.replace(" ", "_")
    normalized = f"{normalized[0].upper()}{normalized[1:]}"

    md5_hash = hashlib.md5(normalized.encode("utf-8")).hexdigest()  # noqa: S324

    char1 = md5_hash[0]
    char2 = md5_hash[:2]
    hash_path = f"{char1}/{char2}"

    # I think the data already has this done, but better safe than sorry
    encoded_filename = urllib.parse.quote(normalized)
    url = scraping_config["image_url_template"].format(hash_path, encoded_filename)

    return url


def sanitize(string: str) -> str:
    return str(string.replace(" ", "_")).translate(
        str.maketrans("", "", parsing_config["broken_chars"])
    )


def tag_fixer(string: str) -> str:
    return string.replace("&lt;", "<").replace("&gt;", ">")


def line_breaker(string: str) -> str:
    string = tag_fixer(string)
    return string.replace("<br/>", "\n").replace("<br>", "\n")


def input_parser(string: str) -> str:
    result = string

    # Leo Whitefang requires this special exception
    if result == "[s/h] h/s":
        result = "[S]H;[H]S"
    elif (match := re.search(r"(\w(?:\/\w)+)", result)) is not None:
        pattern = match.group(1)
        replacements = pattern.split("/")
        result = ";".join([result.replace(pattern, r) for r in replacements])

    return result
