import requests
import json
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

URL = os.getenv("SEARCH_ENDPOINT")
CODE = os.getenv("SEARCH_CODE")

logger.info(f"Search endpoint configured: {URL}")
logger.info(f"Search code configured: {CODE}")

def search_image(query):
    """Search for images using the search service"""
    if not URL:
        logger.error("SEARCH_ENDPOINT not configured in environment")
        return []
    
    if not CODE:
        logger.error("SEARCH_CODE not configured in environment")
        return []
    
    payload = {
        "Query": query,
        "AccessCode": CODE
    }
    
    try:
        search_url = f"{URL}/api/search"
        logger.info(f"Sending search request to {search_url}")
        logger.debug(f"Payload: {payload}")
        
        response = requests.post(
            search_url, 
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        logger.info(f"Search response status: {response.status_code}")
        logger.debug(f"Search response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Search successful, received {len(result) if isinstance(result, list) else 1} result(s)")
            return result if isinstance(result, list) else []
        else:
            logger.warning(f"Search returned non-200 status: {response.status_code}")
            return []
            
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error to search service: {str(e)}")
        return []
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout connecting to search service: {str(e)}")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse search response as JSON: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in search_image: {str(e)}")
        return []