from flask import Blueprint, request, jsonify
import asyncio
import string
import random
import io
import json
from database.pool import db

bp = Blueprint('raw', __name__, url_prefix='/raw')

@bp.route('/report', methods=['POST'])
async def report():
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
            img_url = await upload_image_to_supabase(img_file)
            if not img_url:
                return jsonify({
                    'success': False,
                    'message': 'Failed to upload image'
                    }), 500
        
        result = await save_raw_report(text, location, reporter_id, img_url, source)
        
        status_code = 201 if result.get('success') else 500
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
            }), 500

async def upload_image_to_supabase(img_file):
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

async def save_raw_report(text, location, reporter_id, img_url=None, source=None):
    async with db.token_pool.acquire() as connection:
        await connection.execute('''
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
        
        await connection.execute('''
            INSERT INTO raw_reports (raw_id, text, location, reporter_id, img_url, source, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, CURRENT_TIMESTAMP)
        ''', raw_id, text, json.dumps(location), reporter_id, img_url, source)
    
    return {
        "success": True,
        'message': 'Raw report saved successfully'
    }

@bp.route('/', methods=['GET'])
async def get_all_reports():
    try:
        result = await fetch_all_raw_reports()
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
            }), 500

async def fetch_all_raw_reports():
    async with db.token_pool.acquire() as connection:
        await connection.execute('''
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
        
        reports = await connection.fetch('''
            SELECT raw_id, text, location, reporter_id, img_url, source, created_at
            FROM raw_reports
            ORDER BY created_at DESC
        ''')
    
    reports_list = []
    for report in reports:
        reports_list.append({
            'raw_id': report['raw_id'],
            'text': report['text'],
            'location': json.loads(report['location']) if report['location'] else None,
            'reporter_id': report['reporter_id'],
            'img_url': report['img_url'],
            'source': report['source'],
            'created_at': report['created_at'].isoformat() if report['created_at'] else None
        })
    
    return {
        "success": True,
        'message': 'Reports retrieved successfully',
        'data': reports_list
    }

@bp.route('/delete', methods=['POST'])
async def delete():
    try:
        data = request.get_json()
        raw_id = data.get('raw_id')
        
        if not raw_id:
            return jsonify({
                'success': False,
                'message': 'Missing required field: raw_id'
                }), 400
        
        result = await delete_raw_report(raw_id)
        
        status_code = 404 if not result.get('success') else 200
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
            }), 500

async def delete_raw_report(raw_id):
    async with db.token_pool.acquire() as connection:
        existing_report = await connection.fetchrow(
            'SELECT raw_id FROM raw_reports WHERE raw_id = $1',
            raw_id
        )
        
        if not existing_report:
            return {
                "success": False,
                'message': 'Report not found'
            }
        
        await connection.execute(
            'DELETE FROM raw_reports WHERE raw_id = $1',
            raw_id
        )
    
    return {
        "success": True,
        'message': 'Report deleted successfully'
    }
