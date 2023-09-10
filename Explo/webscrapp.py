from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

steamSearch = "https://store.steampowered.com/search/?term="

def search(gameName):
    gameName = gameName.replace(" ", "+")
    strToSearch = "god+of+war"
    driver = webdriver.Firefox()
    driver.get(f"{strToSearch}")
    elem = driver.find_element(ByName, )
search("god of war")