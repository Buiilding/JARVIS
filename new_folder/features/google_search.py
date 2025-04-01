from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re, pyttsx3
import requests
import webbrowser as web



def google_search(command):  # Parameter is the full command

    """Opens the first Google search result for the given topic, parsed from the command."""
    url = f'https://www.google.com/search?q={command}'
    # speak("Okay sir!")
    # speak(f"Searching Google for {topic}")
    web.open(url)  # Opens the URL in the default browser
    return url  # Return URL