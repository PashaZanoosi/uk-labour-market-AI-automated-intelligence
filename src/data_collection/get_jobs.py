import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")


url = "https://api.adzuna.com/v1/api/jobs/gb/search/1"

params = {
    "app_id": APP_ID,
    "app_key": APP_KEY,
    "results_per_page": 50,
    "sort_by": "date"
}


response = requests.get(url, params=params)


if response.status_code == 200:

    data = response.json()

    print("Jobs collected:", len(data["results"]))


    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"data/raw/jobs_{timestamp}.json"


    with open(filename, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )


    print(f"Saved: {filename}")


else:
    print("API Error")
    print(response.text)