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