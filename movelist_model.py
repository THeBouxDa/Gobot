import aiosqlite
import sqlite3
import asyncio
from pathlib import Path

STATEMENTS: list[str] = [
    """
        CREATE TABLE IF NOT EXISTS characters (
            character_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS moves (
            move_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            character_id INT NOT NULL,
            FOREIGN KEY (character_id) REFERENCES characters (character_id)
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS char_aliases (
            alias_id INTEGER PRIMARY KEY AUTOINCREMENT,
            alias TEXT UNIQUE NOT NULL,
            character_id INT NOT NULL,
            FOREIGN KEY (character_id) REFERENCES characters (character_id)
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS move_aliases (
            alias_id INTEGER PRIMARY KEY AUTOINCREMENT,
            alias TEXT UNIQUE NOT NULL,
            move_id INT NOT NULL,
            FOREIGN KEY (move_id) REFERENCES characters (move_id)
        );
    """
]

class Database:
    def __init__(self, db_filepath: Path) -> None:
        self.db_filepath = db_filepath

    
    # def create_tables(self):
    #     with sqlite3.connect(self.db_filepath) as connection:
    #         cursor = connection.cursor()
            
    #         for statement in STATEMENTS:
    #             cursor.execute(statement)
            
    #         connection.commit()
    #         print("Tables created successfully.")
    
    async def create_tables(self):
        async with aiosqlite.connect(self.db_filepath) as connection:
            for statement in STATEMENTS:
                await connection.execute(statement)
            
            await connection.commit()
            print("Tables created successfully.")