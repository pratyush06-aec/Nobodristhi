from flask import Blueprint, request, jsonify
from database.pool import db

bp = Blueprint('template', __name__, url_prefix='/template')

def init_table():
    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS templates (
                template_number INT PRIMARY KEY CHECK (template_number >= 1 AND template_number <= 5)
            )
        ''')
        conn.commit()
        cur.close()
    except Exception as e:
        if conn:
            conn.rollback()
    finally:
        if conn:
            db.return_connection(conn)

init_table()

@bp.route('/save', methods=['POST'])
def save_template():
    """Save template number"""
    try:
        print("\n🔵 [SAVE_TEMPLATE] Request received")
        
        data = request.get_json()
        
        if not data:
            print("❌ [SAVE_TEMPLATE] Invalid JSON")
            return jsonify({'success': False, 'message': 'Invalid JSON'}), 400
        
        template_number = data.get('template_number')
        
        if not template_number:
            print("❌ [SAVE_TEMPLATE] Missing template_number")
            return jsonify({'success': False, 'message': 'Missing template_number'}), 400
        
        # Validate it's an integer
        try:
            template_num = int(template_number)
        except (ValueError, TypeError):
            print(f"❌ [SAVE_TEMPLATE] Invalid template_number type")
            return jsonify({'success': False, 'message': 'template_number must be an integer'}), 400
        
        # Validate range 1-5
        if template_num < 1 or template_num > 5:
            print(f"❌ [SAVE_TEMPLATE] Out of range: {template_num}")
            return jsonify({'success': False, 'message': 'template_number must be between 1 and 5'}), 400
        
        # Save to database
        conn = None
        try:
            conn = db.get_connection()
            cur = conn.cursor()
            
            # Check if exists
            cur.execute('SELECT template_number FROM templates WHERE template_number = %s', (template_num,))
            exists = cur.fetchone()
            
            if exists:
                # Delete old, insert new
                cur.execute('DELETE FROM templates WHERE template_number != %s', (template_num,))
                print(f"🔄 [SAVE_TEMPLATE] Cleared other templates")
            else:
                # Clear all, insert this one
                cur.execute('DELETE FROM templates')
                print(f"🔄 [SAVE_TEMPLATE] Cleared table")
            
            cur.execute('INSERT INTO templates (template_number) VALUES (%s)', (template_num,))
            conn.commit()
            cur.close()
            
            print(f"✅ [SAVE_TEMPLATE] Template {template_num} saved")
            return jsonify({'success': True, 'template_number': template_num}), 200
            
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ [SAVE_TEMPLATE] DB Error: {str(e)}")
            return jsonify({'success': False, 'message': str(e)}), 500
        finally:
            if conn:
                db.return_connection(conn)
    
    except Exception as e:
        print(f"❌ [SAVE_TEMPLATE] Exception: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/get', methods=['GET'])
def get_template():
    try:
        print("\n🔵 [GET_TEMPLATE] Request received")
        
        conn = None
        try:
            conn = db.get_connection()
            cur = conn.cursor()
            
            cur.execute('SELECT template_number FROM templates LIMIT 1')
            row = cur.fetchone()
            cur.close()
            
            if not row:
                print("❌ [GET_TEMPLATE] No template found")
                return jsonify({'success': False, 'message': 'No template saved'}), 404
            
            template_num = row[0]
            print(f"✅ [GET_TEMPLATE] Template {template_num} fetched")
            return jsonify({'success': True, 'template_number': template_num}), 200
            
        except Exception as e:
            print(f"❌ [GET_TEMPLATE] DB Error: {str(e)}")
            return jsonify({'success': False, 'message': str(e)}), 500
        finally:
            if conn:
                db.return_connection(conn)
    
    except Exception as e:
        print(f"❌ [GET_TEMPLATE] Exception: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500
