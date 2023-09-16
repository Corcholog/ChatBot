from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SessionStarted, ActionExecuted
from swiplserver import PrologMQI
from bs4 import BeautifulSoup
import requests
import time
import webscrapp
import re

consult_path = "consult('C:/Users/logue/OneDrive/Escritorio/ChatBot/Explo/knowledge_db.pl')"

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
                dispatcher.utter_message(text="\n")
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
                dispatcher.utter_message(text="\n")

                for entry in response:
                    for game_info in entry['Top10']:
                        game_name, score = game_info
                        formatted_entry = f"{game_name}, score: {score}"
                        dispatcher.utter_message(text=f"{formatted_entry}")
                        dispatcher.utter_message(text="\n")

                # end_time = time.time()
                # elapsed_time = end_time - start_time
                # dispatcher.utter_message(text=f"Elapsed time inside of the query: {elapsed_time} seconds")

        return []

class TopGamesByGenre(Action): 
    def name(self) -> Text:
        return "top_games_by_genre"
    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        with PrologMQI(port=8000) as mqi:
            with mqi.create_thread() as prolog_thread:
                prolog_thread.query(consult_path)
                genre = next(tracker.get_latest_entity_values("genre_type"), None)
                response = prolog_thread.query(f"top_10_genre(Top10,'{genre}')")
                dispatcher.utter_message(text=f"The top 10 games of {genre} are:")
                dispatcher.utter_message(text="\n")

                for entry in response:
                    for game_info in entry['Top10']:
                        game_name, score = game_info
                        formatted_entry = f"{game_name}, score: {score}"
                        dispatcher.utter_message(text=f"{formatted_entry}")
                        dispatcher.utter_message(text="\n")

        return []

