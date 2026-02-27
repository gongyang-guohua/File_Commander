import json
import os
from sqlalchemy.orm import Session
from database import SessionLocal
from models import File, Project
from ai_classifier import AIClassifier
import time

def get_unclassified_files(db: Session, limit=100):
    return db.query(File).filter(File.project_id == None).limit(limit).all()

def get_or_create_project(db: Session, project_name, description=None):
    project = db.query(Project).filter(Project.name == project_name).first()
    if not project:
        project = Project(name=project_name, description=description)
        db.add(project)
        db.commit()
        db.refresh(project)
    return project

def process_batch(db: Session, classifier: AIClassifier):
    # 获取未分类文件
    files = get_unclassified_files(db, limit=50) # 一次处理 50 个
    if not files:
        print("没有未分类的文件。")
        return False

    # 准备元数据
    files_metadata = [{"path": f.path, "name": f.filename} for f in files]
    
    # 调用 AI
    print(f"正在分析 {len(files)} 个文件...")
    json_response = classifier.batch_classify(files_metadata)
    
    # 解析 JSON
    try:
        # 清理可能的 markdown 标记
        json_str = json_response.strip()
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
            
        results = json.loads(json_str)
        
        for item in results:
            path = item.get("path")
            project_name = item.get("project")
            
            if not path or not project_name:
                continue
                
            # 查找对应的文件记录
            # 注意：路径匹配可能需要处理斜杠问题
            file_record = next((f for f in files if f.path == path), None)
            if not file_record:
                # 尝试标准化路径匹配
                file_record = next((f for f in files if os.path.normpath(f.path) == os.path.normpath(path)), None)
            
            if file_record:
                if project_name not in ["General", "Trash", "Unknown"]:
                    project = get_or_create_project(db, project_name, item.get("reason"))
                    file_record.project_id = project.id
                    print(f"[{project_name}] {file_record.filename}")
                else:
                    # 可以设置一个特殊的 'General' 项目或标记为已扫描但无项目
                    # 这里暂时略过，或者可以建一个 ID 为 0 的 General 项目
                    print(f"[Ignored] {file_record.filename} ({project_name})")
                    
        db.commit()
        return True
        
    except json.JSONDecodeError:
        print(f"JSON 解析失败: {json_response}")
        return True # 继续尝试下一批
    except Exception as e:
        print(f"处理批次时发生未知错误: {e}")
        return True

def main():
    db = SessionLocal()
    classifier = AIClassifier()
    
    consecutive_failures = 0
    
    try:
        while True:
            # 简单限流: 如果连续失败，增加等待时间
            try:
                has_more = process_batch(db, classifier)
                if not has_more:
                    break
                consecutive_failures = 0 
                time.sleep(2) # 基础等待2秒
            except Exception as e:
                consecutive_failures += 1
                wait_time = min(60, 2 ** consecutive_failures) # 指数退避，最大60秒
                print(f"发生错误，等待 {wait_time} 秒后重试... ({e})")
                time.sleep(wait_time)
                
    finally:
        db.close()

if __name__ == "__main__":
    main()
