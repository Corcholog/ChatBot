from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SessionStarted, ActionExecuted
from swiplserver import PrologMQI
from sklearn.tree import DecisionTreeClassifier
from sklearn import tree
from sklearn.preprocessing import MultiLabelBinarizer
import graphviz
import pandas as pd
import time
import webscrapp
import psycopg2
import csv
from .profile import addGame

# Database connection parameters
params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '2108',
    'host': 'localhost',  # or the IP address of your PostgreSQL server
    'port': '5432'  # default port for PostgreSQL
}

# Knowledge database 
consult_path = "consult('C:/Users/logue/OneDrive/Escritorio/ChatBot/Explo/knowledge_db.pl')"

# Decission Tree Model Initialization
df = pd.read_csv('C:/Users/logue/OneDrive/Escritorio/ChatBot/Explo/UserProfile/gamesInfo.csv')

processed_games = set(df['game'])
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

model = DecisionTreeClassifier(max_depth=3)

model.fit(x,y)

def getDataFrame(game_name) -> pd.DataFrame:
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    game_info = "SELECT ge.genre_name, d.dev_name, g.score FROM GAME g JOIN WAS_DEV wd ON g.name = wd.game_name JOIN DEVELOPER d on wd.dev_id = d.dev_id JOIN HAS_GENRE hg on wd.game_name = hg.game_name JOIN GENRE ge on ge.genre_id = hg.genre_id WHERE g.name = %s"
    cur.execute(game_info, (game_name,))
    result = cur.fetchall()
    genres = set()
    devs = set()
    score = result[0][2]
    for row in result:
        genres.add(row[0])
        devs.add(row[1])
    str_genres = ','.join(genres)
    str_devs = ','.join(devs)


    to_predict = f'{game_name},"{str_genres}","{str_devs}",{score}'

    # Use the csv.reader to split the string
    parsed_data = list(csv.reader([to_predict]))[0]

    predict_df = pd.DataFrame([parsed_data], columns=['game', 'genres', 'developer', 'score'])

    # separate genre list in columns for each genre, same for the developers
    predict_df['genres'] = predict_df['genres'].str.split(',')
    predict_df['developer'] = predict_df['developer'].str.split(',')

    # one-hot encode the genres and developers
    mlb_testing = MultiLabelBinarizer()
    mlb2_testing = MultiLabelBinarizer()
    devs_testing_encoded = mlb2_testing.fit_transform(predict_df['developer'])
    genres_testing_encoded = mlb_testing.fit_transform(predict_df['genres'])
    devs_predict_df = pd.DataFrame(devs_testing_encoded, columns=mlb2_testing.classes_)
    genres_predict_df = pd.DataFrame(genres_testing_encoded, columns=mlb_testing.classes_)

    # Concatenate the one-hot encoded genres with the dataframe
    predict_df = pd.concat([predict_df, genres_predict_df], axis=1)
    predict_df = pd.concat([predict_df, devs_predict_df], axis=1)

    # erase the original genres and developer columns
    predict_df = predict_df.drop(columns=['genres'])
    predict_df = predict_df.drop(columns=['developer'])

    # onehot encode the other columns/features
    predict_df = pd.get_dummies(data=predict_df, drop_first=True)

    # i need the missing features because the game to predict won't have all genres and developers.
    training_features = list(x.columns)

    # if a feature is missing, i put a zero
    for feature in training_features:
        if feature not in predict_df.columns:
            predict_df[feature] = 0

    # if i have a new genre or developer that is not in the trained model i erase it. (I didn't test what could happen if the testing data does not match the required columns)
    for feature in predict_df.columns:
        if feature not in training_features:
            predict_df = predict_df.drop(columns=[feature])

    predict_df = predict_df[training_features]
    conn.commit()
    cur.close()
    conn.close()
    return predict_df

class PredictGame(Action):
    def name(self) -> Text:
        return "predict_game"
    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_name = next(tracker.get_latest_entity_values("game_name"), None)
        result = model.predict(getDataFrame(game_name))

        if result[0] == 1:
            dispatcher.utter_message("You'll like it")
        else:
            dispatcher.utter_message("You won't like it")

class UpdateProfile(Action):
    def name(self) -> Text:
        return "update_profile"
    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_name = next(tracker.get_latest_entity_values("game_name"), None)

        if game_name is not None:
            if not game_name in processed_games:
                last_intent = tracker.get_intent_of_latest_message()
                processed_games.add(game_name)
                if last_intent == "likes_game":
                    addGame(game_name,1)
                    dispatcher.utter_message(response="utter_likes_game")

                elif last_intent == "dislikes_game":
                    addGame(game_name,0)
                    dispatcher.utter_message(response="utter_dislikes_game")
            else: # TO-DO: Check if intent = likes_game AND game was disliked, change that value. Same or intent dislikes and game was liked (update user taste)
                dispatcher.utter_message("We already knew owo")
            
        else:
            dispatcher.utter_message("I didn't understand which game you like")

