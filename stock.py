"""This file gets the stock information from the API yfinance and saves it to a CSV file."""

from datetime import datetime
import yfinance as yf
import data

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

# ==================================================================================================

COMPANIES = None

def get_companies():
    """Return the company data."""
    global COMPANIES
    COMPANIES = data.load_companies()

def save_previous_closing():
    """Save the previous closing prices of the companies."""

    # check if we already have logged the previous closing prices
    # read date from file "data/date" and compare to today's date
    with open("data/date", "r", encoding="utf-8") as file:
        date = file.read()
        if date == str(datetime.today().date()):
            return
        else:
            # update the date
            with open("data/date", "w", encoding="utf-8") as file:
                file.write(str(datetime.today().date()))

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
        previous_closing_prices_list.append([company, COMPANIES[company]] + previous_closing_prices[company])

    data.save_data("data/previous_closings.csv", header, previous_closing_prices_list)

get_companies()
save_previous_closing()
