"""A setup file for the project."""
import os
import json

def save_firebase_creds():
    """Convert the JSON file to a dictionary and save it as an environment variable."""
    # check if the service account key exists
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

    # convert the JSON file to a dictionary
    with open("serviceAccountKey.json", "r", encoding="utf-8") as file:
        creds = json.load(file)

    # open the .env file and append the FIREBASE_CREDS variable
    with open(".env", "a", encoding="utf-8") as file:
        file.write(f"\nFIREBASE_CREDS={json.dumps(creds)}")

save_firebase_creds()
