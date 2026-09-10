from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import aiosqlite
from sqlalchemy import text

from modules.utils.logging_utils import get_logger

type Connection = aiosqlite.Connection
type ConnectionPool = asyncio.Queue[Connection]


if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from sqlalchemy.ext.asyncio.engine import AsyncEngine

    from modules.scraper.character import Character, Move


CONNECTION_MAX = 5

CREATE_TABLES = [
    """
        PRAGMA journal_mode=WAL;
    """,
    """
        CREATE TABLE IF NOT EXISTS characters (
            character_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            path TEXT NOT NULL UNIQUE,
            page_url TEXT NOT NULL UNIQUE,
            data_url TEXT NOT NULL UNIQUE
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS moves (
            move_id INTEGER PRIMARY KEY AUTOINCREMENT,
            section TEXT,
            category TEXT,
            name TEXT,
            input TEXT,
            guard TEXT,
            invuln TEXT,
            damage TEXT,
            startup TEXT,
            active TEXT,
            recovery TEXT,
            images TEXT,
            hitboxes TEXT,
            onBlock TEXT,
            onHit TEXT,
            char_name TEXT NOT NULL,
            UNIQUE(char_name, input) ON CONFLICT IGNORE,
            FOREIGN KEY (char_name) REFERENCES characters (name)
        );
    """,
]
CLEAR_TABLES = ["DROP TABLE IF EXISTS characters;", "DROP TABLE IF EXISTS moves;"]

INSERT_CHARACTER = (
    "INSERT INTO characters (name, path, page_url, data_url) VALUES (:a, :b, :c, :d);"
)
INSERT_MOVE = """INSERT INTO moves
    (section, category, name, input, startup, active, recovery, damage, guard, invuln, images, hitboxes, onBlock, onHit, char_name) values
    (:section, :category, :name, :input, :startup, :active, :recovery, :damage, :guard, :invuln, :images, :hitboxes, :onBlock, :onHit, :char_name);
"""


type DataMap = Mapping[str, str]

logger = get_logger(__name__)


class ConnectionManager:
    def __init__(self, engine: AsyncEngine) -> None:
        self.engine = engine

    async def create_tables(self) -> None:
        async with self.engine.begin() as conn:
            for query in CREATE_TABLES:
                await conn.execute(text(query))

            logger.checkpoint("Tables created successfully.")

    async def clear_tables(self) -> None:
        async with self.engine.begin() as conn:
            for query in CLEAR_TABLES:
                await conn.execute(text(query))

        logger.checkpoint("Tables dropped successfully.")

    async def insert_characters(self, characters: Sequence[Character]) -> None:
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
            await conn.execute(text(INSERT_CHARACTER), props)

        logger.checkpoint("Inserted all characters.")

    async def insert_moves(self, moves: list[Move]) -> None:
        move_gen: list[DataMap] = [move.data for move in moves]
        async with self.engine.begin() as conn:
            await conn.execute(text(INSERT_MOVE), move_gen)
            await conn.commit()
