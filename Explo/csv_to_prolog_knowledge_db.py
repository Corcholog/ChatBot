import csv
import subprocess
import re

filename = "games-data.csv"

fields = []
rows = []

#reading csv

with open(filename, 'r') as csvfile:
    csvreader = csv.reader(csvfile) # abro en modo READ

    fields = next(csvreader) #como la primer fila son los nombres de los campos, los guardo iterando.

    for row in csvreader: # leo todas las filas
        rows.append(row)

    print("Total number of games: %d"%(csvreader.line_num)) 



# The Legend of Zelda: Ocarina of Time, Nintendo64, November 23, 1998, 99, 9.1, Nintendo, Action Adventure,Fantasy, 1 Player, 22, 5749,

class Game:
    def __init__(self, game_info):
        self.name = game_info[0].replace('"','\\\"')
        self.platform = game_info[1]
        self.release_date = game_info[2].replace(",", "")
        self.score = str('"'+game_info[3]+'"')
        self.u_score = game_info[4]
        self.developer = game_info[5].replace(" ", "") #quito espacios
        self.developer = self.developer.replace("[", "")
        self.developer = self.developer.replace("]", "")
        self.developer = self.developer.split(',') #convierto en lista
        self.genre = game_info[6].replace("Action Adventure", "Action,Adventure")
        self.genre = self.genre.replace("'", "") #quito comillas simples
        self.genre = self.genre.replace('"', '') #quito comillas dobles
        self.genre = self.genre.split(',') #convierto en lista
        self.players = game_info[7]
        self.critics = game_info[8]
        self.users = game_info[9]
    
    def __str__(self):
        return f"{self.name}, {self.platform}, {self.release_date}, {self.score}, {self.u_score}, {self.developer}, {self.genre}, {self.players}, {self.critics}, {self.users}"


def update_gdb(rows):
    gdb = open("game_db.txt", "w")
    for row in rows:
        a = Game(row) 
        #print(a.developer)
        #gdb.write(a.__str__())
        #gdb.write("\n")
    gdb.close()

def update_kdb(rows):
    processed_games = set()  # Initialize a set to keep track of processed game names

    db = open("knowledge_db.pl", "w")
    #escribo hechos
    genre = set()
    for row in rows:
        a = Game(row)
         # Create a unique identifier for the game using its name and score
        game_identifier = f"{a.name}"
        
        genre.add(f"{a.genre}")
        # Check if the game has already been processed
        if game_identifier not in processed_games:
            
            # Add the game identifier to the set of processed games
            db.write(f"game(\"{a.name}\").\n")
            db.write(f"release_date(\"{a.name}\",\"{a.release_date}\").\n")
            db.write(f"score(\"{a.name}\",{a.score}).\n")
            db.write(f"u_score(\"{a.name}\",\"{a.u_score}\").\n")
            formatted_dev = "['" + ', '.join([elemento.strip("'") for elemento in a.developer]) + "']"
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

            processed_games.add(game_identifier)
        else:
            db.write(f"platform(\"{a.name}\",\"{a.platform}\").\n")

    gens = open("C:/Users/logue/OneDrive/Escritorio/Explo/data/genres.txt", "w")
    for gen in genre:
        gens.write(f"{gen}\n")
    gens.close()



        # Read the file with genres
    with open("C:/Users/logue/OneDrive/Escritorio/Explo/data/genres.txt", 'r') as infile:
        lines = infile.readlines()

    # Create a set to store unique genres
    unique_genres = set()

    # Extract unique genres from the lines
    for line in lines:
        genres = line.strip().strip('[]').replace(' ', '').split(',')
        unique_genres.update(genres)

    # Write the unique genres to a new file
    with open("C:/Users/logue/OneDrive/Escritorio/Explo/data/genres.txt", 'w') as outfile:
        for genre in unique_genres:
            genre = genre.replace("'", "")
            outfile.write(f"- {genre}\n")

    #cierro archivo 
    db.close()
        # Define a regular expression pattern to match the lines you want to modify
    pattern = re.compile(r'platform\("([^"]+)",\s*"([^"]+)"\)\.')

    # Read lines from the file
    with open('knowledge_db.pl', 'r') as file:
        lines = file.readlines()

    # Create a dictionary to store the unified entries
    platforms_dict = {}

    # Parse and update the dictionary
    for line in lines:
        match = pattern.match(line)
        if match:
            game_name = match.group(1)
            platform = match.group(2)

            if game_name in platforms_dict:
                platforms_dict[game_name].append(platform)
            else:
                platforms_dict[game_name] = [platform]

    # Write the updated entries back to the file, preserving other lines
    with open('knowledge_db.pl', 'w') as file:
        added_games = set()
        for line in lines:
            match = pattern.match(line)
            if match:
                game_name = match.group(1)
                if game_name not in added_games:
                    platforms = platforms_dict[game_name]
                    platforms_str = "','".join(platforms)
                    file.write(f"platform(\"{game_name}\",['{platforms_str}']).\n")
                added_games.add(game_name)
            else:
                file.write(line)
    #reordeno
    subprocess.run("sort knowledge_db.pl /o knowledge_db.pl", cwd="C:/Users/logue/OneDrive/Escritorio/Explo")

update_kdb(rows)
#update_gdb(rows)

