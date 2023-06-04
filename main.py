"""Main file for the project."""

import os
import configparser
from flask import Flask, render_template

app = Flask(__name__)

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
        config.read("config.ini")
        api_token = config["API"]["API_TOKEN"]
        # create a .env file and write the API token to it
        with open(".env", "w", encoding="utf-8") as file:
            file.write("MARKETAUX_API_TOKEN=" + api_token)


if __name__ == "__main__":
    main()
    app.run()