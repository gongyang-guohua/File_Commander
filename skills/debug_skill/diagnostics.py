import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import create_engine

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

try:
    from database import engine, SessionLocal
    from models import Base
    import psutil
except ImportError as e:
    print(f"Error: Missing core modules: {e}")
    sys.exit(1)

def check_env():
    print("--- Environment Check ---")
    load_dotenv(override=True)
    keys = ["DATABASE_URL", "MOONSHOT_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY"]
    for key in keys:
        val = os.getenv(key)
        status = "✅ Found" if val else "❌ Missing"
        print(f"{key}: {status}")

def check_db():
    print("\n--- Database Check ---")
    try:
        with engine.connect() as conn:
            print("✅ Database connection successful.")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

def check_paths():
    print("\n--- Path Check ---")
    paths = ["/Volumes/Workspace/Projects", "/Volumes/Workspace/Models", "/Volumes/Workspace/References"]
    for p in paths:
        exists = os.path.exists(p)
        status = "✅ Exists" if exists else "❌ Not found"
        print(f"{p}: {status}")

def check_logs():
    print("\n--- Deduplication Log Check ---")
    try:
        from models import DeduplicationLog
        db = SessionLocal()
        count = db.query(DeduplicationLog).count()
        print(f"Total deduplication logs: {count}")
        if count > 0:
            last = db.query(DeduplicationLog).order_by(DeduplicationLog.deleted_at.desc()).first()
            print(f"Latest deletion: {last.deleted_path}")
            print(f"Kept version: {last.kept_path}")
            print(f"Space saved: {last.file_size} bytes")
        db.close()
    except Exception as e:
        print(f"❌ Error checking logs: {e}")

if __name__ == "__main__":
    check_env()
    check_db()
    check_paths()
    check_logs()
