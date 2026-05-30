from flask import Blueprint, request, jsonify
import asyncio
import json
from database.pool import db
import nest_asyncio

# Allow nested event loops for Flask async operations
nest_asyncio.apply()

bp = Blueprint('processed', __name__, url_prefix='/processed')

def run_async(coro):
    """Helper function to run async code safely in Flask context"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

@bp.route('/', methods=['GET'])
def get_all_processed():
    try:
        result = run_async(fetch_all_processed_reports())
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
            }), 500

async def fetch_all_processed_reports():
    async with db.token_pool.acquire() as connection:
        reports = await connection.fetch('''
            SELECT processed_id, raw_id, breaking, summary, description, location, reporter_id, img_url, source, created_at
            FROM processed_reports
            ORDER BY created_at DESC
        ''')
    
    reports_list = []
    for report in reports:
        reports_list.append({
            'processed_id': report['processed_id'],
            'raw_id': report['raw_id'],
            'breaking': report['breaking'],
            'summary': report['summary'],
            'description': report['description'],
            'location': json.loads(report['location']) if report['location'] else None,
            'reporter_id': report['reporter_id'],
            'img_url': json.loads(report['img_url']) if report['img_url'] else None,
            'source': report['source'],
            'created_at': report['created_at'].isoformat() if report['created_at'] else None
        })
    
    return {
        "success": True,
        'message': 'Processed reports retrieved successfully',
        'data': reports_list
    }

@bp.route('/delete', methods=['POST'])
def delete():
    try:
        data = request.get_json()
        processed_id = data.get('processed_id')
        
        if not processed_id:
            return jsonify({
                'success': False,
                'message': 'Missing required field: processed_id'
                }), 400
        
        result = run_async(delete_processed_report(processed_id))
        
        status_code = 404 if not result.get('success') else 200
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
            }), 500

@bp.route('/report', methods=['POST'])
def report():
    try:
        data = request.get_json()
        processed_id = data.get('processed_id')
        
        if not processed_id:
            return jsonify({
                'success': False,
                'message': 'Missing required field: processed_id'
                }), 400
        
        result = run_async(fetch_processed_report_by_id(processed_id))
        
        if not result.get('success'):
            return jsonify(result), 404
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
            }), 500

async def fetch_processed_report_by_id(processed_id):
    async with db.token_pool.acquire() as connection:
        report = await connection.fetchrow('''
            SELECT processed_id, raw_id, breaking, summary, description, location, reporter_id, img_url, source, created_at
            FROM processed_reports
            WHERE processed_id = $1
        ''', processed_id)
    
    if not report:
        return {
            "success": False,
            'message': 'Processed report not found'
        }
    
    return {
        "success": True,
        'message': 'Processed report retrieved successfully',
        'data': {
            'processed_id': report['processed_id'],
            'raw_id': report['raw_id'],
            'breaking': report['breaking'],
            'summary': report['summary'],
            'description': report['description'],
            'location': json.loads(report['location']) if report['location'] else None,
            'reporter_id': report['reporter_id'],
            'img_url': json.loads(report['img_url']) if report['img_url'] else None,
            'source': report['source'],
            'created_at': report['created_at'].isoformat() if report['created_at'] else None
        }
    }

async def delete_processed_report(processed_id):
    async with db.token_pool.acquire() as connection:
        existing_report = await connection.fetchrow(
            'SELECT processed_id FROM processed_reports WHERE processed_id = $1',
            processed_id
        )
        
        if not existing_report:
            return {
                "success": False,
                'message': 'Processed report not found'
            }
        
        await connection.execute(
            'DELETE FROM processed_reports WHERE processed_id = $1',
            processed_id
        )
    
    return {
        "success": True,
        'message': 'Processed report deleted successfully'
    }
