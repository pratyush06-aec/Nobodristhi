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
        print("\n🔵 [RAW REPORT] Request received")
        
        text = request.form.get('text')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        reporter_id = request.form.get('reporterid')
        source = request.form.get('source')
        img_file = request.files.get('image')
        
        print(f"📥 [RAW REPORT] Fields received - text: {bool(text)}, lat: {latitude}, lon: {longitude}, reporter: {reporter_id}")
        
        if not all([text, latitude, longitude, reporter_id]):
            print("❌ [RAW REPORT] Missing required fields")
            return jsonify({
                'success': False,
                'message': 'Missing required fields: text, latitude, longitude, reporterid'
            }), 400
        
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            print("❌ [RAW REPORT] Invalid coordinates")
            return jsonify({
                'success': False,
                'message': 'latitude and longitude must be valid numbers'
            }), 400
        
        location = [latitude, longitude]
        
        img_url = None
        if img_file and img_file.filename:
            print("📸 [RAW REPORT] Uploading image to Supabase...")
            img_url = upload_image_to_supabase(img_file)
            if not img_url:
                print("❌ [RAW REPORT] Image upload failed")
                return jsonify({
                    'success': False,
                    'message': 'Failed to upload image'
                }), 500
            print(f"✅ [RAW REPORT] Image uploaded: {img_url[:50]}...")
        
        print("💾 [RAW REPORT] Saving report to database...")
        result = save_raw_report(text, location, reporter_id, img_url, source)
        print(f"✅ [RAW REPORT] Report saved: {result}")
        
        status_code = 201 if result.get('success') else 500
        return jsonify(result), status_code
        
    except Exception as e:
        print(f"❌ [RAW REPORT] Exception: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"📍 [RAW REPORT] Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

def upload_image_to_supabase(img_file):
    try:
        print("🔵 [UPLOAD_IMAGE] Starting image upload")
        file_content = img_file.read()
        print(f"📊 [UPLOAD_IMAGE] File size: {len(file_content)} bytes")
        
        characters = string.ascii_letters + string.digits
        random_suffix = ''.join(random.choice(characters) for _ in range(10))
        file_extension = img_file.filename.rsplit('.', 1)[-1] if '.' in img_file.filename else 'jpg'
        file_name = f"{random_suffix}.{file_extension}"
        print(f"📝 [UPLOAD_IMAGE] File name: {file_name}")
        
        response = db.supabase_client.storage.from_('images').upload(
            file=file_content,
            path=file_name
        )
        print("✅ [UPLOAD_IMAGE] File uploaded to Supabase")
        
        img_url = db.supabase_client.storage.from_('images').get_public_url(file_name)
        print(f"✅ [UPLOAD_IMAGE] Public URL generated")
        
        return img_url
    except Exception as e:
        print(f"❌ [UPLOAD_IMAGE] Upload failed: {type(e).__name__}: {str(e)}")
        return None

def save_raw_report(text, location, reporter_id, img_url=None, source=None):
    conn = None
    try:
        print(f"\n🔵 [SAVE_RAW_REPORT] Starting save for reporter: {reporter_id}")
        
        print("🔌 [SAVE_RAW_REPORT] Getting database connection...")
        conn = db.get_connection()
        cur = conn.cursor()
        print("✅ [SAVE_RAW_REPORT] Connection acquired")
        
        print("📊 [SAVE_RAW_REPORT] Creating raw_reports table if not exists...")
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
        print("✅ [SAVE_RAW_REPORT] Table verified")
        
        characters = string.ascii_letters + string.digits
        raw_id = ''.join(random.choice(characters) for _ in range(16))
        print(f"🆔 [SAVE_RAW_REPORT] Generated raw_id: {raw_id}")
        
        print("➕ [SAVE_RAW_REPORT] Inserting report...")
        cur.execute('''
            INSERT INTO raw_reports (raw_id, text, location, reporter_id, img_url, source, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        ''', (raw_id, text, json.dumps(location), reporter_id, img_url, source))
        conn.commit()
        print(f"✅ [SAVE_RAW_REPORT] Report {raw_id} inserted successfully")
        
        cur.close()
        return {
            "success": True,
            'message': 'Raw report saved successfully'
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ [SAVE_RAW_REPORT] Exception: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"📍 [SAVE_RAW_REPORT] Traceback: {traceback.format_exc()}")
        raise
    finally:
        if conn:
            db.return_connection(conn)
            print("✅ [SAVE_RAW_REPORT] Connection returned to pool")

@bp.route('/', methods=['GET'])
def get_all_reports():
    try:
        print("\n🔵 [GET_ALL_REPORTS] Request received")
        result = fetch_all_raw_reports()
        print(f"✅ [GET_ALL_REPORTS] Retrieved {len(result.get('data', []))} reports")
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ [GET_ALL_REPORTS] Exception: {type(e).__name__}: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

def fetch_all_raw_reports():
    conn = None
    try:
        print(f"\n🔵 [FETCH_ALL_RAW_REPORTS] Starting fetch")
        
        print("🔌 [FETCH_ALL_RAW_REPORTS] Getting database connection...")
        conn = db.get_connection()
        cur = conn.cursor()
        print("✅ [FETCH_ALL_RAW_REPORTS] Connection acquired")
        
        print("📊 [FETCH_ALL_RAW_REPORTS] Creating raw_reports table if not exists...")
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
        print("✅ [FETCH_ALL_RAW_REPORTS] Table verified")
        
        print("🔍 [FETCH_ALL_RAW_REPORTS] Fetching all reports...")
        cur.execute('''
            SELECT raw_id, text, location, reporter_id, img_url, source, created_at
            FROM raw_reports
            ORDER BY created_at DESC
        ''')
        rows = cur.fetchall()
        print(f"✅ [FETCH_ALL_RAW_REPORTS] Found {len(rows)} reports")
        
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
        print(f"❌ [FETCH_ALL_RAW_REPORTS] Exception: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"📍 [FETCH_ALL_RAW_REPORTS] Traceback: {traceback.format_exc()}")
        raise
    finally:
        if conn:
            db.return_connection(conn)
            print("✅ [FETCH_ALL_RAW_REPORTS] Connection returned to pool")

@bp.route('/delete', methods=['POST'])
def delete():
    try:
        print("\n🔵 [DELETE_RAW] Request received")
        
        data = request.get_json()
        raw_id = data.get('raw_id')
        print(f"📥 [DELETE_RAW] Deleting raw_id: {raw_id}")
        
        if not raw_id:
            print("❌ [DELETE_RAW] Missing raw_id")
            return jsonify({
                'success': False,
                'message': 'Missing required field: raw_id'
            }), 400
        
        result = delete_raw_report(raw_id)
        print(f"✅ [DELETE_RAW] Result: {result}")
        
        status_code = 404 if not result.get('success') else 200
        return jsonify(result), status_code
        
    except Exception as e:
        print(f"❌ [DELETE_RAW] Exception: {type(e).__name__}: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

def delete_raw_report(raw_id):
    conn = None
    try:
        print(f"\n🔵 [DELETE_RAW_REPORT] Starting delete for raw_id: {raw_id}")
        
        print("🔌 [DELETE_RAW_REPORT] Getting database connection...")
        conn = db.get_connection()
        cur = conn.cursor()
        print("✅ [DELETE_RAW_REPORT] Connection acquired")
        
        print(f"🔍 [DELETE_RAW_REPORT] Checking if report {raw_id} exists...")
        cur.execute('SELECT raw_id FROM raw_reports WHERE raw_id = %s', (raw_id,))
        existing_report = cur.fetchone()
        
        if not existing_report:
            print(f"❌ [DELETE_RAW_REPORT] Report {raw_id} not found")
            return {
                "success": False,
                'message': 'Report not found'
            }
        print(f"✅ [DELETE_RAW_REPORT] Report found - proceeding with delete")
        
        print(f"🗑️  [DELETE_RAW_REPORT] Deleting report {raw_id}...")
        cur.execute('DELETE FROM raw_reports WHERE raw_id = %s', (raw_id,))
        conn.commit()
        print(f"✅ [DELETE_RAW_REPORT] Report deleted successfully")
        
        cur.close()
        return {
            "success": True,
            'message': 'Report deleted successfully'
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ [DELETE_RAW_REPORT] Exception: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"📍 [DELETE_RAW_REPORT] Traceback: {traceback.format_exc()}")
        raise
    finally:
        if conn:
            db.return_connection(conn)
            print("✅ [DELETE_RAW_REPORT] Connection returned to pool")
