from flask import Blueprint, request, jsonify
from database.pool import db

bp = Blueprint('member', __name__, url_prefix='/member')

@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        member_id = data.get('id')
        name = data.get('name')
        email = data.get('email')
        role = data.get('role')
        
        if not all([member_id, name, email, role]):
            return jsonify({
                'success': False,
                'message': 'Missing required fields: id, name, email, role'
            }), 400
        
        result = save_member(member_id, name, email, role)
        status_code = 409 if not result.get('success') else 201
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

def save_member(member_id, name, email, role):
    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id VARCHAR PRIMARY KEY,
                name VARCHAR NOT NULL,
                email VARCHAR NOT NULL,
                role VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cur.execute('SELECT id FROM members WHERE id = %s', (member_id,))
        existing_member = cur.fetchone()
        
        if existing_member:
            conn.commit()
            return {
                "success": True,
                'message': 'Member already exists'
            }
        
        cur.execute('''
            INSERT INTO members (id, name, email, role, created_at)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
        ''', (member_id, name, email, role))
        conn.commit()
        
        cur.close()
        return {
            "success": True,
            'message': 'Member saved successfully'
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            db.return_connection(conn)

@bp.route('/delete', methods=['POST'])
def delete():
    try:
        data = request.get_json()
        member_id = data.get('id')
        
        if not member_id:
            return jsonify({
                'success': False,
                'message': 'Missing required field: id'
            }), 400
        
        result = delete_member(member_id)
        status_code = 404 if not result.get('success') else 200
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

def delete_member(member_id):
    """Delete member from database"""
    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT id FROM members WHERE id = %s', (member_id,))
        existing_member = cur.fetchone()
        
        if not existing_member:
            return {
                "success": False,
                'message': 'Member not found'
            }
        
        cur.execute('DELETE FROM members WHERE id = %s', (member_id,))
        conn.commit()
        
        cur.close()
        return {
            "success": True,
            'message': 'Member deleted successfully'
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            db.return_connection(conn)
