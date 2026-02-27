import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from database import engine, Base, DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
import models  # 必须导入 models 才能注册 Base

def create_database():
    """检查并创建数据库"""
    try:
        conn = psycopg2.connect(
            user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT, dbname='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # 检查数据库是否存在
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
        exists = cur.fetchone()
        
        if not exists:
            print(f"数据库 {DB_NAME} 不存在，正在创建...")
            cur.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"数据库 {DB_NAME} 创建成功！")
        else:
            print(f"数据库 {DB_NAME} 已存在。")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"创建数据库时出错: {e}")

def init_tables():
    """初始化表结构"""
    try:
        # Base.metadata.create_all 需要 engine 绑定到目标数据库
        # database.py 中的 engine 已经配置为连接到 file_manager
        Base.metadata.create_all(bind=engine)
        print("表结构初始化成功。")
    except Exception as e:
        print(f"初始化表结构出错: {e}")

if __name__ == "__main__":
    create_database()
    init_tables()
