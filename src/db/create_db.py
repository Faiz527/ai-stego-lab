"""Create PostgreSQL database"""
import psycopg2
from psycopg2 import sql
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
PROJECT_ROOT = Path(__file__).parent
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=str(ENV_FILE), override=True)

# Get credentials from .env
db_password = os.getenv('DB_PASSWORD')
if not db_password:
    raise ValueError("❌ DB_PASSWORD environment variable is REQUIRED but not set.")

db_host = os.getenv('DB_HOST', 'localhost')
db_port = int(os.getenv('DB_PORT', 5432))
db_user = os.getenv('DB_USER', 'postgres')
db_name = os.getenv('DB_NAME', 'stegnography')  # Database name to create/check

print(f"🔧 Using credentials from .env:")
print(f"   Host: {db_host}")
print(f"   User: {db_user}")
print(f"   Password: {'*' * len(db_password)}")

try:
    # Connect to default 'postgres' database
    print(f"\n🔌 Connecting to PostgreSQL...")
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        database='postgres'
    )
    
    conn.autocommit = True
    cursor = conn.cursor()
    print("✅ Connected!")
    
    # Validate database name to prevent SQL injection
    if not db_name or not db_name.replace('_', '').isalnum():
        raise ValueError("Invalid database name. Use only alphanumeric characters and underscores.")
    
    # Check if database already exists (works with all PostgreSQL versions)
    print("\n🔄 Checking if database exists...")
    cursor.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s",
        (db_name,)
    )
    
    if cursor.fetchone():
        print(f"✅ Database '{db_name}' already exists")
        print("ℹ️  Your user data has been preserved!")
    else:
        print(f"🔄 Creating new database '{db_name}'...")
        # Use identifier quoting for safety
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
        print(f"✅ Database '{db_name}' created successfully!")
    
    cursor.close()
    conn.close()
    print("\n✅ Database setup complete!")

except Exception as e:
    print(f"❌ Error: {e}")
    print(f"\n⚠️  Troubleshooting:")
    print(f"   1. Check .env file has correct DB_PASSWORD")
    print(f"   2. Verify PostgreSQL is running: psql -U postgres -h localhost")
    print(f"   3. If password is wrong, update DB_PASSWORD in .env")
    exit(1)