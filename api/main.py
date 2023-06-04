"""Main file for the project."""

import os
import configparser
import news
import stock
from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
scheduler = BackgroundScheduler(daemon=True)

stock = stock.Stock()
news = news.News(stock.get_companies_tickers())

# ==============================================================================
def update_data():
    """Update the stock data."""
    stock.save_previous_closings()
    stock.save_current_prices()
    news.save_news()
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
        # read the API key from config.ini
        config = configparser.ConfigParser()
        config.read("api/config.ini")
        api_token = config["API"]["API_TOKEN"]
        # create a .env file and write the API token to it
        with open(".env", "w", encoding="utf-8") as file:
            file.write("MARKETAUX_API_TOKEN=" + api_token)


if __name__ == "__main__":
    main()
    scheduler.add_job(func=update_data, trigger="interval", seconds=30)
    
    scheduler.start()
    app.run()
