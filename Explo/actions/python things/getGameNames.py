import csv

# Input and output file paths
input_file_path = 'C:/Users/logue/OneDrive/Escritorio/ChatBot/Explo/games-data.csv'
output_file_path = 'C:/Users/logue/OneDrive/Escritorio/ChatBot/Explo/actions/python things/games_lookup.txt'



with open(input_file_path, 'r') as csv_file, open(output_file_path, 'w') as txt_file:
    reader = csv.reader(csv_file)
    next(reader)  # Skip the header row if there's one
    
    processed_games = set()
    for row in reader:
        if row[0] not in processed_games:
            name = row[0] 
            txt_file.write('- '+ name.replace('"','\\\"') + '\n')
            processed_games.add(name)


print(f"Lookup table with unique game names written to {output_file_path}")


