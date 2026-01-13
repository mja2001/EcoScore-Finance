import os
from dotenv import load_dotenv
import psycopg2
from pymongo import MongoClient
import redis

load_dotenv()

class DatabaseConfig:
    """Database configuration and connection management"""
    
    @staticmethod
    def get_postgres_connection():
        """Get PostgreSQL connection"""
        try:
            conn = psycopg2.connect(
                host=os.getenv('POSTGRES_HOST', 'localhost'),
                port=os.getenv('POSTGRES_PORT', '5432'),
                database=os.getenv('POSTGRES_DB', 'ecoscore_finance'),
                user=os.getenv('POSTGRES_USER', 'postgres'),
                password=os.getenv('POSTGRES_PASSWORD', '')
            )
            return conn
        except Exception as e:
            print(f"PostgreSQL connection error: {e}")
            return None
    
    @staticmethod
    def get_mongodb_client():
        """Get MongoDB client"""
        try:
            client = MongoClient(
                os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
            )
            return client['ecoscore_iot']
        except Exception as e:
            print(f"MongoDB connection error: {e}")
            return None
    
    @staticmethod
    def get_redis_client():
        """Get Redis client for caching"""
        try:
            client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=0,
                decode_responses=True
            )
            return client
        except Exception as e:
            print(f"Redis connection error: {e}")
            return None

    @staticmethod
    def init_postgres_tables():
        """Initialize PostgreSQL tables"""
        conn = DatabaseConfig.get_postgres_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Create loans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loans (
                id SERIAL PRIMARY KEY,
                loan_id VARCHAR(50) UNIQUE NOT NULL,
                borrower_name VARCHAR(255) NOT NULL,
                loan_amount DECIMAL(15, 2) NOT NULL,
                project_type VARCHAR(100),
                description TEXT,
                eco_score DECIMAL(5, 2),
                predicted_carbon_reduction DECIMAL(10, 2),
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create incentives table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incentives (
                id SERIAL PRIMARY KEY,
                loan_id VARCHAR(50) REFERENCES loans(loan_id),
                incentive_type VARCHAR(50),
                amount DECIMAL(15, 2),
                blockchain_tx_id VARCHAR(255),
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create milestones table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS milestones (
                id SERIAL PRIMARY KEY,
                loan_id VARCHAR(50) REFERENCES loans(loan_id),
                milestone_name VARCHAR(255),
                target_value DECIMAL(10, 2),
                current_value DECIMAL(10, 2),
                achieved BOOLEAN DEFAULT FALSE,
                achieved_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ PostgreSQL tables initialized successfully")
        return True
