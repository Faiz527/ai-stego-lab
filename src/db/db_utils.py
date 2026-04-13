"""
Database Utilities Module
==========================
Handles all PostgreSQL database operations including user management,
operation logging, and activity tracking.
"""

import psycopg2
from psycopg2 import sql
import os
import logging
import secrets
import hmac
from datetime import datetime, timedelta
from collections import defaultdict
from threading import Lock
from dotenv import load_dotenv
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(dotenv_path=str(PROJECT_ROOT / '.env'))

# Database configuration
DB_PASSWORD = os.getenv('DB_PASSWORD')
if not DB_PASSWORD:
    raise ValueError("❌ DB_PASSWORD environment variable is REQUIRED but not set. "
                     "Set it in .env or Streamlit secrets.")

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'stegnography'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': DB_PASSWORD
}

# Rate limiting configuration
RATE_LIMIT_WINDOW = 300  # 5 minutes
MAX_LOGIN_ATTEMPTS = 5
_login_attempts = defaultdict(list)
_rate_limit_lock = Lock()


class DatabaseError(Exception):
    """Generic database error that doesn't expose internal details."""
    pass


class AuthenticationError(Exception):
    """Authentication-related error."""
    pass


class RateLimitError(Exception):
    """Rate limit exceeded error."""
    pass


def _hash_password(password: str) -> str:
    """
    Hash password using bcrypt.
    
    Args:
        password (str): Plain text password
    
    Returns:
        str: Bcrypt hashed password
    """
    try:
        import bcrypt
    except ImportError:
        raise ImportError("bcrypt is required. Install with: pip install bcrypt")
    
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def _verify_password(password: str, password_hash: str) -> bool:
    """
    Verify password using constant-time comparison via bcrypt.
    
    Args:
        password (str): Plain text password
        password_hash (str): Bcrypt hashed password
    
    Returns:
        bool: True if password matches
    """
    try:
        import bcrypt
    except ImportError:
        raise ImportError("bcrypt is required. Install with: pip install bcrypt")
    
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


def _check_rate_limit(identifier: str) -> bool:
    """
    Check if identifier has exceeded rate limit.
    
    Args:
        identifier (str): Username or IP to check
    
    Returns:
        bool: True if within rate limit, False if exceeded
    """
    with _rate_limit_lock:
        now = datetime.now()
        cutoff = now - timedelta(seconds=RATE_LIMIT_WINDOW)
        
        # Clean old attempts
        _login_attempts[identifier] = [
            t for t in _login_attempts[identifier] if t > cutoff
        ]
        
        return len(_login_attempts[identifier]) < MAX_LOGIN_ATTEMPTS


def _record_login_attempt(identifier: str):
    """Record a login attempt for rate limiting."""
    with _rate_limit_lock:
        _login_attempts[identifier].append(datetime.now())


def _clear_login_attempts(identifier: str):
    """Clear login attempts after successful login."""
    with _rate_limit_lock:
        _login_attempts[identifier] = []


def get_db_connection():
    """
    Get PostgreSQL database connection.
    
    On Streamlit Cloud: Uses Neon database from secrets.toml
    Locally: Uses .env credentials
    """
    import os
    from dotenv import load_dotenv
    
    # Try to use Streamlit secrets first (for Streamlit Cloud)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'postgres' in st.secrets:
            logger.info("📡 Using Streamlit Cloud database (Neon)")
            creds = st.secrets['postgres']
            conn = psycopg2.connect(
                host=creds.get('host'),
                port=int(creds.get('port', 5432)),
                database=creds.get('dbname'),
                user=creds.get('user'),
                password=creds.get('password'),
                sslmode=creds.get('sslmode', 'require')
            )
            return conn
    except Exception as e:
        logger.debug(f"Streamlit secrets not available: {e}")
    
    # Fall back to .env for local development
    try:
        load_dotenv()
        host = os.getenv('DB_HOST', 'localhost')
        port = int(os.getenv('DB_PORT', 5432))
        database = os.getenv('DB_NAME', 'stegnography')
        user = os.getenv('DB_USER', 'postgres')
        password = os.getenv('DB_PASSWORD')
        if not password:
            raise ValueError("❌ DB_PASSWORD environment variable is REQUIRED but not set. "
                     "Set it in .env or Streamlit secrets.")
        
        logger.info(f"🔌 Using local database: {host}:{port}/{database}")
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise


