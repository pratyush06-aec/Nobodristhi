import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from routes.member import bp as member_bp
from routes.raw import bp as raw_bp
from routes.processed import bp as processed_bp
from routes.admin import bp as admin_bp
from database import db
from handlers.process import init_tables, processing_task
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Suppress noisy werkzeug logging for malformed requests
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

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
app.register_blueprint(admin_bp)

@app.before_request
def validate_request():
    """Validate incoming requests and reject obviously malformed ones"""
    # Allow preflight CORS requests
    if request.method == 'OPTIONS':
        return None
    
    # Validate that request has proper headers
    if request.method in ['POST', 'PUT', 'PATCH']:
        content_type = request.headers.get('Content-Type', '')
        if not content_type and not request.files:
            return jsonify({'success': False, 'message': 'Invalid Content-Type'}), 400
    
    return None

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Server is running'}), 200

@app.errorhandler(400)
def bad_request(e):
    """Handle bad requests silently without logging spam"""
    return jsonify({'success': False, 'message': 'Bad request'}), 400

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'message': 'Endpoint not found'}), 404

if __name__ == '__main__':
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Only initialize once (not in the reloader process)
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not DEBUG:
        # Initialize database connection pool
        print("\n🔌 Initializing database connection pool...")
        db.connect()
        print("✅ Database pool initialized")
        
        # Initialize database tables
        print("\n📊 Initializing database tables...")
        init_tables()
        print("✅ Database tables ready")
        
        # Start background processing task
        print("\n🔄 Starting background processing task...")
        processing_task.start()
        print("✅ Background task started")
    
    # Run Flask app
    print(f"\n🚀 Starting Flask server on http://0.0.0.0:{PORT}")
    try:
        app.run(host='0.0.0.0', port=PORT, debug=DEBUG, threaded=True)
    finally:
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not DEBUG:
            print("\n🛑 Shutting down...")
            processing_task.stop()
            print("✅ Background task stopped")
            db.close_all()
            print("✅ Database connections closed")
