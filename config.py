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

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}