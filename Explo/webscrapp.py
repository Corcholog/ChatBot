import requests
from bs4 import BeautifulSoup


def get_game_link(game_name_og : str) -> str:
    game_name = game_name_og.lower()

    # pongo en formato para link de steam ejemplo: "https://store.steampowered.com/search/?term=god+of+war", lowercase con + en lugar de espacios
    game_name = game_name.replace(" ", "+")

    url = "https://store.steampowered.com/search/?term=" + game_name

    html_text = requests.get(url).text # obtengo el html como string
    soup = BeautifulSoup(html_text, 'html.parser')
    img = soup.find_all("div", {"id": {"highlight_strip"}})
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

def esp_news() -> list:
    url = "https://www.3djuegos.com/noticias"

    if url is not None:
        html_text = requests.get(url).text
        soup = BeautifulSoup(html_text, 'html.parser')
        articles = soup.find_all("article", {"class" : "m-river-item-post"})
        news = []
        for post in articles:
            news.append(post.find("h2",{"class": "m-river-item-post__title"}).get_text().strip())
        return news
    return url

def eng_news() -> str:
    url = "https://www.thegamer.com/category/game-news/"

    if url is not None:
        html_text = requests.get(url).text
        soup = BeautifulSoup(html_text, 'html.parser')
        aux = soup.find_all("div", {"class" : "display-card article large"})
        aux2 = soup.find_all("div", {"class" : "display-card article small"})
        news = []
        for art in aux:
            news.append(art.find("h5", {"class": "display-card-title"}).get_text().strip())
        for art2 in aux2:
            news.append(art2.find("h5", {"class": "display-card-title"}).get_text().strip())
        return news
    return url

def get_first_image_from_google(query):
    # Define the URL and headers
    query = query.lower()
    query = query.replace(" ", "+")
    url = "https://duckduckgo.com/?t=h_&q="+ query + "&iax=images&ia=images"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Make the request
    response = requests.get(url, headers=headers)
    
    # Parse the response with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the first image
    img_tag = soup.find("img")
    
    # Return the image URL
    if img_tag:
        return img_tag["src"]
    else:
        return None
