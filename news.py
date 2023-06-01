"""This file processes the news data and saves it to a JSON file."""

# API: https://newsapi.org/docs/get-started

import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

API_TOKEN = None
COMPANIES = None

def news_init(companies):
    """Initialize the news data."""
    global COMPANIES
    COMPANIES = companies

    load_dotenv()
    global API_TOKEN
    API_TOKEN = os.getenv("MARKETAUX_API_TOKEN")

def get_news(company_name):
    """Return the news data for said company."""
    pass
    
