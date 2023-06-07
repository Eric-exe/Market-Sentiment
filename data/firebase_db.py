"""This file connects to the Firebase database and saves the data to Firebase realtime database."""

import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

class FirebaseDB:
    """The class for connecting to and accessing the Firebase database."""
    def __init__(self):
        """Initialize the FirebaseDB class."""
        load_dotenv()
        cred = credentials.Certificate(json.loads(os.getenv("FIREBASE_CREDS")))

        # initialize the app with a service account, granting admin privileges
        firebase_admin.initialize_app(cred, {
            'databaseURL': os.getenv("FIREBASE_DB_URL")
        })

        # get a reference to the database service
        self.db_ref = db.reference()

    def update_stock_data(self, data):
        """Update the stock data in the Firebase database."""
        self.db_ref.update({"stock_data" : data})

    def get_stock_meta(self):
        """Get the stock metadata from the Firebase database."""
        return self.db_ref.child("stock_data").child("meta").get()

    def get_stock_data(self):
        """Get the stock data from the Firebase database."""
        return self.db_ref.child("stock_data").child("data").get()
