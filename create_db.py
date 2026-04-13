"""Create PostgreSQL database"""
import psycopg2
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
PROJECT_ROOT = Path(__file__).parent
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=str(ENV_FILE), override=True)

# Get credentials from .env
db_password = os.getenv('DB_PASSWORD', 'Password')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = int(os.getenv('DB_PORT', 5432))
db_user = os.getenv('DB_USER', 'postgres')

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
    
    print("\n🔄 Dropping existing database...")
    try:
        cursor.execute("DROP DATABASE stegnography;")
        print("✅ Old database dropped")
    except Exception as e:
        print(f"ℹ️  No existing database to drop: {str(e)[:50]}")
    
    print("🔄 Creating new database...")
    cursor.execute("CREATE DATABASE stegnography;")
    print("✅ Database 'stegnography' created successfully!")
    
    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Error: {e}")
    print(f"\n⚠️  Troubleshooting:")
    print(f"   1. Check .env file has correct DB_PASSWORD")
    print(f"   2. Verify PostgreSQL is running")
    print(f"   3. Test with: psql -U postgres -h localhost")