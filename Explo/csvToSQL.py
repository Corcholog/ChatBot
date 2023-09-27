import csv
import psycopg2

# Database connection parameters
params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '2108',
    'host': 'localhost',  # or the IP address of your PostgreSQL server
    'port': '5432'  # default port for PostgreSQL
}

class Game:
    def __init__(self, game_info):
        self.name = game_info[0].replace('"','\\\"')
        self.platform = game_info[1]
        self.release_date = game_info[2].replace(",", "")
        self.score = game_info[3]
        self.u_score = game_info[4]
        self.developer = game_info[5].replace(" ", "") # quito espacios
        self.developer = self.developer.replace("[", "") # quito caracteres no alfanumericos que me dan conflictos para escribir reglas en prolog.
        self.developer = self.developer.replace("]", "")
        self.developer = self.developer.split(',') # convierto en lista
        self.genre = game_info[6].replace("Action Adventure", "Action,Adventure")
        self.genre = self.genre.replace("'", "") # quito comillas simples
        self.genre = self.genre.replace('"', '') # quito comillas dobles
        self.genre = self.genre.split(',') # convierto en lista
        self.players = game_info[7]
        self.critics = game_info[8]
        self.users = game_info[9]
    
    def __str__(self):
        return f"{self.name}, {self.platform}, {self.release_date}, {self.score}, {self.u_score}, {self.developer}, {self.genre}, {self.players}, {self.critics}, {self.users}"
    
filename = 'C:/Users/logue/OneDrive/Escritorio/ChatBot/Explo/games-data.csv'

fields = []
rows = []

# leo csv 
# row format -> game name, platform, release date, score, user score, developer, genres, players, critics, users

with open(filename, 'r') as csvfile:
    csvreader = csv.reader(csvfile) # abro en modo lectura

    fields = next(csvreader) # como la primer fila son los nombres de los campos, los guardo iterando.

    for row in csvreader: # leo todas las filas
        rows.append(row)

def mudanza(rows):

    # Establish the connection
    conn = psycopg2.connect(**params)

    # Create a cursor object
    cur = conn.cursor()

    processed_genres = set()
    processed_developers = set()
    processed_platforms = set()
    g_id = 0
    d_id = 0
    p_id = 0
    for row in rows:
        a = Game(row)
        for g in a.genre:
            if g not in processed_genres:
                cur.execute("INSERT INTO GENRE(genre_id, genre_name) VALUES (%s, %s)", (g_id, g))
                g_id = g_id + 1
                processed_genres.add(g)

        for d in a.developer:
            if d not in processed_developers:
                cur.execute("INSERT INTO DEVELOPER(dev_id, dev_name) VALUES (%s, %s)", (d_id, d))
                d_id = d_id + 1
                processed_developers.add(d)

        if a.platform not in processed_platforms:
            cur.execute("INSERT INTO PLATFORM(platform_id, platform_name) VALUES (%s, %s)", (p_id, a.platform))
            p_id = p_id + 1
            processed_platforms.add(a.platform)
    
    processed_games = set()
    for row in rows:
        a = Game(row)
        if a.name not in processed_games:
            cur.execute("INSERT INTO GAME(name, score, user_score, players, critics, users) VALUES (%s, %s, %s, %s, %s, %s)", (a.name, a.score, a.u_score, a.players, a.critics, a.users))

            for d in a.developer:
                queryd = "SELECT dev_id FROM DEVELOPER WHERE dev_name = %s"

                cur.execute(queryd, (d,))
                resultd = cur.fetchone()
                dev_id = resultd[0]

                cur.execute("SELECT 1 FROM WAS_DEV WHERE game_name = %s AND dev_id = %s", (a.name, dev_id))
                exists = cur.fetchone()

                if not exists:
                    cur.execute("INSERT INTO WAS_DEV(game_name, dev_id) VALUES (%s, %s)", (a.name, dev_id))

            
            genset = set()
            for gen in a.genre:
                genset.add(gen)

            for g in genset:

                # SQL query to fetch the genre_id based on genre_name
                queryg = "SELECT genre_id FROM GENRE WHERE genre_name = %s"

                # Execute the query
                cur.execute(queryg, (g,))

                # Fetch the result
                resultg = cur.fetchone()
                genre_id = resultg[0]
                cur.execute("INSERT INTO HAS_GENRE(game_name, genre_id) VALUES (%s, %s)", (a.name, genre_id))
            
            queryp = "SELECT platform_id FROM PLATFORM WHERE platform_name = %s"
            cur.execute(queryp, (a.platform,))
            resultp = cur.fetchone()
            pl_id = resultp[0]
            cur.execute("INSERT INTO IS_IN(game_name, platform_id, release_date) VALUES (%s, %s, %s)", (a.name, pl_id, a.release_date))
            processed_games.add(a.name)
        else:
            queryp = "SELECT platform_id FROM PLATFORM WHERE platform_name = %s"
            cur.execute(queryp, (a.platform,))
            resultp = cur.fetchone()
            pl_id = resultp[0]
            cur.execute("SELECT 1 FROM IS_IN WHERE game_name = %s AND platform_id = %s AND release_date = %s", (a.name, pl_id, a.release_date))
            exists = cur.fetchone()

            if not exists:
                cur.execute("INSERT INTO IS_IN(game_name, platform_id, release_date) VALUES (%s, %s, %s)", (a.name, pl_id, a.release_date))
    
    # Commit the transaction
    conn.commit()

    # Close the cursor and connection
    cur.close()
    conn.close()

mudanza(rows)