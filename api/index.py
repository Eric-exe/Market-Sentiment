"""Main file for the project."""

import os
from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
import yfinance as yf
import data.data as data
import data.stock as stock
import data.news as news

app = Flask(__name__)
scheduler = BackgroundScheduler()

data = data.Data()  # this is where all the data is stored
stock = stock.Stock(data)
news = news.News(data)

# ==============================================================================
def update_data():
    """Update the stock data."""
    stock.save_previous_closings()
    stock.save_current_prices()
    # news.save_news()

update_data() # update the data when the server starts
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
    companies = data.companies
    tickers = data.tickers
    previous_closings = data.previous_closings
    current_prices = data.current_prices
    previous_closings_date_logged = data.previous_closings_date_logged
    current_prices_date_logged = data.current_prices_date_logged

    # format of the response:
    # {
    #    previous_closings_date_logged: date,
    #    current_prices_date_logged: date,
    #    "ticker": {
    #       "company": "company name",
    #       "previous_closings": [previous closing prices],
    #       "current_price": current price,
    #       "change": change,
    #       "five_day_change": five day change
    #    }
    # }

    response = {
        "previous_closings_date_logged": str(previous_closings_date_logged),
        "current_prices_date_logged": str(current_prices_date_logged)
    }
    
    for ticker in tickers:
        response[ticker] = {
            "company": companies[ticker],
            "previous_closings": previous_closings[ticker],
            "current_price": current_prices[ticker],
            "change": stock.get_stock_change(ticker),
            "change_five_day": stock.get_five_day_stock_change(ticker)
        }

    return response

# ==============================================================================

def main():
    """Main function."""
    # check if .env exists
    if not os.path.exists(".env"):
        # throw an error
        raise FileNotFoundError("""The .env file does not exist.
                                Create the .env file and add the following:
                                \nMARKETAUX_API_TOKEN=your_api_token""")

# run update_data() every 10 minutes
scheduler.add_job(func=update_data, trigger="interval", minutes=10)
scheduler.start()

if __name__ == "__main__":
    main()
    app.run()
