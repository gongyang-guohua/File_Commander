-- 1. 创建文件总表
CREATE TABLE IF NOT EXISTS file_index (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(500),                   -- 文件名
    file_path TEXT UNIQUE NOT NULL,           -- 绝对路径 (作为唯一ID)
    file_extension VARCHAR(50),               -- 后缀 (.pdf, .dwg)
    file_size_mb NUMERIC(10, 2),              -- 大小 (MB)
    file_hash CHAR(64),                       -- 指纹 (SHA256)
    drive_letter CHAR(1),                     -- 盘符 (J, D, G)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 您的业务字段
    project_tag VARCHAR(100),                 -- 项目归属 (如: Hostalen)
    is_deleted BOOLEAN DEFAULT FALSE          -- 标记删除
);

-- 2. 创建索引 (让查询飞快)
CREATE INDEX IF NOT EXISTS idx_hash ON file_index(file_hash);
CREATE INDEX IF NOT EXISTS idx_name ON file_index(file_name);

-- 3. 创建查重视图 (神奇视图)
-- 逻辑：只显示那些 哈希值出现次数 > 1 的文件
CREATE OR REPLACE VIEW view_duplicates AS
SELECT t1.id, t1.file_name, t1.file_path, t1.drive_letter, t1.file_size_mb, t1.file_hash
FROM file_index t1
JOIN (
    SELECT file_hash 
    FROM file_index 
    WHERE is_deleted = FALSE 
    GROUP BY file_hash 
    HAVING COUNT(*) > 1
) t2 ON t1.file_hash = t2.file_hash
WHERE t1.is_deleted = FALSE
ORDER BY t1.file_hash, 
         CASE WHEN t1.drive_letter = 'J' THEN 0 ELSE 1 END; -- 让J盘排在最前面，方便保留