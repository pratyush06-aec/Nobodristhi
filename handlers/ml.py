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
    

def update_query(text, breaking, summary, description):
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are a news analyzer. Process short news snippets (minimum 10-15 words) and return a Python dict with the following keys: 'breaking' (string - compelling headline if it's breaking news, None otherwise), 'summary' (string - exactly 20-30 words overview), 'description' (string - exactly 60-100 words detailed explanation). Return ONLY the Python dict, nothing else."
            },
            {
                "role": "user",
                "content": f"Update analysis based on new text. Existing values: breaking='{breaking}', summary='{summary}', description='{description}'. New text: {text}. Please regenerate the breaking, summary, and description."
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
    

def check_similarity(text1, text2):
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are a news similarity analyzer. Compare two news snippets and determine if they are similar or about the same topic. Return ONLY a Python dict with one key: 'is_similar' (boolean - True if the texts are similar or about the same news topic, False otherwise). Return ONLY the Python dict, nothing else."
            },
            {
                "role": "user",
                "content": f"Compare these two texts:\n\nText 1: {text1}\n\nText 2: {text2}\n\nAre they similar or about the same topic?"
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
        
        # Parse result and return boolean
        if isinstance(result, dict) and 'is_similar' in result:
            return bool(result['is_similar'])
        elif isinstance(result, str):
            # Try parsing if it's a string representation of a dict
            parsed = json.loads(result)
            return bool(parsed.get('is_similar', False))
        else:
            return False
    except Exception as e:
        print(f"Error checking similarity: {e}")
        return False