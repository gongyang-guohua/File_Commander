import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# ==========================================
# 提取自原 src/files_scan.py 的本地文件扫描逻辑
# 改造为适合 Agent 识别的原生 Python 工具方法
# ==========================================

IGNORE_DIRS = {'.git', 'node_modules', '$RECYCLE.BIN', 'System Volume Information', '__pycache__'}

def _get_file_hash(filepath: Path) -> Optional[str]:
    """计算指定文件的 SHA256 哈希值供内部调度"""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        return None

def scan_directory_tool(path: str, calculate_hash: bool = False) -> str:
    """
    扫描本地计算机上的指定目录或硬盘驱动器，收集文件元数据并视需计算文件的 SHA256 哈希值。
    该工具支持热加载缓存（断点续传）和大数据流容错。
    
    Args:
        path (str): 需要扫描的本地绝对路径或驱动器字母 (例如 "J:\\", "F:\\Data")。
        calculate_hash (bool): 是否需要对每一个文件执行 SHA256 哈希计算。计算哈希可以识别重复文件，但非常耗时。默认为 False。
        
    Returns:
        str: 扫描进度和结果概要描述，用于通知大模型。真实的细分数据被保存在 scan_results.json 内。
    """
    root_path = Path(path)
    if not root_path.exists():
        return f"Error: 扫盘失败，由于配置的目标路径 `{path}` 在本地不存在。"

    file_list: List[Dict[str, Any]] = []
    cache: Dict[str, Dict[str, Any]] = {}
    output_file = root_path / "scan_results.json"
    
    # 【1】 断点续传：尝试加载现有的结果缓存
    if output_file.exists():
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                old_results = json.load(f)
                for item in old_results:
                    if "path" in item:
                        cache[item["path"]] = item
        except Exception as e:
            pass # 缓存损坏则静默忽略，重新计算全量

    # 【2】 核心遍历逻辑（含对缓存的判断和 Interrupt 保护）
    try:
        for root, dirs, files in os.walk(root_path):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for name in files:
                file_path = Path(root) / name
                str_path = str(file_path)
                
                try:
                    stat = file_path.stat()
                    modified_iso = datetime.fromtimestamp(stat.st_mtime).isoformat()
                    
                    # 热加载：跳过时间戳和体积皆匹配的数据的重复哈希计算
                    if str_path in cache:
                        cached_item = cache[str_path]
                        if cached_item.get("modified") == modified_iso and cached_item.get("size") == stat.st_size:
                            file_list.append(cached_item)
                            continue 
                            
                    file_info = {
                        "path": str_path,
                        "name": name,
                        "size": stat.st_size,
                        "type": file_path.suffix.lower(),
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified": modified_iso
                    }
                    
                    if calculate_hash:
                        file_info["hash"] = _get_file_hash(file_path)
                    
                    file_list.append(file_info)
                    
                except Exception:
                    continue  # 单一文件读取异常时不中断全局扫描
                    
    except KeyboardInterrupt:
        # Agent 后台终止时也能捕获至此处
        pass 
    
    # 【3】 归档落盘与反馈
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(file_list, f, indent=2, ensure_ascii=False)
        return f"Scanning successfully finished/interrupted for `{path}`. Total handled valid target items: {len(file_list)}. Data saved at {output_file}."
    except Exception as e:
        fallback = Path("F:/File_Commander/scan_results.json")
        try:
            with open(fallback, 'w', encoding='utf-8') as f:
                json.dump(file_list, f, indent=2, ensure_ascii=False)
            return f"Scanning finished. Due to permission issue on `{path}`, results were saved to fallback at `{fallback}`. Handled items: {len(file_list)}."
        except Exception as err:
            return f"Error: All save attempts failed: Target({e}), Fallback({err}). Generated {len(file_list)} items in memory only."
