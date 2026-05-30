import asyncio
import os
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

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Server is running'})

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

if __name__ == '__main__':
    PORT = int(os.getenv('PORT', 5000))
    
    # Create and set a persistent event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Initialize database in this persistent loop
    try:
        loop.run_until_complete(startup())
        print("✅ Application initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
    
    # Run Flask app (will use the persistent event loop for async routes)
    app.run(host='0.0.0.0', port=PORT, debug=True)
