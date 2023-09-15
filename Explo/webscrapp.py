import requests
from bs4 import BeautifulSoup

def get_game_link(game_name) -> str:
    game_name = game_name.lower()
    
    #pongo en formato para link de steam ejemplo: "https://store.steampowered.com/search/?term=god+of+war", lowercase con + en lugar de espacios
    #quito caracteres no alfanumericos
    game_name = game_name.replace(" ", "+")

    url = "https://store.steampowered.com/search/?term=" + game_name

    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'html.parser')
    link = soup.find("a", {"class": "search_result_row ds_collapse_flag"}).get("href")
    print(link)
    return link

