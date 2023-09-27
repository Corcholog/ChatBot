import pandas as pd
import graphviz
from sklearn.tree import DecisionTreeClassifier
from sklearn import tree
from sklearn.preprocessing import MultiLabelBinarizer

df = pd.read_csv('C:/Users/logue/OneDrive/Escritorio/ChatBot/Explo/Recommendation/train_data.csv')
#print(df)

df = df.drop('game', axis='columns')

# separate genre list in columns for each genre
df['genres'] = df['genres'].str.split(',')
df['developer'] = df['developer'].str.split(',')

# one-hot encode the genres and developers
mlb = MultiLabelBinarizer()
mlb2 = MultiLabelBinarizer()

devs_encoded = mlb2.fit_transform(df['developer'])
genres_encoded = mlb.fit_transform(df['genres'])
devs_df = pd.DataFrame(devs_encoded, columns=mlb2.classes_)
genres_df = pd.DataFrame(genres_encoded, columns=mlb.classes_)

# Concatenate the one-hot encoded genres with the dataframe
df = pd.concat([df, genres_df], axis=1)
df = pd.concat([df, devs_df], axis=1)

# erase the original genres and developer columns
df = df.drop(columns=['genres'])
df = df.drop(columns=['developer'])

# onehot encode
df = pd.get_dummies(data=df, drop_first=True)
print(df)

y = df['likes']
x = df.drop('likes', axis='columns')

print(x.info())

model = DecisionTreeClassifier(max_depth=3)

model.fit(x,y)

print(model.score(x,y))

print()

df_testing = pd.read_csv('C:/Users/logue/OneDrive/Escritorio/ChatBot/Explo/Recommendation/testing_data.csv')

# separate genre list in columns for each genre, same for the developers
df_testing['genres'] = df_testing['genres'].str.split(',')
df_testing['developer'] = df_testing['developer'].str.split(',')

# one-hot encode the genres and developers
mlb_testing = MultiLabelBinarizer()
mlb2_testing = MultiLabelBinarizer()
devs_testing_encoded = mlb2_testing.fit_transform(df_testing['developer'])
genres_testing_encoded = mlb_testing.fit_transform(df_testing['genres'])
devs_df_testing = pd.DataFrame(devs_testing_encoded, columns=mlb2_testing.classes_)
genres_df_testing = pd.DataFrame(genres_testing_encoded, columns=mlb_testing.classes_)

# Concatenate the one-hot encoded genres with the dataframe
df_testing = pd.concat([df_testing, genres_df_testing], axis=1)
df_testing = pd.concat([df_testing, devs_df_testing], axis=1)

# erase the original genres and developer columns
df_testing = df_testing.drop(columns=['genres'])
df_testing = df_testing.drop(columns=['developer'])

# onehot encode the other columns/features
df_testing = pd.get_dummies(data=df_testing, drop_first=True)

# i need the missing features because the game to predict won't have all genres and developers.
training_features = list(x.columns)

# if a feature is missing, i put a zero
for feature in training_features:
    if feature not in df_testing.columns:
        df_testing[feature] = 0

# if i have a new genre or developer that is not in the trained model i erase it. (I didn't test what could happen if the testing data does not match the required columns)
for feature in df_testing.columns:
    if feature not in training_features:
        df_testing = df_testing.drop(columns=[feature])

df_testing = df_testing[training_features]
result = model.predict(df_testing)
print(model.predict(df_testing)) 



dot_data = tree.export_graphviz(model, out_file=None, 
                        feature_names=x.columns.tolist(), 
                        class_names=df['likes'].astype(str).unique().tolist(),
                        filled=True, rounded=True, 
                        special_characters=True)

graph = graphviz.Source(dot_data)
graph.render("arbolPreview")