def initialize_database():
    """
    Initialize database - create tables if they don't exist.
    Drops and recreates operations table to ensure schema is up-to-date.
    
    On Streamlit Cloud:
    - Uses Neon database
    - Creates tables if needed
    
    Handles connection errors gracefully.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create operations table if it doesn't exist (preserve data)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operations (
                id SERIAL PRIMARY KEY,
                user_id INT NOT NULL REFERENCES users(id),
                operation_type VARCHAR(50) DEFAULT 'encode',
                method VARCHAR(50),
                input_image VARCHAR(500),
                output_image VARCHAR(500),
                message_length INT,
                encoding_time FLOAT DEFAULT 0.0,
                status VARCHAR(50) DEFAULT 'success',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create activity_log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id SERIAL PRIMARY KEY,
                user_id INT NOT NULL REFERENCES users(id),
                action VARCHAR(255),
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        conn.commit()
        logger.info("✅ Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        if conn:
            try:
                conn.rollback()
            except:
                pass
        return False
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


def add_user(username: str, password: str) -> bool:
    """
    Add a new user to the database with secure password hashing.
    
    Args:
        username (str): Username (will be converted to lowercase)
        password (str): Plain text password (will be hashed with bcrypt)
    
    Returns:
        bool: Success status
    
    Raises:
        DatabaseError: If database operation fails
    """
    conn = None
    cursor = None
    try:
        # Normalize username to lowercase
        username = username.lower().strip()
        
        # Validate username
        if not username or len(username) < 3 or len(username) > 255:
            logger.warning("Invalid username length")
            return False
        
        # Validate password strength
        if not password or len(password) < 8:
            logger.warning("Password too short")
            return False
        
        # Hash password with bcrypt
        password_hash = _hash_password(password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )
        
        conn.commit()
        logger.info(f"User added successfully")
        return True
        
    except psycopg2.IntegrityError:
        # Username already exists
        logger.warning("Username already exists")
        if conn:
            try:
                conn.rollback()
            except:
                pass
        return False
    except DatabaseError:
        if conn:
            try:
                conn.rollback()
            except:
                pass
        raise
    except Exception as e:
        logger.error(f"Failed to add user: {str(e)}")
        if conn:
            try:
                conn.rollback()
            except:
                pass
        raise DatabaseError("Failed to create user")
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


def verify_user(username: str, password: str) -> dict:
    """
    Verify user credentials with rate limiting and constant-time comparison.
    
    Args:
        username (str): Username
        password (str): Plain text password
    
    Returns:
        dict: Dictionary with user_id if credentials match, None otherwise
              Example: {'user_id': 1, 'username': 'testuser'}
    
    Raises:
        RateLimitError: If too many failed attempts
        DatabaseError: If database operation fails
    """
    # Normalize username
    username = username.lower().strip()
    
    # Check rate limit
    if not _check_rate_limit(username):
        logger.warning(f"Rate limit exceeded for user: {username}")
        raise RateLimitError("Too many login attempts. Please try again later.")
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user's password hash
        cursor.execute(
            "SELECT id, username, password_hash FROM users WHERE username = %s",
            (username,)
        )
        
        result = cursor.fetchone()
        
        if result:
            user_id, db_username, password_hash = result
            
            # Use bcrypt's constant-time comparison
            if _verify_password(password, password_hash):
                _clear_login_attempts(username)
                logger.info(f"User verified successfully")
                return {'user_id': user_id, 'username': db_username}
        
        # Record failed attempt (same response whether user exists or not)
        _record_login_attempt(username)
        logger.warning("Invalid credentials")
        return None
        
    except RateLimitError:
        raise
    except DatabaseError:
        raise
    except Exception as e:
        logger.error(f"User verification failed: {str(e)}")
        # Don't expose internal errors - return generic failure
        _record_login_attempt(username)
        return None
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


def log_operation(user_id: int, operation_type: str, method: str, input_image: str, 
                  output_image: str, message_length: int, encoding_time: float = 0.0, 
                  status: str = 'success'):
    """
    Log a steganography operation.
    
    Args:
        user_id (int): User ID
        operation_type (str): Type of operation ('encode' or 'decode')
        method (str): Steganography method used (LSB, DCT, DWT)
        input_image (str): Input image path
        output_image (str): Output image path
        message_length (int): Size of embedded message in bytes
        encoding_time (float): Time taken for operation in seconds
        status (str): Operation status ('success', 'failed')
    
    Raises:
        DatabaseError: If logging fails
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO operations 
            (user_id, operation_type, method, input_image, output_image, message_length, encoding_time, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, operation_type, method, input_image, output_image, message_length, encoding_time, status))
        
        conn.commit()
        logger.info(f"Operation logged for user {user_id}: {operation_type} via {method}")
        
    except DatabaseError:
        if conn:
            try:
                conn.rollback()
            except:
                pass
        raise
    except psycopg2.Error as e:
        logger.error(f"Failed to log operation: {str(e)}")
        if conn:
            try:
                conn.rollback()
            except:
                pass
        raise DatabaseError("Failed to log operation")
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


