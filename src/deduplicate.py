import os
import sys
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

# Add project root to path
sys.path.append(str(Path(__file__).parent / "src"))

from database import SessionLocal, engine
import models
from scanner import scan_drive

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def find_and_delete_duplicates(target_path: str, dry_run: bool = True):
    """
    Finds duplicate files in the target path and deletes them, keeping one copy.
    """
    db = SessionLocal()
    try:
        # 1. Scan the directory first to ensure the DB is up to date
        logging.info(f"Scanning {target_path}...")
        scan_drive(target_path)
        
        # 2. Query for duplicate hashes
        logging.info("Searching for duplicates in database...")
        subquery = (
            db.query(models.File.hash, func.count(models.File.id).label('count'))
            .filter(models.File.hash != None)
            .group_by(models.File.hash)
            .having(func.count(models.File.id) > 1)
            .subquery()
        )
        
        duplicate_files = (
            db.query(models.File)
            .join(subquery, models.File.hash == subquery.c.hash)
            .order_by(models.File.hash, models.File.created_at)
            .all()
        )
        
        if not duplicate_files:
            logging.info("No duplicates found.")
            return

        # 3. Process duplicates
        processed_hashes = {}  # hash -> kept_path
        deleted_count = 0
        saved_space = 0
        
        for file_entry in duplicate_files:
            if file_entry.hash not in processed_hashes:
                # Keep the first one encountered (oldest or first in query)
                logging.info(f"KEEPING: {file_entry.path} (Hash: {file_entry.hash})")
                processed_hashes[file_entry.hash] = file_entry.path
            else:
                # This is a duplicate!
                kept_path = processed_hashes[file_entry.hash]
                if dry_run:
                    logging.info(f"[DRY RUN] Would delete: {file_entry.path}")
                else:
                    try:
                        # Create log entry
                        log_entry = models.DeduplicationLog(
                            deleted_path=file_entry.path,
                            kept_path=kept_path,
                            file_hash=file_entry.hash,
                            file_size=file_entry.size
                        )
                        db.add(log_entry)

                        if os.path.exists(file_entry.path):
                            os.remove(file_entry.path)
                            logging.info(f"DELETED: {file_entry.path}")
                            # Also remove from DB
                            db.delete(file_entry)
                        else:
                            logging.warning(f"File already missing: {file_entry.path}")
                            db.delete(file_entry)
                    except Exception as e:
                        logging.error(f"Failed to delete {file_entry.path}: {e}")
                        continue
                
                deleted_count += 1
                saved_space += file_entry.size
        
        if not dry_run:
            db.commit()
            
        action = "Found (Dry Run)" if dry_run else "Successfully processed"
        logging.info(f"--- Results ---")
        logging.info(f"{action} {deleted_count} duplicates.")
        logging.info(f"Estimated space saved: {saved_space / (1024*1024):.2f} MB")
        if dry_run:
            logging.info("Run without --dry-run to actually delete files.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Find and delete duplicate files.")
    parser.add_argument("--path", default="/Volumes/Workspace/References", help="Path to scan for duplicates.")
    parser.add_argument("--apply", action="store_true", help="Apply deletions (omit for dry run).")
    args = parser.parse_args()
    
    find_and_delete_duplicates(args.path, dry_run=not args.apply)
