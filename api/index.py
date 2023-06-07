"""Main file for the project."""

import os
import json
from dotenv import load_dotenv
from flask import Flask, render_template, Response
import data.data as data
import data.stock as stock
import data.news as news
import data.firebase_db as firebase_db

app = Flask(__name__)

data = data.Data()  # this is where all the data is stored
stock = stock.Stock(data)
news = news.News(data)

db = firebase_db.FirebaseDB()
# ==============================================================================


def update_stock_data():
    """Update the stock data."""
    stock.save_closings_prices()
    stock.save_current_prices()

# ==============================================================================


@app.route("/")
def index():
    """Return the index page."""
    return render_template("index.html")


@app.route("/styles.css")
def styles():
    """Return the styles.css file."""
    return app.send_static_file("styles.css")


@app.route("/script.js")
def scripts():
    """Return the scrips.js file."""
    return app.send_static_file("script.js")
# ==============================================================================
# GET Requests


@app.route("/api/stock_data", methods=["GET"])
def get_stock_data():
    """Return company info, ticker, previous closing prices, and current prices."""
    update_stock_data()

    response = stock.get_stock_data()
    # update firebase db
    db.update_stock_data(response)

    return Response(json.dumps(response), mimetype="application/json")


def main():
    """Main function."""

    load_dotenv()
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


if __name__ == "__main__":
    main()
    update_stock_data()  # update the stock data when the server starts
    app.run()
