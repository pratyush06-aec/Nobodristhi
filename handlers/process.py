import asyncio
import json
import string
import random
from handlers.ml import optimize_query, update_query, check_similarity
from handlers.search import search_image
from database.pool import db


async def init_tables():
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
        
        await connection.execute('''
            CREATE TABLE IF NOT EXISTS processed_reports (
                processed_id VARCHAR PRIMARY KEY,
                raw_id VARCHAR NOT NULL UNIQUE,
                breaking TEXT,
                summary TEXT NOT NULL,
                description TEXT NOT NULL,
                location JSONB NOT NULL,
                reporter_id TEXT NOT NULL,
                img_url JSONB,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    

from math import radians, sin, cos, sqrt, atan2

def is_inside_radius(
    center_lat,
    center_lon,
    check_lat,
    check_lon,
    radius_meters=50
):
    R = 6371000  

    dlat = radians(check_lat - center_lat)
    dlon = radians(check_lon - center_lon)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(center_lat))
        * cos(radians(check_lat))
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance <= radius_meters


result = is_inside_radius(
    center_lat=62.32,
    center_lon=112.34,
    check_lat=62.3202,
    check_lon=112.3401
)

class RawProcessor:
    def __init__(self):
        pass
    
    async def process_and_save(self, raw_id, text, location, reporter_id, img_url=None, source=None, use_update=False, existing_breaking=None, existing_summary=None, existing_description=None):
        try:
            if use_update and all([existing_breaking is not None, existing_summary, existing_description]):
                optimized_result = update_query(text, existing_breaking, existing_summary, existing_description)
            else:
                optimized_result = optimize_query(text)
            
            if 'error' in optimized_result:
                return {
                    'success': False,
                    'message': f"Failed to optimize query: {optimized_result['error']}"
                }
            
            try:
                if isinstance(optimized_result, str):
                    optimized_data = json.loads(optimized_result)
                else:
                    optimized_data = optimized_result
            except json.JSONDecodeError:
                return {
                    'success': False,
                    'message': 'ML response is not valid JSON format'
                }
            
            if not optimized_data:
                return {
                    'success': False,
                    'message': 'ML response is empty'
                }
            
            breaking = optimized_data.get('breaking')
            summary = optimized_data.get('summary')
            description = optimized_data.get('description')
            
            if summary is None or description is None:
                return {
                    'success': False,
                    'message': 'ML response missing required fields: summary and/or description'
                }
            
            if not img_url and breaking:
                search_results = search_image(breaking)
                img_url = search_results if search_results else []
            
            processed_id = await self._save_to_db(
                raw_id=raw_id,
                breaking=breaking,
                summary=summary,
                description=description,
                location=location,
                reporter_id=reporter_id,
                img_url=img_url,
                source=source
            )
            
            return {
                'success': True,
                'message': 'Report processed and saved successfully',
                'processed_id': processed_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }
    
    async def _is_processed(self, raw_id):
        async with db.token_pool.acquire() as connection:
            result = await connection.fetchval(
                'SELECT processed_id FROM processed_reports WHERE raw_id = $1',
                raw_id
            )
            return result is not None
    
    async def _find_similar_processed_report(self, new_text, new_location):
        try:
            async with db.token_pool.acquire() as connection:
                processed_reports = await connection.fetch('''
                    SELECT pr.raw_id, pr.breaking, pr.summary, pr.description, pr.location,
                           rr.text
                    FROM processed_reports pr
                    JOIN raw_reports rr ON pr.raw_id = rr.raw_id
                    ORDER BY pr.created_at DESC
                ''')
            
            new_lat = new_location.get('latitude')
            new_lon = new_location.get('longitude')
            
            for report in processed_reports:
                existing_location = json.loads(report['location']) if isinstance(report['location'], str) else report['location']
                existing_lat = existing_location.get('latitude')
                existing_lon = existing_location.get('longitude')
                
                if all([new_lat, new_lon, existing_lat, existing_lon]):
                    if is_inside_radius(existing_lat, existing_lon, new_lat, new_lon, radius_meters=50):
                        is_similar = check_similarity(report['text'], new_text)
                        
                        if is_similar:
                            return (
                                report['raw_id'],
                                report['breaking'],
                                report['summary'],
                                report['description']
                            )
            
            return None
        except Exception as e:
            print(f"Error finding similar processed report: {e}")
            return None
    
    async def _save_to_db(self, raw_id, breaking, summary, description, location, reporter_id, img_url=None, source=None):
        async with db.token_pool.acquire() as connection:
            img_url_jsonb = json.dumps(img_url) if img_url else []
            
            characters = string.ascii_letters + string.digits
            processed_id = ''.join(random.choice(characters) for _ in range(16))
            
            await connection.execute('''
                INSERT INTO processed_reports 
                (processed_id, raw_id, breaking, summary, description, location, reporter_id, img_url, source, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, CURRENT_TIMESTAMP)
            ''', processed_id, raw_id, breaking, summary, description, json.dumps(location), reporter_id, img_url_jsonb, source)
            
            return processed_id


class ProcessingTask:
    def __init__(self):
        self.processor = RawProcessor()
        self.running = False
    
    async def start(self):
        self.running = True
        await self.run()
    
    async def stop(self):
        self.running = False
    
    async def run(self):
        while self.running:
            try:
                await self._process_batch()
                await asyncio.sleep(10)
            except Exception as e:
                print(f"Error in processing task: {e}")
                await asyncio.sleep(10)
    
    async def _process_batch(self):
        async with db.token_pool.acquire() as connection:
            raw_reports = await connection.fetch('''
                SELECT raw_id, text, location, reporter_id, img_url, source
                FROM raw_reports
                ORDER BY created_at DESC
            ''')
        
        for report in raw_reports:
            raw_id = report['raw_id']
            
            is_processed = await self.processor._is_processed(raw_id)
            
            if not is_processed:
                location = json.loads(report['location']) if isinstance(report['location'], str) else report['location']
                
                similar_report = await self.processor._find_similar_processed_report(report['text'], location)
                
                if similar_report:
                    original_raw_id, existing_breaking, existing_summary, existing_description = similar_report
                    print(f"Found similar report {original_raw_id} for new raw report {raw_id}. Using update_query.")
                    
                    result = await self.processor.process_and_save(
                        raw_id=raw_id,
                        text=report['text'],
                        location=location,
                        reporter_id=report['reporter_id'],
                        img_url=report['img_url'],
                        source=report['source'],
                        use_update=True,
                        existing_breaking=existing_breaking,
                        existing_summary=existing_summary,
                        existing_description=existing_description
                    )
                else:
                    result = await self.processor.process_and_save(
                        raw_id=raw_id,
                        text=report['text'],
                        location=location,
                        reporter_id=report['reporter_id'],
                        img_url=report['img_url'],
                        source=report['source']
                    )
                
                if result.get('success'):
                    print(f"Successfully processed report: {raw_id}")
                else:
                    print(f"Failed to process report {raw_id}: {result.get('message')}")


processing_task = ProcessingTask()

