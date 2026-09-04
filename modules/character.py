from pathlib import Path

from modules.utils.util import sanitize
from modules.move import Move



class Character:
    def __init__(self, name: str, page_url: str, safe_name: str, data_url: str, data_path: Path) -> None:
        self.name = name
        self.safe_name = safe_name
        self.page_url = page_url
        self.data_url = data_url
        self.data_path = data_path
        
        self.moves: list[Move] = []


    def __repr__(self) -> str:
        return self.format_self(0)
    
    
    def format_self(self, depth: int) -> str:
        start: list[str] | str = []
        indent: str = "\t" * depth
        end: str = f'{indent}]'
        
        start.append(f'{indent}Name: "{self.name}",')
        start.append(f'{indent}URL: "{self.page_url}",')
        start.append(f'{indent}Moves: [')
        start.append(self.format_moves(depth + 1))
        start = "\n".join(start)
        
        return f'{start}\n{end}'

    
    def format_moves(self, depth: int = 0):
        moves: list[str] = [move.format_self(depth) for move in self.moves]
        return ",\n".join(moves)


    def set_moves(self, moves: list[Move]) -> None:
        self.moves = moves


    def add_move(self, move: Move) -> None:
        self.moves.append(move)