def log_activity(user_id: int, action: str, details: str = None):
    """
    Log user activity.
    
    Args:
        user_id (int): User ID
        action (str): Action description
        details (str): Additional details
    
    Raises:
        DatabaseError: If logging fails
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO activity_log (user_id, action, details) VALUES (%s, %s, %s)",
            (user_id, action, details)
        )
        
        conn.commit()
        logger.info(f"Activity logged for user {user_id}")
        
    except DatabaseError:
        if conn:
            try:
                conn.rollback()
            except:
                pass
        raise
    except psycopg2.Error as e:
        logger.error(f"Failed to log activity: {str(e)}")
        if conn:
            try:
                conn.rollback()
            except:
                pass
        raise DatabaseError("Failed to log activity")
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


def get_user_operations(user_id: int, limit: int = 10) -> list:
    """
    Get user's recent operations.
    
    Args:
        user_id (int): User ID
        limit (int): Number of records to retrieve
    
    Returns:
        list: List of operations
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, method, input_image, output_image, message_length, encoding_time, status, created_at
            FROM operations
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (user_id, limit))
        
        operations = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return operations
        
    except Exception as e:
        logger.error(f"Failed to retrieve operations: {str(e)}")
        return []


def get_statistics() -> dict:
    """
    Get application statistics.
    
    Returns:
        dict: Statistics data
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total users
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        # Total operations
        cursor.execute("SELECT COUNT(*) FROM operations")
        total_operations = cursor.fetchone()[0]
        
        # Operations by method
        cursor.execute("SELECT method, COUNT(*) FROM operations GROUP BY method")
        method_counts = cursor.fetchall()
        
        # Average encoding time
        cursor.execute("SELECT AVG(encoding_time) FROM operations")
        avg_time = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return {
            'total_users': total_users,
            'total_operations': total_operations,
            'by_method': dict(method_counts),
            'avg_encoding_time': float(avg_time) if avg_time else 0
        }
        
    except Exception as e:
        logger.error(f"Failed to get statistics: {str(e)}")
        return {}


def get_operation_stats(days: int = 7) -> dict:
    """
    Get operation statistics for the last N days.
    
    Args:
        days (int): Number of days to retrieve stats for
    
    Returns:
        dict: Statistics data
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                DATE(created_at) as date,
                method,
                COUNT(*) as count,
                AVG(encoding_time) as avg_time
            FROM operations
            WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            GROUP BY DATE(created_at), method
            ORDER BY DATE(created_at) DESC
        """, (days,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            'stats': [
                {
                    'date': str(row[0]),
                    'method': row[1],
                    'count': row[2],
                    'avg_time': float(row[3]) if row[3] else 0
                }
                for row in results
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get operation stats: {str(e)}")
        return {'stats': []}


def get_method_distribution() -> dict:
    """
    Get distribution of operations by method.
    
    Returns:
        dict: Method distribution data
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT method, COUNT(*) as count
            FROM operations
            GROUP BY method
        """)
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {method: count for method, count in results}
        
    except Exception as e:
        logger.error(f"Failed to get method distribution: {str(e)}")
        return {}


def get_encode_decode_stats() -> dict:
    """
    Get encoding vs decoding statistics.
    
    Returns:
        dict: Encode/decode statistics
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Fixed: use output_image to distinguish encode vs decode
        # Encode operations have a non-empty output_image
        # Decode operations have empty or NULL output_image
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN output_image IS NOT NULL AND output_image != '' THEN 'Encode' 
                    ELSE 'Decode' 
                END as op_type,
                COUNT(*) as count
            FROM operations
            GROUP BY op_type
        """)
        
        results = dict(cursor.fetchall())
        cursor.close()
        conn.close()
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to get encode/decode stats: {str(e)}")
        return {}


def get_activity_log(user_id: int = None, limit: int = 50) -> list:
    """
    Get activity log entries.
    
    Args:
        user_id (int): Optional user ID filter
        limit (int): Number of records to retrieve
    
    Returns:
        list: Activity log entries
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute("""
                SELECT id, user_id, action, details, created_at
                FROM activity_log
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (user_id, limit))
        else:
            cursor.execute("""
                SELECT id, user_id, action, details, created_at
                FROM activity_log
                ORDER BY created_at DESC
                LIMIT %s
            """, (limit,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to get activity log: {str(e)}")
        return []


def get_timeline_data(days: int = 7) -> list:
    """
    Get timeline data for operations over N days.
    
    Args:
        days (int): Number of days to retrieve
    
    Returns:
        list: Timeline data
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as count
            FROM operations
            WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            GROUP BY DATE(created_at)
            ORDER BY DATE(created_at)
        """, (days,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [{'date': str(row[0]), 'count': row[1]} for row in results]
        
    except Exception as e:
        logger.error(f"Failed to get timeline data: {str(e)}")
        return []


def get_size_distribution() -> dict:
    """
    Get distribution of message sizes.
    
    Returns:
        dict: Size distribution data
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN message_length < 1000 THEN 'Small (< 1KB)'
                    WHEN message_length < 10000 THEN 'Medium (1-10KB)'
                    WHEN message_length < 100000 THEN 'Large (10-100KB)'
                    ELSE 'Very Large (> 100KB)'
                END as size_category,
                COUNT(*) as count
            FROM operations
            GROUP BY size_category
        """)
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {row[0]: row[1] for row in results}
        
    except Exception as e:
        logger.error(f"Failed to get size distribution: {str(e)}")
        return {}


def search_activity_log(search_term: str, limit: int = 50) -> list:
    """
    Search activity log by action or details.
    
    Args:
        search_term (str): Term to search for
        limit (int): Number of results to return
    
    Returns:
        list: Matching activity log entries
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, user_id, action, details, created_at
            FROM activity_log
            WHERE action ILIKE %s OR details ILIKE %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (f'%{search_term}%', f'%{search_term}%', limit))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to search activity log: {str(e)}")
        return []


