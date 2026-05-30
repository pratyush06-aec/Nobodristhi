import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

class Database:
    def __init__(self):
        self.conn_pool = None
        self.supabase_client = None

    def connect(self):
        """Create synchronous connection pool"""
        try:
            host = os.getenv('POSTGRES_TOKEN_HOST')
            port = os.getenv('POSTGRES_TOKEN_PORT')
            user = os.getenv('POSTGRES_TOKEN_USER')
            password = os.getenv('POSTGRES_TOKEN_PASSWORD')
            
            if not all([host, port, user, password]):
                print("❌ Error: Missing PostgreSQL credentials")
                print(f"  POSTGRES_TOKEN_HOST: {'✓' if host else '✗ MISSING'}")
                print(f"  POSTGRES_TOKEN_PORT: {'✓' if port else '✗ MISSING'}")
                print(f"  POSTGRES_TOKEN_USER: {'✓' if user else '✗ MISSING'}")
                print(f"  POSTGRES_TOKEN_PASSWORD: {'✓' if password else '✗ MISSING'}")
                self.conn_pool = None
                return
            
            self.conn_pool = pool.SimpleConnectionPool(
                minconn=2,
                maxconn=20,
                host=host,
                port=int(port),
                database='postgres',
                user=user,
                password=password,
                sslmode='require',
                connect_timeout=10
            )
            print("✅ PostgreSQL connection pool created successfully")
            
        except Exception as e:
            print(f"❌ Error creating connection pool: {type(e).__name__}: {e}")
            self.conn_pool = None
        
        # Initialize Supabase
        try:
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_KEY')
            
            if not supabase_url or not supabase_key:
                print("⚠️  Supabase not configured (SUPABASE_URL or SUPABASE_KEY missing)")
                self.supabase_client = None
            else:
                self.supabase_client = create_client(supabase_url, supabase_key)
                print("✅ Supabase client initialized")
        except Exception as e:
            print(f"⚠️  Error initializing Supabase: {e}")
            self.supabase_client = None

    def get_connection(self):
        """Get a connection from the pool"""
        if self.conn_pool is None:
            raise Exception("Connection pool not initialized. Check database credentials.")
        return self.conn_pool.getconn()

    def return_connection(self, conn):
        """Return a connection to the pool"""
        if self.conn_pool and conn:
            self.conn_pool.putconn(conn)

    def close_all(self):
        """Close all connections in the pool"""
        if self.conn_pool:
            self.conn_pool.closeall()
            print("✅ All database connections closed")

db = Database()

