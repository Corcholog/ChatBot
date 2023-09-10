import pandas as pd
import warnings
import csv
import re
from sklearn.preprocessing import LabelEncoder
from sklearn import tree


warnings.filterwarnings("ignore", category=UserWarning)
#filename = "C:/Users/logue/OneDrive/Escritorio/Explo/games-data.csv"

df = pd.read_csv("C:/Users/logue/OneDrive/Escritorio/ChatBot/Explo/decission_tree/train_data.csv")
print(df.head())


le_genres = LabelEncoder()
le_Developer = LabelEncoder()
le_score = LabelEncoder()

inputs = df.drop('likes',axis='columns')
inputs = df.drop('game',axis='columns')
target = df['likes']


inputs['genres_n'] = le_genres.fit_transform(inputs['genres'])
inputs['developer_n'] = le_Developer.fit_transform(inputs['developer'])
inputs['score_n'] = le_score.fit_transform(inputs['score'])


inputs_n = inputs.drop(['genres','developer', 'score', 'likes'],axis='columns')

print(inputs_n)
print(target)

model = tree.DecisionTreeClassifier()

model.fit(inputs_n, target)

print(model.score(inputs_n,target))

print("le gustará un juego del genero 'Role-Playing, Western-Style', del dev Nintendo y de score 3?") 
print(f"El resultado de la predicción es: {model.predict([[4,1,3]])}")
print()

print("le gustará un juego del genero 'Role-Playing, First-Person, General, Western-Style', del dev Bethesda y de score 0?") 
print(f"El resultado de la predicción es: {model.predict([[3,0,0]])}")
print()

print("le gustará un juego del genero 'Action Adventure,Open-World', del dev Nintendo y de score 4?") 
print(f"El resultado de la predicción es: {model.predict([[1,1,4]])}")

"""
rows = []
games = []
with open(filename, 'r') as csvfile:
    csvreader = csv.reader(csvfile) # abro en modo READ
    le = LabelEncoder()
    fields = next(csvreader) #como la primer fila son los nombres de los campos, los guardo iterando.

    for row in csvreader: # leo todas las filas
        rows.append(row)
        games.append(row[0])
        enc_genres = row[6]
        enc_developer = row[5]
        enc_score = row[3]
        le.fit([enc_genres, enc_developer, enc_score])
        le.transform()

"""


