import requests
from bs4 import BeautifulSoup


def get_game_link(game_name_og : str) -> str:
    game_name = game_name_og.lower()

    # pongo en formato para link de steam ejemplo: "https://store.steampowered.com/search/?term=god+of+war", lowercase con + en lugar de espacios
    game_name = game_name.replace(" ", "+")

    url = "https://store.steampowered.com/search/?term=" + game_name

    html_text = requests.get(url).text # obtengo el html como string
    soup = BeautifulSoup(html_text, 'html.parser')
    link = soup.find("a", {"class": "search_result_row ds_collapse_flag"})
    if link is not None:
        return link.get("href")
    return link
    
def get_game_synopsis(game_name_og) -> str:
    url = get_game_link(game_name_og)

    if url is not None:
        html_text = requests.get(url).text
        soup = BeautifulSoup(html_text, 'html.parser')
        synopsis = soup.find("div",{"class": "game_description_snippet"})
        if synopsis is not None:
            return synopsis.get_text().strip()
        return synopsis
    return url


