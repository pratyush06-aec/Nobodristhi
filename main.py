import asyncio
import os
import threading
from flask import Flask, jsonify
from flask_cors import CORS
from routes.member import bp as member_bp
from routes.raw import bp as raw_bp
from routes.processed import bp as processed_bp
from database import db
from dotenv import load_dotenv
from handlers.process import init_tables, processing_task

load_dotenv()

app = Flask(__name__)

CORS(app, 
     origins="*",
     allow_headers="*",
     methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
     supports_credentials=True)

app.register_blueprint(member_bp)
app.register_blueprint(raw_bp)
app.register_blueprint(processed_bp)

# Global event loop and thread
_loop = None
_loop_thread = None

def get_event_loop():
    """Get or create the background event loop"""
    global _loop
    if _loop is None or _loop.is_closed():
        _loop = asyncio.new_event_loop()
    return _loop

def run_async_in_background(coro):
    """Run async code in the background event loop thread"""
    loop = get_event_loop()
    return asyncio.run_coroutine_threadsafe(coro, loop).result()

def start_event_loop_thread():
    """Start the background event loop in a separate thread"""
    global _loop, _loop_thread
    
    _loop = asyncio.new_event_loop()
    
    def run_loop():
        asyncio.set_event_loop(_loop)
        _loop.run_forever()
    
    _loop_thread = threading.Thread(target=run_loop, daemon=True)
    _loop_thread.start()
    print("✅ Background event loop started")

async def startup():
    db_connected = False
    try:
        await db.connect()
        print("Database connected successfully")
        db_connected = True
        
        await init_tables()
        print("Tables initialized successfully")
        
        asyncio.create_task(processing_task.start())
        print("Processing task started")
    except Exception as e:
        print(f"\n❌ Error during startup: {e}")
        if not db_connected:
            print("\n⚠️  Database connection failed!")
            print("Please check your .env file and ensure you have:")
            print("  - POSTGRES_TOKEN_HOST (e.g., pg-xxx.neon.tech)")
            print("  - POSTGRES_TOKEN_PORT (usually 5432)")
            print("  - POSTGRES_TOKEN_USERNAME")
            print("  - POSTGRES_TOKEN_PASSWORD")
            print("\nServer will start, but API endpoints will fail without database connection.")
        else:
            print(f"\nServer failed to initialize properly.")

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Server is running'})

if __name__ == '__main__':
    PORT = int(os.getenv('PORT', 5000))
    
    # Start background event loop thread
    start_event_loop_thread()
    
    # Initialize database in the background loop
    try:
        run_async_in_background(startup())
        print("✅ Application initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=PORT, debug=True)