def get_user_count() -> int:
    """Get total number of users."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count
    except Exception as e:
        logger.error(f"Failed to get user count: {str(e)}")
        return 0


def get_operation_count() -> int:
    """Get total number of operations."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM operations")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count
    except Exception as e:
        logger.error(f"Failed to get operation count: {str(e)}")
        return 0


def get_recent_activity(limit: int = 100) -> list:
    """
    Get recent activity entries.
    
    Args:
        limit (int): Number of recent entries to retrieve
    
    Returns:
        list: Recent activity entries
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, user_id, action, details, created_at
            FROM activity_log
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to get recent activity: {str(e)}")
        return []


def get_user_stats(username: str) -> list:
    """
    Get statistics for a specific user.
    
    Args:
        username (str): Username to get stats for
    
    Returns:
        list: List of (method, count) tuples
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First get user ID
        cursor.execute("SELECT id FROM users WHERE username = %s", (username.lower(),))
        user_result = cursor.fetchone()
        
        if not user_result:
            cursor.close()
            conn.close()
            return []
        
        user_id = user_result[0]
        
        # Get method distribution for this user
        cursor.execute("""
            SELECT method, COUNT(*) as count
            FROM operations
            WHERE user_id = %s
            GROUP BY method
        """, (user_id,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return results if results else []
        
    except Exception as e:
        logger.error(f"Failed to get user stats: {str(e)}")
        return []


def get_user_id(username: str) -> int:
    """
    Get user ID from username.
    
    Args:
        username (str): Username
    
    Returns:
        int: User ID or None if not found
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = %s", (username.lower(),))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return result[0] if result else None
        
    except Exception as e:
        logger.error(f"Failed to get user ID: {str(e)}")
        return None