import pandas as pd
import warnings
from sklearn.preprocessing import LabelEncoder
from sklearn import tree
import graphviz

warnings.filterwarnings("ignore", category=UserWarning)

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

model = tree.DecisionTreeClassifier(max_depth=3)

model.fit(inputs_n, target)

print(model.score(inputs_n,target))

print("le gustará un juego del genero 'Role-Playing, Western-Style', del dev Nintendo y de score 3?") 
print(f"El resultado de la predicción es: {model.predict([[2,5,5]])}")
print()

print("le gustará un juego del genero 'Action', del dev RockstarNorth y de score 95?") 
print(f"El resultado de la predicción es: {model.predict([[0,7,4]])}")
print()

dot_data = tree.export_graphviz(model, 
                  feature_names=["genre","developer","score"],  
                  class_names=["Likes", "Not Likes"],  
                  filled=True, rounded=True,  
                  special_characters=True,
                   out_file=None,
                           )
graph = graphviz.Source(dot_data)

graph.format = "png"
graph.render("C:/Users/logue/OneDrive/Escritorio/ChatBot/Explo/decission_tree/file_name")