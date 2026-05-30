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
        self.token_pool = await asyncpg.create_pool(
            host=os.getenv('POSTGRES_TOKEN_HOST'),
            port=int(os.getenv('POSTGRES_TOKEN_PORT')),
            database='postgres',
            user=os.getenv('POSTGRES_TOKEN_USERNAME'),
            password=os.getenv('POSTGRES_TOKEN_PASSWORD'),
            ssl='require',
            timeout=10,
            min_size=1,
            max_size=20,
            command_timeout=30,
            statement_cache_size=0
        )
        
        self.supabase_client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )

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

