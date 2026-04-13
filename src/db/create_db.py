"""
create_db.py
============
Create PostgreSQL database for ITR Steganography application.

Usage:
    python -m src.db.create_db
    (from project root)
"""
import psycopg2
import os
from pathlib import Path
from dotenv import load_dotenv
import sys

# Adjust path - go up 2 levels from src/db/ to project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# Add project root to path
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables from .env
load_dotenv(dotenv_path=str(ENV_FILE), override=True)

# Get credentials from .env
db_password = os.getenv('DB_PASSWORD', 'Password')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = int(os.getenv('DB_PORT', 5432))
db_user = os.getenv('DB_USER', 'postgres')
db_name = os.getenv('DB_NAME', 'stegnography')

print(f"🔧 Using credentials from .env:")
print(f"   Host: {db_host}")
print(f"   Port: {db_port}")
print(f"   User: {db_user}")
print(f"   Database: {db_name}")
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
    
    print(f"\n🔄 Dropping existing database '{db_name}'...")
    try:
        cursor.execute(f"DROP DATABASE {db_name};")
        print(f"✅ Old database dropped")
    except Exception as e:
        print(f"ℹ️  No existing database to drop: {str(e)[:50]}")
    
    print(f"🔄 Creating new database '{db_name}'...")
    cursor.execute(f"CREATE DATABASE {db_name};")
    print(f"✅ Database '{db_name}' created successfully!")
    
    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Error: {e}")
    print(f"\n⚠️  Troubleshooting:")
    print(f"   1. Check .env file has correct DB_PASSWORD")
    print(f"   2. Verify PostgreSQL is running: Get-Service postgresql-x64-*")
    print(f"   3. Test connection: psql -U {db_user} -h {db_host}")
    print(f"   4. Verify .env has correct credentials:")
    print(f"      - DB_HOST={db_host}")
    print(f"      - DB_PORT={db_port}")
    print(f"      - DB_NAME={db_name}")
    print(f"      - DB_USER={db_user}")
    print(f"      - DB_PASSWORD=***")
    sys.exit(1)


if __name__ == "__main__":
    print("\n✨ Database setup complete!")