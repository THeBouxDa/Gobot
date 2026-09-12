from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import aiosqlite
from sqlalchemy import text

from modules.resources.queries import get_query, get_query_iter
from modules.utils.logging_utils import get_logger

type Connection = aiosqlite.Connection
type ConnectionPool = asyncio.Queue[Connection]


if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from sqlalchemy.ext.asyncio.engine import AsyncEngine

    from modules.scraper.character import Character, Move


type DataMap = Mapping[str, str]

logger = get_logger(__name__)


class ConnectionManager:
    def __init__(self, engine: AsyncEngine) -> None:
        self.engine = engine

    async def create_tables(self) -> None:
        async with self.engine.begin() as conn:
            for query in get_query_iter("dustloop.schema"):
                await conn.execute(text(query))

            logger.checkpoint("Tables created successfully.")

    async def drop_tables(self) -> None:
        async with self.engine.begin() as conn:
            for query in get_query_iter("dustloop.drop_tables"):
                await conn.execute(text(query))

        logger.checkpoint("Tables dropped successfully.")

    async def insert_characters(self, characters: Sequence[Character]) -> None:
        query = get_query("dustloop.insert_character")
        props: list[DataMap] = [
            {
                "a": char.name,
                "b": str(char.data_path),
                "c": char.page_url,
                "d": char.data_url,
            }
            for char in characters
        ]

        async with self.engine.begin() as conn:
            await conn.execute(text(query), props)

        logger.checkpoint("Inserted all characters.")

    async def insert_moves(self, moves: list[Move]) -> None:
        query = get_query("dustloop.insert_move")

        move_gen: list[DataMap] = [move.data for move in moves]
        async with self.engine.begin() as conn:
            await conn.execute(text(query), move_gen)
