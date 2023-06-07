"""Main file for the project."""

import os
from flask import Flask, render_template
import data.data as data
import data.stock as stock
import data.news as news

app = Flask(__name__)

data = data.Data()  # this is where all the data is stored
stock = stock.Stock(data)
news = news.News(data)

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


@app.route("/api/stock_data")
def get_stock_data():
    """Return company info, ticker, previous closing prices, and current prices."""

    update_stock_data()

    response = {
        "previous_closings_date_logged": str(data.closings_date_logged),
        "current_prices_date_logged": str(data.current_prices_date_logged)
    }

    for ticker in data.tickers:
        response[ticker] = {
            "company": data.companies[ticker],
            "previous_closing_price": data.previous_closing[ticker], 
            "closings": {},
            "current_closing_date": str(data.closings_company_date_logged[ticker]),
            "current_price": data.current_prices[ticker],
            "change": stock.get_stock_change(ticker)
        }
        for closing in data.closings[ticker]:
            # assign the date as the key and the closing price as the value
            response[ticker]["closings"][closing[0]] = closing[1]

    return response


def main():
    """Main function."""
    # check if .env exists
    if not os.path.exists(".env"):
        # throw an error
        raise FileNotFoundError("""The .env file does not exist.
                                Create the .env file and add the following:
                                \nMARKETAUX_API_TOKEN=your_api_token""")


if __name__ == "__main__":
    main()
    update_stock_data()  # update the stock data when the server starts
    app.run()
