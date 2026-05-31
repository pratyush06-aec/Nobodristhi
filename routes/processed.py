from flask import Blueprint, request, jsonify
import json
from database.pool import db

bp = Blueprint('processed', __name__, url_prefix='/processed')

@bp.route('/', methods=['GET'])
def get_all_processed():
    try:
        result = fetch_all_processed_reports()
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ [GET_ALL_PROCESSED] Exception: {type(e).__name__}: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

def fetch_all_processed_reports():
    conn = None
    try:
        
        conn = db.get_connection()
        cur = conn.cursor()
        print("✅ [FETCH_ALL_PROCESSED_REPORTS] Connection acquired")
        
        print("🔍 [FETCH_ALL_PROCESSED_REPORTS] Fetching all reports...")
        cur.execute('''
            SELECT processed_id, raw_id, breaking, summary, description, location, reporter_id, img_url, source, created_at
            FROM processed_reports
            WHERE is_approved = 0
            ORDER BY created_at DESC
        ''')
        rows = cur.fetchall()
        print(f"✅ [FETCH_ALL_PROCESSED_REPORTS] Found {len(rows)} reports")
        
        reports_list = []
        for row in rows:
            location = row[5]
            if isinstance(location, str):
                try:
                    location = json.loads(location)
                except:
                    location = []
            elif location is None:
                location = []
            
            # Convert floats to strings in location array
            if isinstance(location, list):
                location = [str(item) if isinstance(item, float) else item for item in location]
            
            img_url = row[7]
            if isinstance(img_url, str):
                try:
                    img_url = json.loads(img_url)
                except:
                    img_url = []
            elif img_url is None:
                img_url = []
            elif not isinstance(img_url, list):
                img_url = [img_url] if img_url else []
            
            reports_list.append({
                'processed_id': row[0],
                'raw_id': row[1],
                'breaking': row[2],
                'summary': row[3],
                'description': row[4],
                'location': location,
                'reporter_id': row[6],
                'img_url': img_url,
                'source': row[8],
                'created_at': row[9].isoformat() if row[9] else None
            })
        
        cur.close()
        return {
            "success": True,
            'message': 'Processed reports retrieved successfully',
            'data': reports_list
        }
        
    except Exception as e:
        print(f"❌ [FETCH_ALL_PROCESSED_REPORTS] Exception: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"📍 [FETCH_ALL_PROCESSED_REPORTS] Traceback: {traceback.format_exc()}")
        raise
    finally:
        if conn:
            db.return_connection(conn)
            print("✅ [FETCH_ALL_PROCESSED_REPORTS] Connection returned to pool")

@bp.route('/delete', methods=['POST'])
def delete():
    try:
        print("\n🔵 [DELETE_PROCESSED] Request received")
        
        data = request.get_json()
        processed_id = data.get('processed_id')
        print(f"📥 [DELETE_PROCESSED] Deleting processed_id: {processed_id}")
        
        if not processed_id:
            print("❌ [DELETE_PROCESSED] Missing processed_id")
            return jsonify({
                'success': False,
                'message': 'Missing required field: processed_id'
            }), 400
        
        result = delete_processed_report(processed_id)
        print(f"✅ [DELETE_PROCESSED] Result: {result}")
        
        status_code = 404 if not result.get('success') else 200
        return jsonify(result), status_code
        
    except Exception as e:
        print(f"❌ [DELETE_PROCESSED] Exception: {type(e).__name__}: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/report', methods=['POST'])
def report():
    try:
        print("\n🔵 [GET_PROCESSED_REPORT] Request received")
        
        data = request.get_json()
        processed_id = data.get('processed_id')
        print(f"📥 [GET_PROCESSED_REPORT] Getting processed_id: {processed_id}")
        
        if not processed_id:
            print("❌ [GET_PROCESSED_REPORT] Missing processed_id")
            return jsonify({
                'success': False,
                'message': 'Missing required field: processed_id'
            }), 400
        
        result = fetch_processed_report_by_id(processed_id)
        print(f"✅ [GET_PROCESSED_REPORT] Result retrieved")
        
        if not result.get('success'):
            return jsonify(result), 404
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ [GET_PROCESSED_REPORT] Exception: {type(e).__name__}: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

def fetch_processed_report_by_id(processed_id):
    conn = None
    try:
        print(f"\n🔵 [FETCH_PROCESSED_REPORT_BY_ID] Starting fetch for {processed_id}")
        
        print("🔌 [FETCH_PROCESSED_REPORT_BY_ID] Getting database connection...")
        conn = db.get_connection()
        cur = conn.cursor()
        print("✅ [FETCH_PROCESSED_REPORT_BY_ID] Connection acquired")
        
        print(f"🔍 [FETCH_PROCESSED_REPORT_BY_ID] Fetching report {processed_id}...")
        cur.execute('''
            SELECT processed_id, raw_id, breaking, summary, description, location, reporter_id, img_url, source, created_at
            FROM processed_reports
            WHERE processed_id = %s
        ''', (processed_id,))
        row = cur.fetchone()
        
        if not row:
            print(f"❌ [FETCH_PROCESSED_REPORT_BY_ID] Report {processed_id} not found")
            return {
                "success": False,
                'message': 'Processed report not found'
            }
        
        print(f"✅ [FETCH_PROCESSED_REPORT_BY_ID] Report found")
        cur.close()
        
        # Handle location - JSONB column already returns as dict/list, not string
        location = row[5]
        if isinstance(location, str):
            try:
                location = json.loads(location)
            except:
                location = []
        elif location is None:
            location = []
        
        # Convert floats to strings in location array
        if isinstance(location, list):
            location = [str(item) if isinstance(item, float) else item for item in location]
        
        # Handle img_url - similarly handle JSONB if present
        img_url = row[7]
        if isinstance(img_url, str):
            try:
                img_url = json.loads(img_url)
            except:
                img_url = []
        elif img_url is None:
            img_url = []
        elif not isinstance(img_url, list):
            img_url = [img_url] if img_url else []
        
        return {
            "success": True,
            'message': 'Processed report retrieved successfully',
            'data': {
                'processed_id': row[0],
                'raw_id': row[1],
                'breaking': row[2],
                'summary': row[3],
                'description': row[4],
                'location': location,
                'reporter_id': row[6],
                'img_url': img_url,
                'source': row[8],
                'created_at': row[9].isoformat() if row[9] else None
            }
        }
        
    except Exception as e:
        print(f"❌ [FETCH_PROCESSED_REPORT_BY_ID] Exception: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"📍 [FETCH_PROCESSED_REPORT_BY_ID] Traceback: {traceback.format_exc()}")
        raise
    finally:
        if conn:
            db.return_connection(conn)
            print("✅ [FETCH_PROCESSED_REPORT_BY_ID] Connection returned to pool")

def delete_processed_report(processed_id):
    conn = None
    try:
        print(f"\n🔵 [DELETE_PROCESSED_REPORT] Starting delete for {processed_id}")
        
        print("🔌 [DELETE_PROCESSED_REPORT] Getting database connection...")
        conn = db.get_connection()
        cur = conn.cursor()
        print("✅ [DELETE_PROCESSED_REPORT] Connection acquired")
        
        print(f"🔍 [DELETE_PROCESSED_REPORT] Checking if report {processed_id} exists...")
        cur.execute('SELECT processed_id FROM processed_reports WHERE processed_id = %s', (processed_id,))
        existing_report = cur.fetchone()
        
        if not existing_report:
            print(f"❌ [DELETE_PROCESSED_REPORT] Report {processed_id} not found")
            return {
                "success": False,
                'message': 'Processed report not found'
            }
        print(f"✅ [DELETE_PROCESSED_REPORT] Report found - proceeding with delete")
        
        print(f"🗑️  [DELETE_PROCESSED_REPORT] Deleting report {processed_id}...")
        cur.execute('DELETE FROM processed_reports WHERE processed_id = %s', (processed_id,))
        conn.commit()
        print(f"✅ [DELETE_PROCESSED_REPORT] Report deleted successfully")
        
        cur.close()
        return {
            "success": True,
            'message': 'Processed report deleted successfully'
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ [DELETE_PROCESSED_REPORT] Exception: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"📍 [DELETE_PROCESSED_REPORT] Traceback: {traceback.format_exc()}")
        raise
    finally:
        if conn:
            db.return_connection(conn)
            print("✅ [DELETE_PROCESSED_REPORT] Connection returned to pool")