class GetNews(Action):
    def name(self) -> Text:
        return "get_news"
    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        news = webscrapp.eng_news()
        if (len(news) == 0) or (news is None):
            news = webscrapp.esp_news()
        if (len(news) > 0):
            n = 1
            for new in news:
                dispatcher.utter_message(text=f"{n}. {new}")
                #dispatcher.utter_message(text="\n")
                n = n + 1
        else:
            dispatcher.utter_message(text=f"I can't find the news. Server is probably over maintenance.")

class GetSynopsis(Action):
    def name(self) -> Text:
        return "get_synopsis"
    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_to_search = next(tracker.get_latest_entity_values("game_name"), None)
        if game_to_search is not None:
            synopsis = webscrapp.get_game_synopsis(game_to_search)
            if synopsis is not None:
                dispatcher.utter_message(text=f"Here you have the synopsis:")
                dispatcher.utter_message(text=f"{synopsis}")
            else:
                dispatcher.utter_message(response="utter_there_is_no_link")
        else:
            dispatcher.utter_message(response="utter_there_is_no_link")

class GetGameLink(Action):
    def name(self) -> Text:
        return "get_link"
    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_to_search = next(tracker.get_latest_entity_values("game_name"), None)
        if game_to_search is not None:
            url = webscrapp.get_game_link(game_to_search)
            if url is not None:
                dispatcher.utter_message(response="utter_give_link")
                dispatcher.utter_message(text=f"{url}")
            else:
                dispatcher.utter_message(response="utter_there_is_no_link")
        else:
            dispatcher.utter_message(response="utter_there_is_no_link")

class TopGames(Action):
    def name(self) -> Text:
        return "top_games_query"
    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # start_time = time.time()
        with PrologMQI(port=8000) as mqi:
            with mqi.create_thread() as prolog_thread:
                prolog_thread.query(consult_path) 
                N = 10
                response = prolog_thread.query(f"top_10_ranking(Top10, {N})")
                dispatcher.utter_message(text=f"The top 10 games by score are:")
                for entry in response:
                    for game_info in entry['Top10']:
                        game_name, score = game_info
                        formatted_entry = f"{game_name}, score: {score}"
                        dispatcher.utter_message(text=f"{formatted_entry}")
                # end_time = time.time()
                # elapsed_time = end_time - start_time
                # dispatcher.utter_message(text=f"Elapsed time inside of the query: {elapsed_time} seconds")
        return []

class TopGamesByGenre(Action): 
    def name(self) -> Text:
        return "top_games_by_genre"
    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #start_time = time.time()
        genre = next(tracker.get_latest_entity_values("genre_type"), None)
        if genre is not None:
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            fetch_games = "SELECT GAME.name, MAX(GAME.score) as maxscore FROM GAME join HAS_GENRE on GAME.name = HAS_GENRE.game_name join GENRE ON HAS_GENRE.genre_id = GENRE.genre_id WHERE GENRE.genre_name = %s GROUP BY name, score ORDER BY score DESC LIMIT 10"
            cur.execute(fetch_games, (genre,))
            result = cur.fetchall()
            dispatcher.utter_message(text=f"The top 10 games of {genre} are:")    
            for row in result:
                dispatcher.utter_message(text=f"{row[0]} with a score of: {row[1]}")
            conn.commit()
            cur.close()
            conn.close()
            
        else:
            dispatcher.utter_message("Sorry but i didn't understand which genre are you looking for.")
        #end_time = time.time()
        #elapsed_time = end_time - start_time
        #dispatcher.utter_message(text=f"Elapsed time of Action: {elapsed_time} seconds")
        return []

'''     PROLOG VERSION
class TopGamesByGenre(Action): 
    def name(self) -> Text:
        return "top_games_by_genre"
    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        start_time = time.time()
        with PrologMQI(port=8000) as mqi:
            with mqi.create_thread() as prolog_thread:
                prolog_thread.query(consult_path)
                genre = next(tracker.get_latest_entity_values("genre_type"), None)
                if genre is not None:
                    dispatcher.utter_message(response="utter_on_it")
                    response = prolog_thread.query(f"top_10_genre(Top10,'{genre}')")
                    
                    dispatcher.utter_message(text=f"The top 10 games of {genre} are:")

                    if response is not None:
                        
                        for entry in response:
                            for game_info in entry['Top10']:
                                game_name, score = game_info
                                dispatcher.utter_message(text=f"{game_name}, score: {score}")
                        
                    else:
                        dispatcher.utter_message("Sorry but i didn't understand which genre are you looking for.")
                else:
                    dispatcher.utter_message("Sorry but i didn't understand which genre are you looking for.")
        end_time = time.time()
        elapsed_time = end_time - start_time
        dispatcher.utter_message(text=f"Elapsed time inside of the query: {elapsed_time} seconds")
        return []
'''
'''
dot_data = tree.export_graphviz(model, out_file=None, 
                        feature_names=x.columns.tolist(), 
                        class_names=df['likes'].astype(str).unique().tolist(),
                        filled=True, rounded=True, 
                        special_characters=True)

graph = graphviz.Source(dot_data)
graph.render("arbolPreview")

'''
