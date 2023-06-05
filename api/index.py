"""Main file for the project."""

import os
from api.data import data
from api.data import stock
from api.data import news
from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler

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


def main():
    """Main function."""
    # check if .env exists
    if not os.path.exists(".env"):
        # throw an error
        raise FileNotFoundError("""The .env file does not exist.
                                Create the .env file and add the following:
                                \nMARKETAUX_API_TOKEN=your_api_token""")


if __name__ == "__main__":
    stock.save_previous_closings()
    print(data.previous_closings)
    main()
    scheduler.add_job(func=update_data, trigger="interval", seconds=10)
    scheduler.start()
    app.run()
