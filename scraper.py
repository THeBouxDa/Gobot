from time import sleep
from typing import Final

import requests
from pathlib import Path

from bs4 import BeautifulSoup

from config import headers
from modules.character_model import Character



DOMAIN: Final[str] = "https://dustloop.com"
homepage_url = f"{DOMAIN}/w/GGST"
homepage = Path.absolute(Path.joinpath(Path.cwd(), 'data', 'raw', 'homepage.html'))

def scrape_data(url, filepath):
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()  # Check for HTTP errors

    with open(filepath, "w", encoding="utf8") as file:
        file.write(response.text)


def get_characters(characters):
    for name, character in characters.items():
        url = character.page_url
        filepath = Path.absolute(Path.joinpath(Path.cwd(), 'data', 'raw', 'characters', f"{name}.html"))

        scrape_data(url, filepath)
        sleep(3)


def find_characters() -> dict[str, Character]:
    characters: dict[str, Character] = {}
    
    with open(homepage, "r", encoding="utf8") as file:
        soup = BeautifulSoup(file.read(), "html.parser")

        character_links = soup.select(".home-card > div.add-hover-effect > span > a")
        character_links += soup.select(".home-card > div.add-hover-effect > p > span > a")

        for link in character_links:
            name = str(link.attrs['title']).strip("?")
            url = f"{DOMAIN}{str(link.attrs['href'])}"
            
            characters[name] = Character(name, url)
        
    return characters


def find_moves(character: Character):
    moves = []

    filepath = Path.absolute(Path.joinpath(
        Path.cwd(),
        'data',
        'raw',
        'characters',
        f"{character.name}.html"
    ))
    
    with open(filepath, "r", encoding="utf8") as file:
        soup = BeautifulSoup(file.read(), "html.parser")
        move_containers = soup.select(".attack-container")
        
        for container in move_containers:
            pass
            
            
    return moves


if __name__ == "__main__":
    characters = find_characters()
    
    
    

    # # 4. Extract specific elements (e.g., Hacker News titles using CSS selectors)
    # links = soup.select(".titleline > a")

    # # 5. Loop and print the data
    # for index, link in enumerate(links[:10], start=1):
    #     title = link.get_text()
    #     href = link.get("href")
    #     print(f"{index}. {title} \n   URL: {href}\n")