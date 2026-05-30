from flask import Blueprint, request, jsonify
from database.pool import db
import json
import string
import secrets

bp = Blueprint('admin', __name__, url_prefix='/admin')

def generate_complete_id():
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(16))

@bp.route('/approve', methods=['GET'])
def approve_news():
    try:
        processed_id = request.args.get('processed_id')
        
        if not processed_id:
            return jsonify({
                'success': False,
                'message': 'Missing required parameter: processed_id'
            }), 400
        
        result = move_to_complete(processed_id)
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

def get_all_complete_news():
    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT complete_id, processed_id, raw_id, breaking, summary, 
                   description, location, reporter_id, img_url, source, 
                   created_at, approved_at
            FROM complete_news
            ORDER BY approved_at DESC
        ''')
        
        rows = cur.fetchall()
        cur.close()
        
        news_list = []
        for row in rows:
            (complete_id, processed_id, raw_id, breaking, summary, 
             description, location, reporter_id, img_url, source, 
             created_at, approved_at) = row
            
            if isinstance(location, str):
                try:
                    location = json.loads(location)
                except:
                    location = {}
            
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
                'created_at': str(created_at) if created_at else None,
                'approved_at': str(approved_at) if approved_at else None
            })
        
        return news_list
        
    except Exception as e:
        raise
    finally:
        if conn:
            db.return_connection(conn)

def move_to_complete(processed_id):
    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        
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
                created_at TIMESTAMP,
                approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cur.execute('''
            SELECT processed_id, raw_id, breaking, summary, description, 
                   location, reporter_id, img_url, source, created_at
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
        
        (p_id, raw_id, breaking, summary, description, 
         location, reporter_id, img_url, source, created_at) = report
        
        complete_id = generate_complete_id()
        
        is_breaking = breaking.lower() in ['true', '1', 'yes'] if breaking else False
        
        cur.execute('''
            INSERT INTO complete_news 
            (complete_id, processed_id, raw_id, breaking, summary, description, 
             location, reporter_id, img_url, source, is_breaking, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (complete_id, p_id, raw_id, breaking, summary, description, 
              location, reporter_id, img_url, source, is_breaking, created_at))
        
        cur.execute('''
            UPDATE processed_reports
            SET is_approved = 1
            WHERE processed_id = %s
        ''', (processed_id,))
        
        conn.commit()
        cur.close()
        
        return {
            'success': True,
            'message': 'Report approved and moved to complete_news',
            'complete_id': complete_id,
            'processed_id': processed_id
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            db.return_connection(conn)
