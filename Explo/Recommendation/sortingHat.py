import csv
import pandas as pd
from sklearn.preprocessing import StandardScaler, MultiLabelBinarizer
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import numpy as np
import graphviz
from sklearn.tree import DecisionTreeClassifier
from sklearn import tree

#initialize the models
model = DecisionTreeClassifier(max_depth=3)
clf = SVC(kernel='linear')



def sortingHat(user_path):
    user_path = 'C:/Users/Julian/Desktop/cork/Recommendation/15Games.csv'
    line_count = 0
    with open(user_path, 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            line_count += 1
    
    if line_count <= 7:
        # Decission Tree Model Initialization
        df = pd.read_csv(user_path)
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
        x = df.drop('likes', axis='columns') # Features
        y = df['likes'] # Target

        # Train the model
        model.fit(x,y)
        
        print("The model has been trained as a Decission Tree Classifier")

    else:
        df = pd.read_csv(user_path)
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

        # Train the SVM model
        clf.fit(x, y)
        print("The model has been trained as a Support Vector Machine Classifier")
sortingHat()