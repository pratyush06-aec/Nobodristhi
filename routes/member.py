from flask import Blueprint, request, jsonify
from database.pool import db

bp = Blueprint('member', __name__, url_prefix='/member')

@bp.route('/login', methods=['POST'])
def login():
    try:
        print("\n🔵 [MEMBER LOGIN] Request received")
        
        print("📥 [MEMBER LOGIN] Parsing JSON data...")
        data = request.get_json()
        print(f"✅ [MEMBER LOGIN] JSON parsed successfully: {data}")
        
        print("📋 [MEMBER LOGIN] Extracting fields...")
        member_id = data.get('id')
        name = data.get('name')
        email = data.get('email')
        role = data.get('role')
        print(f"✅ [MEMBER LOGIN] Fields extracted - ID: {member_id}, Name: {name}, Email: {email}, Role: {role}")
        
        print("🔍 [MEMBER LOGIN] Validating required fields...")
        if not all([member_id, name, email, role]):
            print("❌ [MEMBER LOGIN] Validation failed - Missing required fields")
            return jsonify({
                'success': False,
                'message': 'Missing required fields: id, name, email, role'
            }), 400
        print("✅ [MEMBER LOGIN] All fields validated successfully")
        
        print("💾 [MEMBER LOGIN] Calling save_member function...")
        result = save_member(member_id, name, email, role)
        print(f"✅ [MEMBER LOGIN] save_member completed: {result}")
        
        status_code = 409 if not result.get('success') else 201
        print(f"📤 [MEMBER LOGIN] Returning response with status code: {status_code}")
        return jsonify(result), status_code
        
    except Exception as e:
        print(f"❌ [MEMBER LOGIN] Exception occurred: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"📍 [MEMBER LOGIN] Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

def save_member(member_id, name, email, role):
    """Save member to database"""
    conn = None
    try:
        print(f"\n🔵 [SAVE_MEMBER] Starting save_member for member_id: {member_id}")
        
        print("🔌 [SAVE_MEMBER] Getting database connection...")
        conn = db.get_connection()
        cur = conn.cursor()
        print("✅ [SAVE_MEMBER] Database connection acquired")
        
        print("📊 [SAVE_MEMBER] Creating members table if not exists...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id VARCHAR PRIMARY KEY,
                name VARCHAR NOT NULL,
                email VARCHAR NOT NULL,
                role VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ [SAVE_MEMBER] Table creation/verification completed")
        
        print(f"🔍 [SAVE_MEMBER] Checking if member {member_id} already exists...")
        cur.execute('SELECT id FROM members WHERE id = %s', (member_id,))
        existing_member = cur.fetchone()
        
        if existing_member:
            print(f"⚠️  [SAVE_MEMBER] Member {member_id} already exists")
            conn.commit()
            return {
                "success": True,
                'message': 'Member already exists'
            }
        print(f"✅ [SAVE_MEMBER] Member {member_id} is new - proceeding with insert")
        
        print(f"➕ [SAVE_MEMBER] Inserting new member: {member_id}")
        cur.execute('''
            INSERT INTO members (id, name, email, role, created_at)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
        ''', (member_id, name, email, role))
        conn.commit()
        print(f"✅ [SAVE_MEMBER] Member {member_id} inserted successfully")
        
        cur.close()
        return {
            "success": True,
            'message': 'Member saved successfully'
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ [SAVE_MEMBER] Exception occurred: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"📍 [SAVE_MEMBER] Traceback: {traceback.format_exc()}")
        raise
    finally:
        if conn:
            db.return_connection(conn)
            print("✅ [SAVE_MEMBER] Connection returned to pool")

@bp.route('/delete', methods=['POST'])
def delete():
    try:
        print("\n🔵 [MEMBER DELETE] Request received")
        
        print("📥 [MEMBER DELETE] Parsing JSON data...")
        data = request.get_json()
        print(f"✅ [MEMBER DELETE] JSON parsed successfully")
        
        print("📋 [MEMBER DELETE] Extracting member_id...")
        member_id = data.get('id')
        print(f"✅ [MEMBER DELETE] member_id extracted: {member_id}")
        
        print("🔍 [MEMBER DELETE] Validating member_id...")
        if not member_id:
            print("❌ [MEMBER DELETE] Validation failed - Missing member_id")
            return jsonify({
                'success': False,
                'message': 'Missing required field: id'
            }), 400
        print("✅ [MEMBER DELETE] member_id validated successfully")
        
        print("🗑️  [MEMBER DELETE] Calling delete_member function...")
        result = delete_member(member_id)
        print(f"✅ [MEMBER DELETE] delete_member completed: {result}")
        
        status_code = 404 if not result.get('success') else 200
        print(f"📤 [MEMBER DELETE] Returning response with status code: {status_code}")
        return jsonify(result), status_code
        
    except Exception as e:
        print(f"❌ [MEMBER DELETE] Exception occurred: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"📍 [MEMBER DELETE] Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

def delete_member(member_id):
    """Delete member from database"""
    conn = None
    try:
        print(f"\n🔵 [DELETE_MEMBER] Starting delete_member for member_id: {member_id}")
        
        print("🔌 [DELETE_MEMBER] Getting database connection...")
        conn = db.get_connection()
        cur = conn.cursor()
        print("✅ [DELETE_MEMBER] Database connection acquired")
        
        print(f"🔍 [DELETE_MEMBER] Checking if member {member_id} exists...")
        cur.execute('SELECT id FROM members WHERE id = %s', (member_id,))
        existing_member = cur.fetchone()
        
        if not existing_member:
            print(f"❌ [DELETE_MEMBER] Member {member_id} not found")
            return {
                "success": False,
                'message': 'Member not found'
            }
        print(f"✅ [DELETE_MEMBER] Member {member_id} found - proceeding with delete")
        
        print(f"🗑️  [DELETE_MEMBER] Deleting member {member_id}...")
        cur.execute('DELETE FROM members WHERE id = %s', (member_id,))
        conn.commit()
        print(f"✅ [DELETE_MEMBER] Member {member_id} deleted successfully")
        
        cur.close()
        return {
            "success": True,
            'message': 'Member deleted successfully'
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ [DELETE_MEMBER] Exception occurred: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"📍 [DELETE_MEMBER] Traceback: {traceback.format_exc()}")
        raise
    finally:
        if conn:
            db.return_connection(conn)
            print("✅ [DELETE_MEMBER] Connection returned to pool")
