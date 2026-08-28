from typing import Collection

class Move:
    def __init__(self, name: str, character: str, picture: str, hitbox: str) -> None:
        pass

class Character:
    def __init__(self, name: str, page_url: str) -> None:
        self.name = name
        # self.page_url = str.join(DOMAIN, page_url)
        self.page_url = page_url
        
        self.moves: list[Move] = []
    
    
    def __repr__(self) -> str:
        return f"({self.name}, {self.page_url})"
    

    def set_moves(self, moves: list[Move]) -> None:
        self.moves = moves
    

    def add_move(self, move: Move) -> None:
        self.moves.append(move)