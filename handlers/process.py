import asyncio
import json
import string
import random
from handlers.ml import optimize_query
from handlers.search import search_image
from database.pool import db


async def init_tables():
    async with db.token_pool.acquire() as connection:
        await connection.execute('''
            CREATE TABLE IF NOT EXISTS raw_reports (
                raw_id VARCHAR PRIMARY KEY,
                text TEXT NOT NULL,
                location JSONB NOT NULL,
                reporter_id VARCHAR NOT NULL,
                img_url JSONB,
                source VARCHAR,
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
    


class RawProcessor:
    def __init__(self):
        pass
    
    async def process_and_save(self, raw_id, text, location, reporter_id, img_url=None, source=None):
        try:
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
    
    async def _save_to_db(self, raw_id, breaking, summary, description, location, reporter_id, img_url=None, source=None):
        async with db.token_pool.acquire() as connection:
            img_url_jsonb = json.dumps(img_url) if img_url else []
            
            # Generate 16-character processed_id
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

