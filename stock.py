"""This file gets the stock information from the API yfinance and saves it to a CSV file."""

import os
from datetime import datetime
import yfinance as yf
import data

COMPANIES = None
COMPANY_STATS = None
DATE = None

# ==================================================================================================

def get_stock_info(ticker):
    """Return the stock information from the API."""
    return yf.Ticker(ticker).info

def get_stock_price(info):
    """Return the stock price from the API."""
    return info["currentPrice"]

def get_stock_previous_close(info):
    """Return the stock previous close from the API."""
    return info["previousClose"]

def get_stock_change(info):
    """Return the stock change percentage from the API."""
    return round((get_stock_price(info) - get_stock_previous_close(info)) / get_stock_previous_close(info) * 100, 2)

def get_five_day_stock_change(info):
    """Return the stock change percentage from the COMPANY_STATS if applicable. Else, return -1."""
    current_price = get_stock_price(info)
    previous_closings = COMPANY_STATS[info["symbol"]]
    if (len(previous_closings) == 5):
        previous_closing = previous_closings[0]
        return round((current_price - previous_closing) / previous_closing * 100, 2)
    return -1    

# ==================================================================================================

def get_companies():
    """Return the company data."""
    global COMPANIES
    COMPANIES = data.load_companies()

    global COMPANY_STATS
    COMPANY_STATS = {}

def save_previous_closing():
    """Save the previous closing prices of the companies."""

    # check if we already have logged the previous closing prices
    # read date from file "data/date" and compare to today's date

    # if file does not exist, create it and write today's date
    DATE = str(datetime.today().date())

    if (not os.path.isfile("data/date")):
        with open("data/stock/date", "w", encoding="utf-8") as file:
            file.write(DATE)

    # if file exists, read the date and compare to today's date
    else:
        with open("data/stock/date", "r", encoding="utf-8") as file:
            date = file.read()
            if date == DATE:
                # save stats to COMPANY_STATS
                with open("data/stock/previous_closings.csv", "r", encoding="utf-8") as file:
                    previous_closing_data = data.read_csv("data/stock/previous_closings.csv")
                    previous_closing_data.pop(0)
                    for company in previous_closing_data:
                        ticker = company[1]
                        COMPANY_STATS[ticker] = company[2:]
                return
            
            else:
                # update the date
                with open("data/stock/date", "w", encoding="utf-8") as file:
                    file.write(DATE)

    # read the previous closing prices from the CSV file
    previous_closing_prices = data.load_previous_closings()

    for company in COMPANIES:
        ticker = COMPANIES[company]
        info = get_stock_info(ticker)
        # if the company is not in the dictionary, add it
        if company not in previous_closing_prices:
            previous_closing_prices[company] = []
        previous_closing_prices[company].insert(0, get_stock_previous_close(info))
        # if the list has more than 5 elements, remove the last element
        if len(previous_closing_prices[company]) > 5:
            previous_closing_prices[company].pop()

    # save the previous closing prices to the CSV file
    header = ["Company",
              "Ticker", 
              "Previous Close 1", 
              "Previous Close 2", 
              "Previous Close 3", 
              "Previous Close 4", 
              "Previous Close 5"]
    # turn the dictionary into a list
    previous_closing_prices_list = []
    for company in previous_closing_prices:
        ticker = COMPANIES[company]
        previous_closing_prices_list.append([company,ticker] + previous_closing_prices[company])
        # save to COMPANY_STATS
        COMPANY_STATS[ticker] = previous_closing_prices[company]

    data.save_data("data/stock/previous_closings.csv", header, previous_closing_prices_list)

def company_init():
    """Initialize the companies' data."""
    get_companies()
    save_previous_closing()

company_init()