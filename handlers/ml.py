import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

# Load all tokens from tokens.json
TOKENS = []
TOKEN_INDEX = 0

def load_tokens():
    global TOKENS
    try:
        token_file = os.path.join(os.path.dirname(__file__), '..', 'tokens.json')
        with open(token_file, 'r') as f:
            token_data = json.load(f)
            TOKENS = [t['token'] for t in token_data]
            print(f"✅ Loaded {len(TOKENS)} tokens from tokens.json")
    except Exception as e:
        print(f"❌ Error loading tokens.json: {e}")
        TOKENS = []

# Initialize tokens on import
load_tokens()

API_URL = "https://openrouter.io/api/v1/chat/completions"
MODEL = "openai/gpt-4o-mini:free"

def get_next_token():
    """Get the next available token in rotation"""
    global TOKEN_INDEX
    if not TOKENS:
        return None
    token = TOKENS[TOKEN_INDEX]
    TOKEN_INDEX = (TOKEN_INDEX + 1) % len(TOKENS)
    return token

def make_request(messages, max_retries=3):
    """Make API request with token rotation on failure"""
    for attempt in range(max_retries):
        token = get_next_token()
        if not token:
            return {
                "success": False,
                "error": "No tokens available"
            }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        payload = {
            "model": MODEL,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                # Extract the content from OpenRouter response
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    return content
                return result
            elif response.status_code == 401:
                print(f"❌ Token {TOKEN_INDEX} invalid, trying next...")
                continue
            elif response.status_code == 429:
                print(f"⚠️  Rate limited on token {TOKEN_INDEX}, trying next...")
                continue
            else:
                print(f"⚠️  Request failed with status {response.status_code}, trying next...")
                continue
                
        except requests.exceptions.Timeout:
            print(f"⚠️  Request timeout on token {TOKEN_INDEX}, trying next...")
            continue
        except Exception as e:
            print(f"⚠️  Error on token {TOKEN_INDEX}: {str(e)}, trying next...")
            continue
    
    return {
        "success": False,
        "error": f"Failed after {max_retries} attempts"
    }

def optimize_query(text):
    messages = [
        {
            "role": "system",
            "content": "You are a news analyzer. Process short news snippets (minimum 10-15 words) and return a Python dict with the following keys: 'breaking' (string - compelling headline if it's breaking news, None otherwise), 'summary' (string - exactly 20-30 words overview), 'description' (string - exactly 60-100 words detailed explanation). Return ONLY the Python dict, nothing else."
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
            "content": "You are a news analyzer. Process short news snippets (minimum 10-15 words) and return a Python dict with the following keys: 'breaking' (string - compelling headline if it's breaking news, None otherwise), 'summary' (string - exactly 20-30 words overview), 'description' (string - exactly 60-100 words detailed explanation). Return ONLY the Python dict, nothing else."
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
        
        # Parse result and return boolean
        if isinstance(result, dict) and 'is_similar' in result:
            return bool(result['is_similar'])
        
        return False
    except Exception as e:
        print(f"❌ Similarity check error: {str(e)}")
        return False