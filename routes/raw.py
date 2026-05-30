from flask import Blueprint, request, jsonify
import string
import random
import json
from database.pool import db

bp = Blueprint('raw', __name__, url_prefix='/raw')

@bp.route('/report', methods=['POST'])
def report():
    conn = None
    try:
        text = request.form.get('text')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        reporter_id = request.form.get('reporterid')
        source = request.form.get('source')
        img_file = request.files.get('image')
        
        if not all([text, latitude, longitude, reporter_id]):
            return jsonify({
                'success': False,
                'message': 'Missing required fields: text, latitude, longitude, reporterid'
            }), 400
        
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'latitude and longitude must be valid numbers'
            }), 400
        
        location = [latitude, longitude]
        
        img_url = None
        if img_file and img_file.filename:
            img_url = upload_image_to_supabase(img_file)
            if not img_url:
                return jsonify({
                    'success': False,
                    'message': 'Failed to upload image'
                }), 500
        
        result = save_raw_report(text, location, reporter_id, img_url, source)
        status_code = 201 if result.get('success') else 500
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

def upload_image_to_supabase(img_file):
    try:
        file_content = img_file.read()
        
        characters = string.ascii_letters + string.digits
        random_suffix = ''.join(random.choice(characters) for _ in range(10))
        file_extension = img_file.filename.rsplit('.', 1)[-1] if '.' in img_file.filename else 'jpg'
        file_name = f"{random_suffix}.{file_extension}"
        
        response = db.supabase_client.storage.from_('images').upload(
            file=file_content,
            path=file_name
        )
        
        img_url = db.supabase_client.storage.from_('images').get_public_url(file_name)
        return img_url
    except Exception as e:
        return None

def save_raw_report(text, location, reporter_id, img_url=None, source=None):
    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS raw_reports (
                raw_id VARCHAR PRIMARY KEY,
                text TEXT NOT NULL,
                location JSONB NOT NULL,
                reporter_id TEXT NOT NULL,
                img_url TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        characters = string.ascii_letters + string.digits
        raw_id = ''.join(random.choice(characters) for _ in range(16))
        
        cur.execute('''
            INSERT INTO raw_reports (raw_id, text, location, reporter_id, img_url, source, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        ''', (raw_id, text, json.dumps(location), reporter_id, img_url, source))
        conn.commit()
        
        cur.close()
        return {
            "success": True,
            'message': 'Raw report saved successfully'
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            db.return_connection(conn)

@bp.route('/', methods=['GET'])
def get_all_reports():
    try:
        result = fetch_all_raw_reports()
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

def fetch_all_raw_reports():
    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS raw_reports (
                raw_id VARCHAR PRIMARY KEY,
                text TEXT NOT NULL,
                location JSONB NOT NULL,
                reporter_id TEXT NOT NULL,
                img_url TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cur.execute('''
            SELECT raw_id, text, location, reporter_id, img_url, source, created_at
            FROM raw_reports
            ORDER BY created_at DESC
        ''')
        rows = cur.fetchall()
        
        reports_list = []
        for row in rows:
            reports_list.append({
                'raw_id': row[0],
                'text': row[1],
                'location': json.loads(row[2]) if row[2] else None,
                'reporter_id': row[3],
                'img_url': row[4],
                'source': row[5],
                'created_at': row[6].isoformat() if row[6] else None
            })
        
        cur.close()
        return {
            "success": True,
            'message': 'Reports retrieved successfully',
            'data': reports_list
        }
        
    except Exception as e:
        raise
    finally:
        if conn:
            db.return_connection(conn)

@bp.route('/delete', methods=['POST'])
def delete():
    try:
        data = request.get_json()
        raw_id = data.get('raw_id')
        
        if not raw_id:
            return jsonify({
                'success': False,
                'message': 'Missing required field: raw_id'
            }), 400
        
        result = delete_raw_report(raw_id)
        status_code = 404 if not result.get('success') else 200
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

def delete_raw_report(raw_id):
    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT raw_id FROM raw_reports WHERE raw_id = %s', (raw_id,))
        existing_report = cur.fetchone()
        
        if not existing_report:
            return {
                "success": False,
                'message': 'Report not found'
            }
        
        cur.execute('DELETE FROM raw_reports WHERE raw_id = %s', (raw_id,))
        conn.commit()
        
        cur.close()
        return {
            "success": True,
            'message': 'Report deleted successfully'
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            db.return_connection(conn)
