import os
import requests
from pathlib import Path
from datetime import datetime
import json

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', '')
ELEVENLABS_API_URL = 'https://api.elevenlabs.io/v1'
VOICE_ID = 'QTKSa2Iyv0yoxvXY2V8a'  

VOICE_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'voice')


def ensure_voice_directory():
    try:
        Path(VOICE_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
        print(f"✅ [ENSURE_VOICE_DIR] Voice directory ready: {VOICE_OUTPUT_DIR}")
        return True
    except Exception as e:
        print(f"❌ [ENSURE_VOICE_DIR] Error creating directory: {str(e)}")
        return False


def generate_voice_file(text, complete_id, voice_id=None):
    try:
        if not ELEVENLABS_API_KEY:
            print("❌ [GENERATE_VOICE_FILE] ElevenLabs API key not configured")
            return {
                'success': False,
                'message': 'ElevenLabs API key not configured'
            }
        
        if not text or not isinstance(text, str):
            print("❌ [GENERATE_VOICE_FILE] Invalid text input")
            return {
                'success': False,
                'message': 'Text input is required and must be a string'
            }
        
        # Ensure voice directory exists
        if not ensure_voice_directory():
            return {
                'success': False,
                'message': 'Failed to create voice directory'
            }
        
        voice_id = voice_id or VOICE_ID
        print(f"\n🔵 [GENERATE_VOICE_FILE] Starting TTS for complete_id={complete_id}")
        print(f"📝 [GENERATE_VOICE_FILE] Text length: {len(text)} characters")
        
        # Prepare API request
        url = f"{ELEVENLABS_API_URL}/text-to-speech/{voice_id}"
        headers = {
            'xi-api-key': ELEVENLABS_API_KEY,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'text': text,
            'model_id': 'eleven_monolingual_v1',
            'voice_settings': {
                'stability': 0.5,
                'similarity_boost': 0.75
            }
        }
        
        print(f"🔄 [GENERATE_VOICE_FILE] Calling ElevenLabs API...")
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        if response.status_code != 200:
            error_msg = f"ElevenLabs API error: {response.status_code} - {response.text}"
            print(f"❌ [GENERATE_VOICE_FILE] {error_msg}")
            return {
                'success': False,
                'message': error_msg
            }
        
        print(f"✅ [GENERATE_VOICE_FILE] API response received")
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{complete_id}_{timestamp}.mp3"
        filepath = os.path.join(VOICE_OUTPUT_DIR, filename)
        
        # Save audio file
        print(f"💾 [GENERATE_VOICE_FILE] Saving audio to {filepath}")
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        # Verify file was created
        if not os.path.exists(filepath):
            print(f"❌ [GENERATE_VOICE_FILE] File creation failed")
            return {
                'success': False,
                'message': 'Failed to save audio file'
            }
        
        file_size = os.path.getsize(filepath)
        print(f"✅ [GENERATE_VOICE_FILE] Audio file saved successfully ({file_size} bytes)")
        
        # Return relative path for database storage
        relative_path = os.path.relpath(filepath, os.path.dirname(os.path.dirname(__file__)))
        
        return {
            'success': True,
            'message': 'Voice file generated successfully',
            'audio_path': relative_path,
            'filename': filename,
            'file_size': file_size
        }
        
    except requests.exceptions.Timeout:
        error_msg = "ElevenLabs API request timed out"
        print(f"❌ [GENERATE_VOICE_FILE] {error_msg}")
        return {
            'success': False,
            'message': error_msg
        }
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error: {str(e)}"
        print(f"❌ [GENERATE_VOICE_FILE] {error_msg}")
        return {
            'success': False,
            'message': error_msg
        }
    except Exception as e:
        print(f"❌ [GENERATE_VOICE_FILE] Unexpected error: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"📍 [GENERATE_VOICE_FILE] Traceback: {traceback.format_exc()}")
        return {
            'success': False,
            'message': f'Error generating voice file: {str(e)}'
        }


def get_voice_file_path(complete_id):
    """
    Get the voice file path for a given complete_id
    
    Args:
        complete_id (str): ID of the complete news
    
    Returns:
        str: Voice file path or None if not found
    """
    try:
        if not os.path.exists(VOICE_OUTPUT_DIR):
            return None
        
        files = os.listdir(VOICE_OUTPUT_DIR)
        matching_files = [f for f in files if f.startswith(complete_id)]
        
        if matching_files:
            # Return the most recent file for this complete_id
            matching_files.sort(reverse=True)
            return os.path.join(VOICE_OUTPUT_DIR, matching_files[0])
        
        return None
    except Exception as e:
        print(f"❌ [GET_VOICE_FILE_PATH] Error: {str(e)}")
        return None
