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
    try:
        await db.connect()
        print("Database connected successfully")
        
        await init_tables()
        print("Tables initialized successfully")
        
        asyncio.create_task(processing_task.start())
        print("Processing task started")
    except Exception as e:
        print(f"Error during startup: {e}")

if __name__ == '__main__':
    PORT = int(os.getenv('PORT', 5000))
    
    # Run startup async function
    asyncio.run(startup())
    
    # Start Flask app
    app.run(host='0.0.0.0', port=PORT, debug=True)
