from typing import TYPE_CHECKING, TypedDict

from modules.resources.paths import queries_dir
from modules.utils.logging_utils import get_logger

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path


class Query(TypedDict):
    single: str
    multi: Iterable[str]


def subdir_list(file: Path) -> list[Path]:
    chain: list[Path] = []
    for parent in file.parents:
        if parent == queries_dir:
            break

        chain.append(parent)

    chain.reverse()
    return chain


logger = get_logger(__name__)

queries: dict[str, Query] = {}
for file in queries_dir.glob("**/*.sql"):
    contents = file.read_text(encoding="utf8")
    single = contents
    multi = [query.strip() + ";" for query in contents.strip().split(";") if query]
    prefix = ".".join(parent.name for parent in subdir_list(file))

    queries[f"{prefix}.{file.stem}"] = Query(single=single, multi=multi)
    logger.checkpoint(
        "Loaded %s from queries, key: %s, value:\n%s",
        file.name,
        file.stem,
        contents,
    )


def get_query(key: str) -> str:
    return queries[key]["single"]


def get_query_iter(key: str) -> Iterable[str]:
    return queries[key]["multi"]
