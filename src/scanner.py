import os
import hashlib
import psutil
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal
from models import File
import concurrent.futures

def get_drives():
    """获取所有固定驱动器，排除 C 盘"""
    drives = []
    for partition in psutil.disk_partitions():
        if 'cdrom' in partition.opts or partition.fstype == '':
            continue
        drive = partition.mountpoint
        # 排除 C 盘 (Windows 下通常是 "C:\\")
        if drive.upper().startswith("C"):
            continue
        drives.append(drive)
    return drives

def calculate_sha256(filepath, chunk_size=8192):
    """计算文件的 SHA-256 哈希值"""
    sha256 = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(chunk_size):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def process_file(db: Session, filepath: str, drive: str):
    """处理单个文件：提取元数据并存入数据库"""
    try:
        # 获取文件基本信息
        stat = os.stat(filepath)
        size = stat.st_size
        
        # 检查是否已存在（根据路径）
        existing_file = db.query(File).filter(File.path == filepath).first()
        
        # 如果文件已存在且修改时间未变，可能跳过哈希计算（优化点）
        # 这里为了演示，先简单处理：如果存在但元数据不同则更新，否则跳过
        
        modified_at = datetime.fromtimestamp(stat.st_mtime)
        created_at = datetime.fromtimestamp(stat.st_ctime)
        
        file_hash = None
        # 计算哈希（大文件可以考虑优化，或者仅在发现大小时重复时计算）
        # 这里先全量计算，用于构建基础数据
        file_hash = calculate_sha256(filepath)
        
        if not file_hash: # 读取失败
            return

        filename = os.path.basename(filepath)
        extension = os.path.splitext(filename)[1].lower()

        if existing_file:
            if existing_file.modified_at != modified_at or existing_file.size != size:
                existing_file.size = size
                existing_file.hash = file_hash
                existing_file.modified_at = modified_at
                existing_file.scanned_at = datetime.now()
                print(f"Updated: {filepath}")
        else:
            new_file = File(
                path=filepath,
                filename=filename,
                extension=extension,
                size=size,
                hash=file_hash,
                drive=drive,
                created_at=created_at,
                modified_at=modified_at
            )
            db.add(new_file)
            print(f"Added: {filepath}")
            
        # 提交（为了性能可以批量提交）
        # db.commit() 
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        # db.rollback()

def scan_drive(drive):
    """扫描指定驱动器"""
    print(f"Scanning drive: {drive}")
    db = SessionLocal()
    batch_size = 100
    count = 0
    
    try:
        for root, dirs, files in os.walk(drive):
            for file in files:
                filepath = os.path.join(root, file)
                process_file(db, filepath, drive)
                count += 1
                if count % batch_size == 0:
                    db.commit()
                    print(f"Committed {count} files from {drive}")
        db.commit() # 提交剩余
    except Exception as e:
        print(f"Error during scan of {drive}: {e}")
    finally:
        db.close()

def main():
    drives = get_drives()
    print(f"Found drives to scan: {drives}")
    
    # 可以使用线程池并行扫描不同驱动器，但要注意数据库并发写入
    # SQLite 对并发写入支持有限，PostgreSQL 很好
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(drives) if drives else 1) as executor:
        executor.map(scan_drive, drives)

if __name__ == "__main__":
    main()
