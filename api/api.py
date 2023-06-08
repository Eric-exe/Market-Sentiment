"""Main file for the API."""

import os
import json
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
# ==============================================================================


def update_stock_data():
    """Update the stock data."""
    # TODO: check if the data is recent so that we don't have to update it every time the API is called
    stock.load_stock_data(db)
    stock.save_closings_prices()
    stock.save_current_prices()

# ==============================================================================

@api_bp.route("/stock_data", methods=["GET"])
def get_stock_data():
    """Return company info, ticker, previous closing prices, and current prices."""

    request_time = str(datetime.today().now())
    update_stock_data()

    response = stock.get_stock_data(request_time)
    # update firebase db
    db.update_stock_data(response)

    return Response(json.dumps(response), mimetype="application/json")

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
    