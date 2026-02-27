from dotenv import load_dotenv
load_dotenv(override=True)
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import os
import uvicorn
import models
from database import engine, SessionLocal, get_db
from models import File as FileModel
from pydantic import BaseModel
from datetime import datetime

# 自动创建表（通常在生产环境中应当使用 alembic 迁移）
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="File Commander AI", description="智能文件管理后端 API")

# Pydantic 模型
class FileSchema(BaseModel):
    id: int
    path: str
    filename: str
    extension: Optional[str]
    size: int
    hash: Optional[str]
    drive: str
    created_at: Optional[datetime]
    project_id: Optional[int]

    class Config:
        from_attributes = True

class DuplicateGroup(BaseModel):
    hash: str
    count: int
    files: List[FileSchema]

@app.get("/")
def read_root():
    return {"message": "File Commander AI Backend is running"}

@app.get("/files", response_model=List[FileSchema])
def list_files(
    skip: int = 0, 
    limit: int = 100, 
    drive: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取文件列表，支持分页和简单的搜索/过滤
    """
    query = db.query(models.File)
    if drive:
        query = query.filter(models.File.drive == drive)
    if q:
        query = query.filter(models.File.filename.contains(q))
    
    files = query.offset(skip).limit(limit).all()
    return files

@app.get("/duplicates")
def find_duplicates(db: Session = Depends(get_db)):
    """
    查找重复文件：基于哈希值分组
    返回：具有相同哈希值但路径不同的文件组
    """
    # 查找有重复哈希的记录
    # SQL logic: SELECT hash, count(*) FROM files GROUP BY hash HAVING count(*) > 1
    subquery = (
        db.query(models.File.hash, func.count(models.File.id).label('count'))
        .filter(models.File.hash != None)
        .group_by(models.File.hash)
        .having(func.count(models.File.id) > 1)
        .subquery()
    )
    
    # 获取这些哈希对应的所有文件详情
    # Join subquery with files table
    duplicates = (
        db.query(models.File)
        .join(subquery, models.File.hash == subquery.c.hash)
        .order_by(models.File.hash)
        .all()
    )
    
    # 组织数据结构
    result = {}
    for f in duplicates:
        if f.hash not in result:
            result[f.hash] = []
        result[f.hash].append(f)
        
    # 格式化输出
    output = []
    for h, files in result.items():
        output.append({
            "hash": h,
            "count": len(files),
            "files": files
        })
        
    return output

@app.post("/open")
def open_file_locally(path: str):
    """
    在服务器（本地电脑）上打开文件
    """
    import os
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="文件不存在")
    try:
        os.startfile(path)
        return {"message": f"已打开文件: {path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/classify")
def classify_path(path: str):
    """
    使用 AI 分析路径并建议项目分类
    """
    # 延迟导入以避免循环依赖或加载问题
    from ai_classifier import AIClassifier
    classifier = AIClassifier()
    
    # 获取同目录下的文件作为上下文
    import os
    directory = os.path.dirname(path)
    try:
        files = [os.path.join(directory, f) for f in os.listdir(directory)[:20] if os.path.isfile(os.path.join(directory, f))]
        suggestion = classifier.suggest_structure(files)
        return {"suggestion": suggestion}
    except Exception as e:
        return {"error": str(e)}

@app.post("/organize")
def organize_files():
    pass

