import psycopg2
import pandas as pd
# Database connection parameters
params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '2108',
    'host': 'localhost',  # or the IP address of your PostgreSQL server
    'port': '5432'  # default port for PostgreSQL
}

def addGame(game_name: str, likes: int, user_path: str):
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    game_info = "SELECT ge.genre_name, d.dev_name, g.score FROM GAME g JOIN WAS_DEV wd ON g.name = wd.game_name JOIN DEVELOPER d on wd.dev_id = d.dev_id JOIN HAS_GENRE hg on wd.game_name = hg.game_name JOIN GENRE ge on ge.genre_id = hg.genre_id WHERE g.name = %s"
    cur.execute(game_info, (game_name,))
    result = cur.fetchall()
    if cur.rowcount == 0:
        print(f"Error. There is no result from the query. game was: {game_name}")
    else:
        genres = set()
        devs = set()
        score = result[0][2]
        for row in result:
            genres.add(row[0])
            devs.add(row[1])
        str_genres = ','.join(genres)
        str_devs = ','.join(devs)
        with open(user_path, 'a') as file:
            file.write(f'\n{game_name},\"{str_genres}\",\"{str_devs}\",{score},{likes}')

    conn.commit()
    cur.close()
    conn.close()
