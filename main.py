import os
from flask import Flask, jsonify
from flask_cors import CORS
from routes.member import bp as member_bp
from routes.raw import bp as raw_bp
from routes.processed import bp as processed_bp
from database import db
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configure CORS
CORS(app, 
     origins="*",
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
     supports_credentials=True,
     max_age=3600)

# Register blueprints
app.register_blueprint(member_bp)
app.register_blueprint(raw_bp)
app.register_blueprint(processed_bp)

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Server is running'}), 200

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'message': 'Endpoint not found'}), 404

if __name__ == '__main__':
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Initialize database connection pool
    print("\n🔌 Initializing database connection pool...")
    db.connect()
    print("✅ Database pool initialized")
    
    # Run Flask app
    print(f"🚀 Starting Flask server on http://0.0.0.0:{PORT}")
    try:
        app.run(host='0.0.0.0', port=PORT, debug=DEBUG, threaded=True)
    finally:
        print("\n📴 Closing database connections...")
        db.close_all()
