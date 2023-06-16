"""Main file for the API."""

import json
import threading
from datetime import datetime, timedelta
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

def update_stock_data(request_time):
    """Update the stock data."""
    response = None
    if not stock.load_stock_data(db):
        stock.save_closings_prices()
        stock.save_current_prices()

        # separate db update from the rest of the code
        # this is so that the stock data will only update when necessary
        response = stock.get_stock_data(request_time)
        db.update_stock_data(response)
    else:
        response = stock.get_stock_data(request_time)

    return response

def update_news_data():
    """Update the news data."""
    if not news.load_news_data(db): 
        with lock:
            # only one thread can update the news data at a time.
            # this saves API calls
            news.save_news(db) # save the news data to the database

# ==============================================================================

@api_bp.route("/stock_data", methods=["GET"])
def get_stock():
    """Return company info, ticker, previous closing prices, and current prices."""

    request_time = str(datetime.now())
    response = update_stock_data(request_time)

    return Response(json.dumps(response), mimetype="application/json")


@api_bp.route("/news_data", methods=["GET"])
def get_news():
    """Return the news data."""

    request_time = str(datetime.now())
    update_news_data()

    response = news.get_news_data(request_time)

    return Response(json.dumps(response), mimetype="application/json")
