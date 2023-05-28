"""The Python file for reading the CSV files and writing down information."""

import csv
import os

def read_csv(filename):
    """Return the contents of the CSV file if it exists. Else, return an empty list."""
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            return list(reader)
    return []
    
def load_companies():
    """Return the companies from the CSV file and return it as a dictionary."""
    companies = read_csv("data/companies.csv")
    companies.pop(0)
    companies = {company[0] : company[1] for company in companies}
    return companies

def load_previous_closings():
    """Return the previous closing prices from the CSV file and return it as a dictionary."""
    previous_closings = read_csv("data/previous_closings.csv")
    previous_closings.pop(0)
    previous_closings = {company[0] : company[2:] for company in previous_closings}
    return previous_closings

def save_data(filename, header, data):
    """Save the data to the CSV file."""
    with open(filename, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)
        file.close()