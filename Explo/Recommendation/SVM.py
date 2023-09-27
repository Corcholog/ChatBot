import pandas as pd
from sklearn.preprocessing import StandardScaler, MultiLabelBinarizer
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import numpy as np



df = pd.read_csv('C:/Users/logue/OneDrive/Escritorio/ChatBot/Explo/Recommendation/train_data.csv')
print(df)

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

x_og = df.drop('likes', axis='columns')
x = x_og.values
y = df['likes']

# Scale features
scaler = StandardScaler()
x = scaler.fit_transform(x)

# Create and train the SVM model
clf = SVC(kernel='linear')  
clf.fit(x, y)

df_testing = pd.read_csv('C:/Users/logue/OneDrive/Escritorio/ChatBot/Explo/Recommendation/testing_data.csv')

# separate genre list in columns for each genre
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

# onehot encode
df_testing = pd.get_dummies(data=df_testing, drop_first=True)

# i need the missing features because the game to predict won't have all genres and developers.
training_features = list(x_og.columns)

# if a feature is missing, y put a zero
for feature in training_features:
    if feature not in df_testing.columns:
        df_testing[feature] = 0

# if i have a new genre or developer that is not in the trained model i erase it.
for feature in df_testing.columns:
    if feature not in training_features:
        df_testing = df_testing.drop(columns=[feature])

# Scale features
df_testing = df_testing[training_features]
scaler = StandardScaler()
df_testing = scaler.fit_transform(df_testing)


pred = clf.predict(df_testing)
print(pred)


#Realiza predicciones con los datos de entrenamiento
#y_pred_train = clf.predict(x)

#Calcula la precisión
#accuracy_train = accuracy_score(y, y_pred_train)
#print(f"Training Accuracy: {accuracy_train:.2f}")