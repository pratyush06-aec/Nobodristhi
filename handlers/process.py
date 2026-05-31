import json
import string
import secrets
import threading
import time
from handlers.ml import optimize_query, update_query, check_similarity
from handlers.search import search_image
from database.pool import db


def init_tables():
    conn = None
    try:
        print("\n🔵 [INIT_TABLES] Initializing database tables")
        conn = db.get_connection()
        cur = conn.cursor()
        
        print("📊 [INIT_TABLES] Creating members table...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id VARCHAR PRIMARY KEY,
                name VARCHAR NOT NULL,
                email VARCHAR NOT NULL,
                role VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ [INIT_TABLES] Members table created")
        
        print("📊 [INIT_TABLES] Creating raw_reports table...")
        cur.execute('''
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
        print("✅ [INIT_TABLES] Raw reports table created")
        
        print("📊 [INIT_TABLES] Creating processed_reports table...")
        cur.execute('''
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
                is_approved INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ [INIT_TABLES] Processed reports table created")
        
        print("📊 [INIT_TABLES] Creating complete_news table...")
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
        print("✅ [INIT_TABLES] Complete news table created")
        
        print("📊 [INIT_TABLES] Creating templates table...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS templates (
                template_number INT PRIMARY KEY CHECK (template_number >= 1 AND template_number <= 5)
            )
        ''')
        print("✅ [INIT_TABLES] Templates table created")
        
        conn.commit()
        cur.close()
        print("✅ [INIT_TABLES] All tables initialized successfully")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ [INIT_TABLES] Error: {type(e).__name__}: {str(e)}")
        raise
    finally:
        if conn:
            db.return_connection(conn)


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
    
    def process_and_save(self, raw_id, text, location, reporter_id, img_url=None, source=None, use_update=False, existing_breaking=None, existing_summary=None, existing_description=None):
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
            
            processed_id = self._save_to_db(
                raw_id=raw_id,
                breaking=breaking,
                summary=summary,
                description=description,
                location=location,
                reporter_id=reporter_id,
                img_url=img_url,
                source=source
            )
            
            print(f"✅ [PROCESS_AND_SAVE] Report processed and saved with id: {processed_id}")
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
    
    def _is_processed(self, raw_id):
        conn = None
        try:
            conn = db.get_connection()
            cur = conn.cursor()
            
            cur.execute(
                'SELECT processed_id FROM processed_reports WHERE raw_id = %s',
                (raw_id,)
            )
            result = cur.fetchone()
            cur.close()
            
            return result is not None
            
        except Exception as e:
            return False
        finally:
            if conn:
                db.return_connection(conn)
    
    def _find_similar_processed_report(self, new_text, new_location):
        conn = None
        try:
            conn = db.get_connection()
            cur = conn.cursor()
            
            cur.execute('''
                SELECT pr.raw_id, pr.breaking, pr.summary, pr.description, pr.location,
                       rr.text
                FROM processed_reports pr
                JOIN raw_reports rr ON pr.raw_id = rr.raw_id
                ORDER BY pr.created_at DESC
            ''')
            rows = cur.fetchall()
            cur.close()
            
            new_location_dict = new_location if isinstance(new_location, dict) else {'latitude': new_location[0], 'longitude': new_location[1]}
            new_lat = new_location_dict.get('latitude')
            new_lon = new_location_dict.get('longitude')
            
            for row in rows:
                existing_location = json.loads(row[4]) if isinstance(row[4], str) else row[4]
                existing_lat = existing_location.get('latitude')
                existing_lon = existing_location.get('longitude')
                
                if all([new_lat, new_lon, existing_lat, existing_lon]):
                    if is_inside_radius(existing_lat, existing_lon, new_lat, new_lon, radius_meters=50):
                        is_similar = check_similarity(row[5], new_text)
                        
                        if is_similar:
                            return (
                                row[0],
                                row[1],
                                row[2],
                                row[3]
                            )
            
            return None
            
        except Exception as e:
            return None
        finally:
            if conn:
                db.return_connection(conn)
    
    def _save_to_db(self, raw_id, breaking, summary, description, location, reporter_id, img_url=None, source=None):
        conn = None
        try:
            conn = db.get_connection()
            cur = conn.cursor()
            
            img_url_jsonb = json.dumps(img_url) if img_url else json.dumps([])
            
            characters = string.ascii_letters + string.digits
            processed_id = ''.join(secrets.choice(characters) for _ in range(16))
            
            cur.execute('''
                INSERT INTO processed_reports 
                (processed_id, raw_id, breaking, summary, description, location, reporter_id, img_url, source, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ''', (processed_id, raw_id, breaking, summary, description, json.dumps(location), reporter_id, img_url_jsonb, source))
            
            conn.commit()
            cur.close()
            
            return processed_id
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                db.return_connection(conn)


class ProcessingTask:
    def __init__(self):
        self.processor = RawProcessor()
        self.running = False
        self.thread = None
    
    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def run(self):
        """Main background processing loop"""
        while self.running:
            try:
                self._process_batch()
                time.sleep(10)
            except Exception as e:
                time.sleep(10)
    
    def _process_batch(self):
        conn = None
        try:
            conn = db.get_connection()
            cur = conn.cursor()
            
            cur.execute('''
                SELECT raw_id, text, location, reporter_id, img_url, source
                FROM raw_reports
                ORDER BY created_at DESC
            ''')
            rows = cur.fetchall()
            cur.close()
            
            for row in rows:
                raw_id = row[0]
                
                is_processed = self.processor._is_processed(raw_id)
                
                if not is_processed:
                    location = json.loads(row[2]) if isinstance(row[2], str) else row[2]
                    
                    similar_report = self.processor._find_similar_processed_report(row[1], location)
                    
                    if similar_report:
                        original_raw_id, existing_breaking, existing_summary, existing_description = similar_report
                        
                        result = self.processor.process_and_save(
                            raw_id=raw_id,
                            text=row[1],
                            location=location,
                            reporter_id=row[3],
                            img_url=row[4],
                            source=row[5],
                            use_update=True,
                            existing_breaking=existing_breaking,
                            existing_summary=existing_summary,
                            existing_description=existing_description
                        )
                    else:
                        result = self.processor.process_and_save(
                            raw_id=raw_id,
                            text=row[1],
                            location=location,
                            reporter_id=row[3],
                            img_url=row[4],
                            source=row[5]
                        )
            
        except Exception as e:
            pass
        finally:
            if conn:
                db.return_connection(conn)


processing_task = ProcessingTask()


