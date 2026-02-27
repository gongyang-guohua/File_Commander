import os
import shutil
from sqlalchemy.orm import Session
from database import SessionLocal
from models import File, Project
import time

BACKUP_ROOT = "G:\\Backup"

def get_classified_files(db: Session, limit=100, offset=0):
    return db.query(File).filter(File.project_id != None).offset(offset).limit(limit).all()

def backup_file(file_record: File, project_name: str):
    try:
        # 构建目标路径
        # G:\Backup\<ProjectName>\<Drive>\<PathWithoutDrive>
        drive_letter = file_record.drive.replace(":", "")
        rel_path = os.path.splitdrive(file_record.path)[1].lstrip("\\/")
        dest_path = os.path.join(BACKUP_ROOT, project_name, drive_letter, rel_path)
        
        # 创建目录
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        # 复制文件 (如果源文件存在且目标不存在或源更新)
        if not os.path.exists(dest_path) or os.path.getmtime(file_record.path) > os.path.getmtime(dest_path):
            print(f"Backing up: {file_record.path} -> {dest_path}")
            shutil.copy2(file_record.path, dest_path)
        else:
            # print(f"Skipped (uptodate): {file_record.path}")
            pass
            
    except Exception as e:
        print(f"Error backing up {file_record.path}: {e}")

def main():
    db = SessionLocal()
    offset = 0
    batch_size = 100
    
    try:
        while True:
            files = get_classified_files(db, limit=batch_size, offset=offset)
            if not files:
                break
            
            for file_record in files:
                if file_record.project:
                    backup_file(file_record, file_record.project.name)
            
            offset += batch_size
            print(f"Processed {offset} files for backup...")
            
    finally:
        db.close()

if __name__ == "__main__":
    main()
