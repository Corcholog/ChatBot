import csv
import subprocess
import re

filename = "games-data.csv"

fields = []
rows = []

#leo csv

with open(filename, 'r') as csvfile:
    csvreader = csv.reader(csvfile) # abro en modo lectura

    fields = next(csvreader) # como la primer fila son los nombres de los campos, los guardo iterando.

    for row in csvreader: # leo todas las filas
        rows.append(row)


# row format -> game name, platform, release date, score, user score, developer, genres, players, critics, users

class Game:
    def __init__(self, game_info):
        self.name = game_info[0].replace('"','\\\"')
        self.platform = game_info[1]
        self.release_date = game_info[2].replace(",", "")
        self.score = str('"'+game_info[3]+'"')
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


def update_gdb(rows):
    gdb = open("game_db.txt", "w")
    for row in rows:
        a = Game(row) 
    gdb.close()

def update_kdb(rows):
    processed_games = set()  # inicializo un set de juegos que ya procesé para evitar tuplas repetidas por juegos que cambia su plataforma
    db = open("knowledge_db.pl", "w") # abro en modo escritura la base de conocimientos de Prolog
    for row in rows:
        a = Game(row)
        game_identifier = f"{a.name}" # me guardo el nombre del juego de la fila que estoy procesando

        # me fijo si no fue procesado previamente
        if game_identifier not in processed_games:
            
            # si no fue procesado lo agrego a la base de conocimientos.
            db.write(f"game(\"{a.name}\").\n")
            db.write(f"release_date(\"{a.name}\",\"{a.release_date}\").\n")
            db.write(f"score(\"{a.name}\",{a.score}).\n")
            db.write(f"u_score(\"{a.name}\",\"{a.u_score}\").\n")
            formatted_dev = "['" + ', '.join([elemento.strip("'") for elemento in a.developer]) + "']" #pongo [] para formato de lista de prolog
            formatted_dev = formatted_dev.replace('"','\\\"')
            formatted_dev = formatted_dev.replace("'", "")
            formatted_dev = formatted_dev.replace("[", "['")
            formatted_dev = formatted_dev.replace("]", "']")
            formatted_dev = formatted_dev.replace(" ", "")
            formatted_dev = formatted_dev.replace(",", "','")
            db.write(f"developer(\"{a.name}\",{formatted_dev}).\n")
            db.write(f"genre(\"{a.name}\",{a.genre}).\n")
            db.write(f"players(\"{a.name}\",\"{a.players}\").\n")
            db.write(f"critics(\"{a.name}\",\"{a.critics}\").\n")
            db.write(f"users(\"{a.name}\",\"{a.users}\").\n")
            db.write(f"platform(\"{a.name}\",\"{a.platform}\").\n")
            processed_games.add(game_identifier) # lo guardo como procesado 
        else:
            db.write(f"platform(\"{a.name}\",\"{a.platform}\").\n") # si ya fue procesado pero lo estoy leyendo de nuevo es que existe el mismo juego en otra plataforma.

    #cierro archivo 
    db.close()

    #reordeno
    subprocess.run("sort knowledge_db.pl /o knowledge_db.pl", cwd="C:/Users/logue/OneDrive/Escritorio/ChatBot/Explo")

update_kdb(rows)
#update_gdb(rows)

