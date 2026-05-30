import asyncio
import os
from flask import Flask, jsonify
from flask_cors import CORS
from routes.member import bp as member_bp
from database import db
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CORS(app, 
     origins="*",
     allow_headers="*",
     methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
     supports_credentials=True)

app.register_blueprint(member_bp)

_db_connected = False

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Server is running'})

@app.before_request
def connect_database():
    global _db_connected
    if not _db_connected:
        try:
            asyncio.run(db.connect())
            print("Database connected successfully")
            _db_connected = True
        except Exception as e:
            print(f"Error connecting to database: {e}")

if __name__ == '__main__':
    PORT = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
