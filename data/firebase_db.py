"""This file connects to the Firebase database and saves the data to Firebase realtime database."""

import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

class FirebaseDB:
    """The class for connecting to and accessing the Firebase database."""
    def __init__(self):
        """Initialize the FirebaseDB class."""
        load_dotenv()

        # check if serviceAccountKey.json exists
        if not os.path.exists("serviceAccountKey.json"):
            # throw an error
            raise FileNotFoundError(
            """The serviceAccountKey.json file does not exist. Create the serviceAccountKey.json file:\n
            1. Go to the Firebase console\n
            2. Click on the project\n
            3. Click on the gear icon and select Project Settings\n
            4. Click on the Service Accounts tab\n
            5. Click on the Generate new private key button\n
            6. Rename the downloaded JSON file to serviceAccountKey.json\n
            7. Place the serviceAccountKey.json file in the root directory of the project."""
            )

        cred = credentials.Certificate("serviceAccountKey.json")

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
