import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv("ML_MODEL_URL")
token = os.getenv("ML_TOKEN")

def optimize_query(text):
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are a news analyzer. Process short news snippets (minimum 10-15 words) and return a Python dict with the following keys: 'breaking' (string - compelling headline if it's breaking news, None otherwise), 'summary' (string - exactly 20-30 words overview), 'description' (string - exactly 60-100 words detailed explanation). Return ONLY the Python dict, nothing else."
            },
            {
                "role": "user",
                "content": text
            }
        ],
        "top_p": 0.9
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        result = response.json()
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }