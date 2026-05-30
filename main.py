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

_db_connected = False
_task_started = False

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Server is running'})

@app.before_request
def connect_database():
    global _db_connected, _task_started
    if not _db_connected:
        try:
            asyncio.run(db.connect())
            print("Database connected successfully")
            _db_connected = True
            
            asyncio.run(init_tables())
            
            if not _task_started:
                asyncio.create_task(processing_task.start())
                _task_started = True
                print("Processing task started")
        except Exception as e:
            print(f"Error connecting to database: {e}")

if __name__ == '__main__':
    PORT = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
