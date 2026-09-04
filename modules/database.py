from typing import Iterable
import logging

import aiosqlite
from pathlib import Path

from modules.character import Character, Move
from configs.config import db_bound_keys





CREATE_TABLES: str = """
    PRAGMA journal_mode=WAL;
    
    CREATE TABLE IF NOT EXISTS characters (
        character_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        path TEXT NOT NULL UNIQUE,
        page_url TEXT NOT NULL UNIQUE,
        data_url TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS moves (
        move_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
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

    CREATE TABLE IF NOT EXISTS move_aliases (
        alias_id INTEGER PRIMARY KEY AUTOINCREMENT,
        alias TEXT UNIQUE NOT NULL,
        move_id INT NOT NULL,
        FOREIGN KEY (move_id) REFERENCES moves (move_id)
    );
"""


CLEAR_TABLES: str = """
    DROP TABLE IF EXISTS characters;
    DROP TABLE IF EXISTS moves;
"""


INSERT_CHARACTER = "INSERT INTO characters (name, path, page_url, data_url) VALUES (?, ?, ?, ?);"
INSERT_MOVE = """INSERT INTO moves
    (category, name, input, startup, active, recovery, damage, guard, invuln, images, hitboxes, onBlock, onHit, char_name) values
    (:category, :name, :input, :startup, :active, :recovery, :damage, :guard, :invuln, :images, :hitboxes, :onBlock, :onHit, :char_name);
"""


type CharacterData = tuple[str, str, str, str]

logger = logging.getLogger(__name__)



class Database:
    def __init__(self, db_filepath: Path) -> None:
        self.path = db_filepath


    async def create_tables(self):
        async with aiosqlite.connect(self.path) as db:
            await db.executescript(CREATE_TABLES)
            await db.commit()
            logger.success("Tables created successfully.") # type: ignore
    
    
    async def clear_tables(self):
        async with aiosqlite.connect(self.path) as db:
            await db.executescript(CLEAR_TABLES)
    

    async def insert_characters(self, characters: Iterable[Character]):
        async with aiosqlite.connect(self.path) as db:
            props: Iterable[CharacterData] = (
                (char.name, str(char.data_path), char.page_url, char.data_url)
                for char in characters
            )
            
            await db.executemany(INSERT_CHARACTER, props)
            await db.commit()
            logger.success("Inserted all characters.") # type: ignore
    
    
    async def insert_character(self, character: Character):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(INSERT_CHARACTER, (
                character.name, str(character.data_path),
                character.page_url, character.data_url,
            ))
            
            await db.commit()
            logger.info("Character [%s] inserted successfully.", character.name)


    # just in case i get asked why i require char_name, it's because i
    # don't trust dustloop editors to fill it in for every move
    async def insert_moves(self, moves: list[Move]):
        async with aiosqlite.connect(self.path) as db:

            move_gen = (move.data for move in moves)
            
            await db.executemany(INSERT_MOVE, move_gen)
            await db.commit()
            logger.info("Moves for [%s] inserted successfully")