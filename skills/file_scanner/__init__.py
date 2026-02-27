"""
Google ADK 规范：file_scanner (本地文件扫描核心技能包)
提供文件基础遍历、哈希去重检索及进度缓存续传功能。
"""

from .tools import scan_directory_tool

__all__ = ["scan_directory_tool"]
