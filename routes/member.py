from flask import Blueprint, request, jsonify
import asyncio
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
        
        result = asyncio.run(save_member(member_id, name, email, role))
        
        status_code = 409 if not result.get('success') else 201
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
            }), 500

async def save_member(member_id, name, email, role):
    async with db.token_pool.acquire() as connection:
        await connection.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id VARCHAR PRIMARY KEY,
                name VARCHAR NOT NULL,
                email VARCHAR NOT NULL,
                role VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        existing_member = await connection.fetchrow(
            'SELECT id FROM members WHERE id = $1',
            member_id
        )
        
        if existing_member:
            return {
                "success": True,
                'message': 'Member already exists'
            }
        
        await connection.execute('''
            INSERT INTO members (id, name, email, role, created_at)
            VALUES ($1, $2, $3, $4, CURRENT_TIMESTAMP)
        ''', member_id, name, email, role)
    
    return {
        "success": True,
        'message': 'Member saved successfully'
    }

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
        
        result = asyncio.run(delete_member(member_id))
        
        status_code = 404 if not result.get('success') else 200
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
            }), 500

async def delete_member(member_id):
    async with db.token_pool.acquire() as connection:
        existing_member = await connection.fetchrow(
            'SELECT id FROM members WHERE id = $1',
            member_id
        )
        
        if not existing_member:
            return {
                "success": False,
                'message': 'Member not found'
            }
        
        await connection.execute(
            'DELETE FROM members WHERE id = $1',
            member_id
        )
    
    return {
        "success": True,
        'message': 'Member deleted successfully'
    }
