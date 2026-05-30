import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

URL = os.getenv("SEARCH_ENDPOINT")
CODE = os.getenv("SEARCH_CODE")



def search_image(query):
    payload = {
        "Query": query,
        "AccessCode": CODE
    }
    try:
        response = requests.post(f"{URL}/api/search", json=payload)
        if response.status_code == 200:
            result = response.json()
            return result if isinstance(result, list) else []
        else:
            return []
    except Exception as e:
        return []