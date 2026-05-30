import asyncpg 
import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

class Database:
    def __init__(self):
        self.token_pool = None
        self.supabase_client = None

    async def connect(self):
        # Validate required environment variables
        host = os.getenv('POSTGRES_TOKEN_HOST')
        port = os.getenv('POSTGRES_TOKEN_PORT')
        user = os.getenv('POSTGRES_TOKEN_USER')
        password = os.getenv('POSTGRES_TOKEN_PASSWORD')
        
        if not all([host, port, user, password]):
            print("Error: Missing PostgreSQL environment variables:")
            print(f"  POSTGRES_TOKEN_HOST: {'✓' if host else '✗ MISSING'}")
            print(f"  POSTGRES_TOKEN_PORT: {'✓' if port else '✗ MISSING'}")
            print(f"  POSTGRES_TOKEN_USERNAME: {'✓' if user else '✗ MISSING'}")
            print(f"  POSTGRES_TOKEN_PASSWORD: {'✓' if password else '✗ MISSING'}")
            raise ValueError("Missing required PostgreSQL credentials in .env file")
        
        self.token_pool = await asyncpg.create_pool(
            host=host,
            port=int(port),
            database='postgres',
            user=user,
            password=password,
            ssl='require',
            timeout=10,
            min_size=1,
            max_size=20,
            command_timeout=30,
            statement_cache_size=0
        )
        
        try:
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_KEY')
            
            if not supabase_url or not supabase_key:
                print("Warning: SUPABASE_URL or SUPABASE_KEY not set in environment")
                self.supabase_client = None
            else:
                self.supabase_client = create_client(supabase_url, supabase_key)
                print("Supabase client initialized successfully")
        except Exception as e:
            print(f"Error initializing Supabase client: {e}")
            self.supabase_client = None

    async def refresh_connection(self):
        while True:
            try:
                await asyncio.sleep(30)
                async with self.token_pool.acquire() as connection:
                    await connection.fetchval('SELECT 1')
                
                if self.supabase_client:
                    try:
                        self.supabase_client.storage.list_buckets()
                    except Exception as bucket_error:
                        self.supabase_client = create_client(
                            os.getenv('SUPABASE_URL'),
                            os.getenv('SUPABASE_KEY')
                        )
            except Exception as e:
                try:
                    if self.token_pool:
                        await self.token_pool.close()
                    await self.connect()
                except Exception as reconnect_error:
                    await asyncio.sleep(10)

    async def close(self):
        if self.token_pool:
            await self.token_pool.close()
        if self.supabase_client:
            self.supabase_client = None

db = Database()

