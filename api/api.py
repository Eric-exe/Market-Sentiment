"""Main file for the API."""

import os
import json
import threading
from datetime import datetime
from flask import Blueprint, Response

from api.data import data
from api.data import stock
from api.data import news
from api.data import firebase_db

# create a api blueprint
api_bp = Blueprint("API", __name__)

data = data.Data()  # this is where all the data is stored
stock = stock.Stock(data)
news = news.News(data)

db = firebase_db.FirebaseDB()

lock = threading.Lock()
# ==============================================================================

def update_stock_data():
    """Update the stock data."""
    if not stock.load_stock_data(db):
        stock.save_closings_prices()
        stock.save_current_prices()

def update_news_data():
    """Update the news data."""
    if not news.load_news_data(db):
        with lock:
            # only one thread can update the news data at a time.
            # this saves API calls
            news.save_news(db)

# ==============================================================================

@api_bp.route("/stock_data", methods=["GET"])
def get_stock():
    """Return company info, ticker, previous closing prices, and current prices."""

    request_time = str(datetime.now())
    update_stock_data()

    response = stock.get_stock_data(request_time)
    # update firebase db
    db.update_stock_data(response)

    return Response(json.dumps(response), mimetype="application/json")

@api_bp.route("/news_data", methods=["GET"])
def get_news():
    """Return the news data."""

    request_time = str(datetime.now())
    update_news_data()

    response = news.get_news_data(request_time)

    return Response(json.dumps(response), mimetype="application/json")

# ==============================================================================
def main():
    """Main function."""
    # check if .env exists
    if not os.path.exists(".env"):
        # throw an error
        raise FileNotFoundError(
            """The .env file does not exist. Create the .env file and add the following:\n\n

            MARKETAUX_API_TOKEN=your_api_token\n
            FIREBASE_DB_URL=your_firebase_db_url\n\n

            To get the Marketaux API token, sign up at https://marketaux.com.\n\n

            To get the Firebase DB URL, sign up at https://firebase.google.com.\n
            Create a project and add a realtime database. Then, copy the URL of the realtime database.\n\n

            Place the .env file in the root directory of the project."""
        )
    