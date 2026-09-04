from typing import Iterable

from pathlib import Path


# TODO: separate this into something that makes sense


emoji_list: dict[str, str] = {
    "rock": "🪨",
    "paper": "🗞",
    "scissors": "✂",
    "hand_rock": "✊",
    "hand_paper": "✋",
    "hand_scissors": "✌️"
}

rps_result: dict[str, str] = {
    "draw": "You Drew!",
    "win": "You Won!",
    "lose": "You Lost!"
}

rps_match: dict[str, list[tuple[str, str]]] = {
    "win": [
        ("rock", "scissors"),
        ("paper", "rock"),
        ("scissors", "paper")
    ],
    "lose": [
        ("rock", "paper"),
        ("paper", "scissors"),
        ("scissors", "rock")
    ]
}

excluded_moves = [
    "Wild Assault",
    "Charged Wild Assault",
    "Finish Blow",
    "Dash Cancel",
    "Taunt A",
    "Respect A",
    "Taunt B",
    "Respect B",
]

ignored_sections: list[str] = [
    "Character Mechanics"
]

broken_chars: str = "♯'?"

raw_section_pattern = r'^==([\w ]+)==$'
raw_group_pattern = r'^===(.+?)(?: Data)?===$'
raw_property_pattern = r'^\|.+=.*'


db_bound_keys: Iterable[str] = [
    "name",
    "category",
    "input",
    "guard",
    "invuln",
    "damage",
    "startup",
    "active",
    "recovery",
    "images",
    "hitboxes",
    "onBlock",
    "onHit",
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


authorized_users: dict[str, str] = {
    "me": "216871695359672320"
}



cwd = Path.cwd()
data_dir = cwd / 'data'
logs_dir = cwd / 'logs'
raw_dir = data_dir / 'raw'
processed_dir = data_dir / 'processed'
characters_dir = raw_dir / 'characters'
homepage_path = raw_dir / "homepage.html"