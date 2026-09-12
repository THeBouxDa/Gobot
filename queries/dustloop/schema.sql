PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS characters (
    character_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    path TEXT NOT NULL UNIQUE,
    page_url TEXT NOT NULL UNIQUE,
    data_url TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS moves (
    move_id INTEGER PRIMARY KEY AUTOINCREMENT,
    section TEXT,
    category TEXT,
    name TEXT COLLATE NOCASE,
    input TEXT COLLATE NOCASE,
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
    char_name TEXT NOT NULL COLLATE NOCASE,
    UNIQUE(char_name, input) ON CONFLICT IGNORE,
    FOREIGN KEY (char_name) REFERENCES characters (name)
);

CREATE TABLE IF NOT EXISTS character_aliases (
    alias_id INTEGER PRIMARY KEY AUTOINCREMENT,
    alias TEXT NOT NULL UNIQUE COLLATE NOCASE,
    char_name TEXT NOT NULL COLLATE NOCASE
);

CREATE TABLE IF NOT EXISTS move_aliases (
    alias_id INTEGER PRIMARY KEY AUTOINCREMENT,
    alias TEXT NOT NULL COLLATE NOCASE,
    move_input TEXT NOT NULL COLLATE NOCASE,
    char_name TEXT NOT NULL COLLATE NOCASE,
    UNIQUE(char_name, alias)
);

CREATE INDEX IF NOT EXISTS idx_moves_char ON moves(char_name);
CREATE INDEX IF NOT EXISTS idx_moves_name ON moves(name);
CREATE INDEX IF NOT EXISTS idx_moves_input ON moves(input);

CREATE INDEX IF NOT EXISTS idx_char_aliases_lookup ON character_aliases(alias, char_name);
CREATE INDEX IF NOT EXISTS idx_move_aliases_lookup ON move_aliases(alias, move_input, char_name);