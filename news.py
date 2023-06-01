"""This file processes the news data and saves it to a JSON file."""

# API: https://www.marketaux.com/documentation

import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta

API_TOKEN = None

def news_init():
    """Initialize the news data."""

    load_dotenv()
    global API_TOKEN
    API_TOKEN = os.getenv("MARKETAUX_API_TOKEN")

def get_news(ticker):
    """Return the news data for said company."""

    if (API_TOKEN is None):
        news_init()
    # build the request
    url = "https://api.marketaux.com/v1/news/all?" + \
          "symbols=" + ticker + \
          "&filter_entities=true" + \
          "&api_token=" + API_TOKEN
    
    print(url)
    # send the request
    # response = requests.get(url)
