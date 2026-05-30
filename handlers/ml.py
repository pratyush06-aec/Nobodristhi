import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

TOKENS = []
TOKEN_INDEX = 0

def load_tokens():
    global TOKENS
    try:
        token_file = os.path.join(os.path.dirname(__file__), '..', 'tokens.json')
        with open(token_file, 'r') as f:
            token_data = json.load(f)
            TOKENS = [t['token'] for t in token_data]
    except Exception as e:
        TOKENS = []

load_tokens()

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODELS = [
    "openai/gpt-oss-120b:free",
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free"
]
MODEL_INDEX = 0

def get_next_token():
    """Get the next available token in rotation"""
    global TOKEN_INDEX
    if not TOKENS:
        return None
    token = TOKENS[TOKEN_INDEX]
    TOKEN_INDEX = (TOKEN_INDEX + 1) % len(TOKENS)
    return token

def get_next_model():
    """Get the next available model in rotation"""
    global MODEL_INDEX
    if not MODELS:
        return None
    model = MODELS[MODEL_INDEX]
    MODEL_INDEX = (MODEL_INDEX + 1) % len(MODELS)
    return model

def make_request(messages):
    attempts = 0
    max_attempts = len(TOKENS) * len(MODELS)
    first_attempt = True
    
    while attempts < max_attempts:
        attempts += 1
        token = get_next_token()
        model = get_next_model()
        
        if not token:
            return {
                "success": False,
                "error": "No tokens available"
            }
        
        if not model:
            return {
                "success": False,
                "error": "No models available"
            }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    return content
                return result
            else:
                continue
                
        except (requests.exceptions.Timeout, Exception):
            continue
    
    return {
        "success": False,
        "error": f"Failed after trying all {max_attempts} token/model combinations"
    }

def optimize_query(text):
    messages = [
        {
            "role": "system",
            "content": "You are a news analyzer. Process short news snippets (minimum 10-15 words) and return a Python dict with the following keys: 'breaking' (string - compelling headline), 'summary' (string - exactly 20-30 words overview), 'description' (string - exactly 60-100 words detailed explanation). Return ONLY the Python dict, nothing else."
        },
        {
            "role": "user",
            "content": text
        }
    ]
    
    try:
        result = make_request(messages)
        if isinstance(result, str):
            return json.loads(result)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def update_query(text, breaking, summary, description):
    messages = [
        {
            "role": "system",
            "content": "You are a news analyzer. Process short news snippets (minimum 10-15 words) and return a Python dict with the following keys: 'breaking' (string - compelling headline), 'summary' (string - exactly 20-30 words overview), 'description' (string - exactly 60-100 words detailed explanation). Return ONLY the Python dict, nothing else."
        },
        {
            "role": "user",
            "content": f"Update analysis based on new text. Existing values: breaking='{breaking}', summary='{summary}', description='{description}'. New text: {text}. Please regenerate the breaking, summary, and description."
        }
    ]
    
    try:
        result = make_request(messages)
        if isinstance(result, str):
            return json.loads(result)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def check_similarity(text1, text2):
    messages = [
        {
            "role": "system",
            "content": "You are a news similarity analyzer. Compare two news snippets and determine if they are similar or about the same topic. Return ONLY a Python dict with one key: 'is_similar' (boolean - True if the texts are similar or about the same news topic, False otherwise). Return ONLY the Python dict, nothing else."
        },
        {
            "role": "user",
            "content": f"Compare these two texts:\n\nText 1: {text1}\n\nText 2: {text2}\n\nAre they similar or about the same topic?"
        }
    ]
    
    try:
        result = make_request(messages)
        
        if isinstance(result, str):
            result = json.loads(result)
        
        if isinstance(result, dict) and 'is_similar' in result:
            return bool(result['is_similar'])
        
        return False
    except Exception as e:
        return False