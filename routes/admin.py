from flask import Blueprint, request, jsonify, send_file
from database.pool import db
import json
import string
import secrets
import os
from handlers.voice import generate_voice_file, get_voice_file_path

bp = Blueprint('admin', __name__, url_prefix='/admin')

def generate_complete_id():
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(16))

@bp.route('/approve', methods=['POST'])
def approve_news():
    try:
        print("\n🔵 [APPROVE_NEWS] Request received")
        
        data = request.get_json()
        print(f"📥 [APPROVE_NEWS] Raw data: {data}")
        
        if data is None:
            print("❌ [APPROVE_NEWS] Invalid JSON format")
            return jsonify({
                'success': False,
                'message': 'Invalid JSON format'
            }), 400
        
        processed_id = data.get('processed_id')
        img_index = data.get('img_index')
        
        print(f"📥 [APPROVE_NEWS] processed_id={processed_id}, img_index={img_index}")
        
        if not processed_id:
            print("❌ [APPROVE_NEWS] Missing processed_id")
            return jsonify({
                'success': False,
                'message': 'Missing required field: processed_id'
            }), 400
        
        if img_index is None:
            print("❌ [APPROVE_NEWS] Missing img_index")
            return jsonify({
                'success': False,
                'message': 'Missing required field: img_index (image selection required)'
            }), 400
        
        # Ensure img_index is an integer
        try:
            img_index = int(img_index)
            print(f"✅ [APPROVE_NEWS] img_index converted to int: {img_index}")
        except (ValueError, TypeError) as e:
            print(f"❌ [APPROVE_NEWS] img_index conversion error: {e}")
            return jsonify({
                'success': False,
                'message': 'img_index must be an integer'
            }), 400
        
        print(f"🔄 [APPROVE_NEWS] Calling move_to_complete...")
        result = move_to_complete(processed_id, img_index)
        print(f"✅ [APPROVE_NEWS] Result: {result}")
        
        status_code = 404 if not result.get('success') else 200
        return jsonify(result), status_code
        
    except Exception as e:
        print(f"❌ [APPROVE_NEWS] Exception: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"📍 [APPROVE_NEWS] Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/reject', methods=['POST'])
def reject_news():
    try:
        data = request.get_json()
        
        if data is None:
            return jsonify({
                'success': False,
                'message': 'Invalid JSON format'
            }), 400
        
        processed_id = data.get('processed_id')
        
        if not processed_id:
            return jsonify({
                'success': False,
                'message': 'Missing required field: processed_id'
            }), 400
        
        result = mark_as_rejected(processed_id)
        status_code = 404 if not result.get('success') else 200
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/list', methods=['GET'])
def list_complete_news():
    try:
        result = get_all_complete_news()
        return jsonify({
            'success': True,
            'data': result,
            'count': len(result)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/list-daily', methods=['POST'])
def list_complete_news_daily():
    try:
        print("\n🔵 [LIST_COMPLETE_NEWS_DAILY] Request received")
        
        data = request.get_json()
        print(f"📥 [LIST_COMPLETE_NEWS_DAILY] Raw data: {data}")
        
        if data is None:
            print("❌ [LIST_COMPLETE_NEWS_DAILY] Invalid JSON format")
            return jsonify({
                'success': False,
                'message': 'Invalid JSON format'
            }), 400
        
        timestamp = data.get('timestamp')
        print(f"📥 [LIST_COMPLETE_NEWS_DAILY] timestamp={timestamp}")
        
        if not timestamp:
            print("❌ [LIST_COMPLETE_NEWS_DAILY] Missing timestamp")
            return jsonify({
                'success': False,
                'message': 'Missing required field: timestamp'
            }), 400
        
        result = get_complete_news_by_date(timestamp)
        print(f"✅ [LIST_COMPLETE_NEWS_DAILY] Found {len(result)} records")
        
        return jsonify({
            'success': True,
            'data': result,
            'count': len(result)
        }), 200
        
    except Exception as e:
        print(f"❌ [LIST_COMPLETE_NEWS_DAILY] Exception: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"📍 [LIST_COMPLETE_NEWS_DAILY] Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/voices/<complete_id>.mp3', methods=['GET'])
def get_voice_file(complete_id):
    """Serve voice file for a complete news item"""
    try:
        print(f"\n🔵 [GET_VOICE_FILE] Request for {complete_id}")
        
        voice_path = get_voice_file_path(complete_id)
        
        if not voice_path or not os.path.exists(voice_path):
            print(f"❌ [GET_VOICE_FILE] Voice file not found for {complete_id}")
            return jsonify({
                'success': False,
                'message': 'Voice file not found'
            }), 404
        
        print(f"✅ [GET_VOICE_FILE] Sending voice file from {voice_path}")
        return send_file(voice_path, mimetype='audio/mpeg', as_attachment=False)
        
    except Exception as e:
        print(f"❌ [GET_VOICE_FILE] Exception: {type(e).__name__}: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

def get_all_complete_news():
    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT complete_id, processed_id, raw_id, breaking, summary, 
                   description, location, reporter_id, img_url, source, voice_url,
                   created_at, approved_at
            FROM complete_news
            ORDER BY approved_at DESC
        ''')
        
        rows = cur.fetchall()
        cur.close()
        
        news_list = []
        for row in rows:
            (complete_id, processed_id, raw_id, breaking, summary, 
             description, location, reporter_id, img_url, source, voice_url,
             created_at, approved_at) = row
            
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
            
            news_list.append({
                'complete_id': complete_id,
                'processed_id': processed_id,
                'raw_id': raw_id,
                'breaking': breaking,
                'summary': summary,
                'description': description,
                'location': location,
                'reporter_id': reporter_id,
                'img_url': img_url,
                'source': source,
                'voice_url': voice_url,
                'created_at': str(created_at) if created_at else None,
                'approved_at': str(approved_at) if approved_at else None
            })
        
        return news_list
        
    except Exception as e:
        raise
    finally:
        if conn:
            db.return_connection(conn)

def get_complete_news_by_date(timestamp):
    conn = None
    try:
        from datetime import datetime
        
        print(f"🔄 [GET_COMPLETE_NEWS_BY_DATE] Parsing timestamp: {timestamp}")
        
        # Parse timestamp - handle both ISO format and other common formats
        if isinstance(timestamp, str):
            try:
                # Try ISO format first (YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD)
                if 'T' in timestamp:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                else:
                    dt = datetime.fromisoformat(timestamp)
            except:
                # Try other common formats
                try:
                    dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                except:
                    dt = datetime.strptime(timestamp, '%Y-%m-%d')
        else:
            dt = datetime.fromtimestamp(timestamp)
        
        year = dt.year
        month = dt.month
        day = dt.day
        
        print(f"✅ [GET_COMPLETE_NEWS_BY_DATE] Extracted date: {year}-{month:02d}-{day:02d}")
        
        conn = db.get_connection()
        cur = conn.cursor()
        
        # Query complete_news where created_at matches the given date
        cur.execute('''
            SELECT complete_id, processed_id, raw_id, breaking, summary, 
                   description, location, reporter_id, img_url, source, voice_url,
                   created_at, approved_at
            FROM complete_news
            WHERE EXTRACT(YEAR FROM created_at) = %s
              AND EXTRACT(MONTH FROM created_at) = %s
              AND EXTRACT(DAY FROM created_at) = %s
            ORDER BY created_at DESC
        ''', (year, month, day))
        
        rows = cur.fetchall()
        cur.close()
        
        print(f"🔍 [GET_COMPLETE_NEWS_BY_DATE] Found {len(rows)} records for {year}-{month:02d}-{day:02d}")
        
        news_list = []
        for row in rows:
            (complete_id, processed_id, raw_id, breaking, summary, 
             description, location, reporter_id, img_url, source, voice_url,
             created_at, approved_at) = row
            
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
            
            news_list.append({
                'complete_id': complete_id,
                'processed_id': processed_id,
                'raw_id': raw_id,
                'breaking': breaking,
                'summary': summary,
                'description': description,
                'location': location,
                'reporter_id': reporter_id,
                'img_url': img_url,
                'source': source,
                'voice_url': voice_url,
                'created_at': str(created_at) if created_at else None,
                'approved_at': str(approved_at) if approved_at else None
            })
        
        print(f"✅ [GET_COMPLETE_NEWS_BY_DATE] Returning {len(news_list)} records")
        return news_list
        
    except Exception as e:
        print(f"❌ [GET_COMPLETE_NEWS_BY_DATE] Exception: {type(e).__name__}: {str(e)}")
        raise
    finally:
        if conn:
            db.return_connection(conn)

def move_to_complete(processed_id, img_index=None):
    conn = None
    try:
        print(f"\n🔵 [MOVE_TO_COMPLETE] Starting for processed_id={processed_id}, img_index={img_index}")
        
        conn = db.get_connection()
        cur = conn.cursor()
        print("✅ [MOVE_TO_COMPLETE] Connection acquired")
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS complete_news (
                complete_id VARCHAR PRIMARY KEY,
                processed_id VARCHAR NOT NULL,
                raw_id VARCHAR NOT NULL,
                breaking TEXT,
                summary TEXT NOT NULL,
                description TEXT NOT NULL,
                location JSONB NOT NULL,
                reporter_id TEXT NOT NULL,
                img_url TEXT,
                source TEXT,
                is_breaking BOOLEAN,
                voice_url TEXT,
                created_at TIMESTAMP,
                approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ [MOVE_TO_COMPLETE] Table ensured")
        
        cur.execute('''
            SELECT processed_id, raw_id, breaking, summary, description, 
                   location, reporter_id, img_url, source, created_at
            FROM processed_reports
            WHERE processed_id = %s
        ''', (processed_id,))
        
        report = cur.fetchone()
        print(f"🔍 [MOVE_TO_COMPLETE] Report found: {report is not None}")
        
        if not report:
            print(f"❌ [MOVE_TO_COMPLETE] Report {processed_id} not found")
            conn.commit()
            cur.close()
            return {
                'success': False,
                'message': 'Processed report not found'
            }
        
        (p_id, raw_id, breaking, summary, description, 
         location, reporter_id, img_url, source, created_at) = report
        
        print(f"📦 [MOVE_TO_COMPLETE] Report data extracted")
        
        # Convert location JSONB to proper JSON array
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
        
        print(f"✅ [MOVE_TO_COMPLETE] Location processed: {location}")
        
        complete_id = generate_complete_id()
        print(f"✅ [MOVE_TO_COMPLETE] Generated complete_id: {complete_id}")
        
        final_img_url = None
        if img_index is not None and img_url:
            print(f"🔄 [MOVE_TO_COMPLETE] Processing image index {img_index}")
            try:
                if isinstance(img_url, list):
                    if 0 <= img_index < len(img_url):
                        final_img_url = img_url[img_index]
                        print(f"✅ [MOVE_TO_COMPLETE] Image selected: {final_img_url}")
                    else:
                        print(f"❌ [MOVE_TO_COMPLETE] Image index out of range")
                        return {
                            'success': False,
                            'message': f'Image index {img_index} out of range. Available images: 0-{len(img_url)-1}'
                        }
                else:
                    # If it's a string, parse it first
                    img_list = json.loads(img_url) if isinstance(img_url, str) else img_url
                    if isinstance(img_list, list) and 0 <= img_index < len(img_list):
                        final_img_url = img_list[img_index]
                        print(f"✅ [MOVE_TO_COMPLETE] Image selected from parsed: {final_img_url}")
                    else:
                        print(f"❌ [MOVE_TO_COMPLETE] Invalid image index or no images")
                        return {
                            'success': False,
                            'message': f'Invalid image index or no images available'
                        }
            except Exception as e:
                print(f"❌ [MOVE_TO_COMPLETE] Image processing error: {e}")
                return {
                    'success': False,
                    'message': f'Error processing image index: {str(e)}'
                }
        
        is_breaking = breaking.lower() in ['true', '1', 'yes'] if breaking else False
        print(f"✅ [MOVE_TO_COMPLETE] is_breaking: {is_breaking}")
        
        # Convert location to JSON string for JSONB insertion
        location_json = json.dumps(location) if location else json.dumps([])
        print(f"✅ [MOVE_TO_COMPLETE] location_json prepared: {location_json}")
        
        # Generate voice file from description
        print(f"🔄 [MOVE_TO_COMPLETE] Generating voice file...")
        voice_result = generate_voice_file(description, complete_id)
        voice_url = None
        if voice_result.get('success'):
            voice_url = f"/admin/voices/{complete_id}.mp3"
            print(f"✅ [MOVE_TO_COMPLETE] Voice file generated: {voice_url}")
        else:
            print(f"⚠️  [MOVE_TO_COMPLETE] Voice generation failed: {voice_result.get('message')}")
        
        print(f"🔄 [MOVE_TO_COMPLETE] Inserting into complete_news...")
        cur.execute('''
            INSERT INTO complete_news 
            (complete_id, processed_id, raw_id, breaking, summary, description, 
             location, reporter_id, img_url, source, is_breaking, voice_url, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (complete_id, p_id, raw_id, breaking, summary, description, 
              location_json, reporter_id, final_img_url, source, is_breaking, voice_url, created_at))
        print(f"✅ [MOVE_TO_COMPLETE] Inserted into complete_news")
        
        print(f"🔄 [MOVE_TO_COMPLETE] Updating processed_reports...")
        cur.execute('''
            UPDATE processed_reports
            SET is_approved = 1
            WHERE processed_id = %s
        ''', (processed_id,))
        print(f"✅ [MOVE_TO_COMPLETE] Updated processed_reports")
        
        conn.commit()
        print(f"✅ [MOVE_TO_COMPLETE] Committed transaction")
        cur.close()
        
        # Fetch the complete record to return with proper JSON
        cur2 = conn.cursor()
        cur2.execute('''SELECT complete_id, processed_id, raw_id, breaking, summary, description, location, reporter_id, img_url, source, voice_url, created_at, approved_at FROM complete_news WHERE complete_id = %s''', (complete_id,))
        complete_record = cur2.fetchone()
        cur2.close()
        print(f"✅ [MOVE_TO_COMPLETE] Fetched complete record")
        
        return_data = {
            'success': True,
            'message': 'Report approved and moved to complete_news',
            'complete_id': complete_id,
            'processed_id': processed_id
        }
        
        if complete_record:
            location_data = complete_record[6]
            if isinstance(location_data, str):
                try:
                    location_data = json.loads(location_data)
                except:
                    location_data = []
            
            return_data['data'] = {
                'complete_id': complete_record[0],
                'processed_id': complete_record[1],
                'raw_id': complete_record[2],
                'breaking': complete_record[3],
                'summary': complete_record[4],
                'description': complete_record[5],
                'location': location_data,
                'reporter_id': complete_record[7],
                'img_url': complete_record[8],
                'source': complete_record[9],
                'voice_url': complete_record[10],
                'created_at': str(complete_record[11]) if complete_record[11] else None,
                'approved_at': str(complete_record[12]) if complete_record[12] else None
            }
        
        print(f"✅ [MOVE_TO_COMPLETE] Returning success response")
        return return_data
        
    except Exception as e:
        print(f"❌ [MOVE_TO_COMPLETE] Exception: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"📍 [MOVE_TO_COMPLETE] Traceback: {traceback.format_exc()}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            db.return_connection(conn)
            print("✅ [MOVE_TO_COMPLETE] Connection returned to pool")

def mark_as_rejected(processed_id):
    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT processed_id, raw_id, breaking, summary, description, location, reporter_id, img_url, source, created_at
            FROM processed_reports
            WHERE processed_id = %s
        ''', (processed_id,))
        
        report = cur.fetchone()
        
        if not report:
            conn.commit()
            cur.close()
            return {
                'success': False,
                'message': 'Processed report not found'
            }
        
        cur.execute('''
            UPDATE processed_reports
            SET is_approved = 2
            WHERE processed_id = %s
        ''', (processed_id,))
        
        conn.commit()
        cur.close()
        
        # Convert location JSONB to proper JSON dict for response
        location_data = report[5]
        if isinstance(location_data, str):
            try:
                location_data = json.loads(location_data)
            except:
                location_data = {}
        elif location_data is None:
            location_data = {}
        
        # Convert img_url JSONB to proper JSON for response
        img_url_data = report[7]
        if isinstance(img_url_data, str):
            try:
                img_url_data = json.loads(img_url_data)
            except:
                img_url_data = None
        
        return {
            'success': True,
            'message': 'Report rejected successfully',
            'processed_id': processed_id,
            'is_approved': 2,
            'data': {
                'processed_id': report[0],
                'raw_id': report[1],
                'breaking': report[2],
                'summary': report[3],
                'description': report[4],
                'location': location_data,
                'reporter_id': report[6],
                'img_url': img_url_data,
                'source': report[8],
                'created_at': str(report[9]) if report[9] else None
            }
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            db.return_connection(conn)
