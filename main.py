"""Main file for the project."""

import os
from dotenv import load_dotenv

import yfinance as yf
load_dotenv()
newsAPIKey = os.getenv("NEWS_API_KEY")

msft = yf.Ticker("GOOG")
print(msft.info)
