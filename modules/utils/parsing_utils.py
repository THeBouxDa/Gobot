import json
import re

from modules.json_types import Parser
from modules.move import Move
from modules.paths import parsing_config

with parsing_config.open(encoding="utf8") as file:
    settings: Parser = json.load(file)


def move_filter(move: Move) -> bool:
    output: bool = True
    if (
        move.get_prop("name") in settings["excluded_moves"]
        or move.get_prop("section") in settings["ignored_sections"]
    ):
        output = False

    return output


def file_parser(url: str) -> str:
    return url.replace(" ", "_")


def sanitize(string: str) -> str:
    return str(string.replace(" ", "_")).translate(
        str.maketrans("", "", settings["broken_chars"])
    )


def tag_fixer(string: str) -> str:
    return string.replace("&lt;", "<").replace("&gt;", ">")


def line_breaker(string: str) -> str:
    string = tag_fixer(string)
    return string.replace("<br/>", "\n").replace("<br>", "\n")


def input_parser(string: str) -> str:
    result = string.upper()

    # Leo Whitefang requires this special exception
    if result == "[S/H] H/S":
        result = "[S]H;[H]S"
    elif (match := re.search(r"(\w(?:\/\w)+)", result)) is not None:
        pattern = match.group(1)
        replacements = pattern.split("/")
        result = ";".join([result.replace(pattern, r) for r in replacements])

    return result
