"""
Database Utilities Module (Minimal Version)
============================================
Handles database operations without complex emoji output.
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# Load environment variables
from dotenv import load_dotenv
load_dotenv(dotenv_path=str(ENV_FILE), override=True, verbose=False)

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "steganography_db")
DB_USER = os.getenv("DB_USER", "stego_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")


def connect_db():
    """Connect to PostgreSQL database."""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        logger.info("Database connection successful")
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None


def init_database():
    """Initialize database with required tables."""
    conn = connect_db()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create operations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS operations (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                operation_type VARCHAR(50),
                method VARCHAR(50),
                status VARCHAR(255),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create activity log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                action VARCHAR(255),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        return False


def add_user(username, password):
    """Add new user to database."""
    try:
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        conn = connect_db()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error adding user: {e}")
        return False


def verify_user(username, password):
    """Verify user credentials."""
    try:
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        conn = connect_db()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE username=%s AND password_hash=%s",
            (username, password_hash)
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None
    except Exception as e:
        logger.error(f"Error verifying user: {e}")
        return False
