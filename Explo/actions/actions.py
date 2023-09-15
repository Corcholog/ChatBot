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

class getGameLink(Action):
    def name(self) -> Text:
        return "get_link"
    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_to_search = next(tracker.get_latest_entity_values("game_name"), None)

        url = webscrapp.get_game_link(game_to_search)
        
        dispatcher.utter_message(text=f"The link for: {game_to_search} is {url}")
        

class TopGamesQuery(Action):
    def name(self) -> Text:
        return "top_games_query"
    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #start_time = time.time()
        with PrologMQI(port=8000) as mqi:
            with mqi.create_thread() as prolog_thread:
                prolog_thread.query(consult_path) 
                N = 10 # proximamente será un input obtenido del tracker ig
                response = prolog_thread.query(f"top_10_ranking(Top10, {N})")
                dispatcher.utter_message(text=f"The top 10 games by score are:")
                dispatcher.utter_message(text="\n")

                for entry in response:
                    for game_info in entry['Top10']:
                        game_name, score = game_info
                        formatted_entry = f"{game_name}, score: {score}"
                        dispatcher.utter_message(text=f"{formatted_entry}")
                        dispatcher.utter_message(text="\n")

                #end_time = time.time()
                #elapsed_time = end_time - start_time
                #dispatcher.utter_message(text=f"Elapsed time inside of the query: {elapsed_time} seconds")

        return []

class TopGamesByGenre(Action): # tengo q controlar que si el resultado es [] me avise q no hay de tal genero.
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

""" ES RE DIFICIL ESTO XD
class TopGamesByDeveloper(Action):
    def name(self) -> Text:
        return "top_games_by_dev"
    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        with PrologMQI(port=8000) as mqi:
            with mqi.create_thread() as prolog_thread:
                prolog_thread.query(consult_path)
                dev = "BethesdaGameStudios" # proximamente será un input obtenido del tracker ig 
                response = prolog_thread.query(f"top_10_dev(Top10, {dev})")
                dispatcher.utter_message(text=f"The top 10 games of {dev} are:")
                dispatcher.utter_message(text="\n")

                for entry in response:
                    for game_info in entry['Top10']:
                        game_name, score = game_info
                        formatted_entry = f"{game_name}, score: {score}"
                        dispatcher.utter_message(text=f"{formatted_entry}")
                        dispatcher.utter_message(text="\n")

        return []

class ActionSessionStart(Action):
    def name(self) -> Text:
        return "action_session_start"

    async def run(
      self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_iamabot")
        return [SessionStarted(), ActionExecuted("action_listen")]
"""
