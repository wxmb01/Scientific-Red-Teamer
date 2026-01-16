# -*- coding: utf-8 -*-
"""
【海马体】Database Manager
功能：管理长期记忆，记录已读论文和待读队列。
这是实现 "Marathon Agent" (长时运行) 的基础。
"""
import sqlite3
import os
import json
from datetime import datetime

# 数据库文件将保存在 data 文件夹下
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
DB_PATH = os.path.join(DATA_DIR, "scholar_memory.db")

def init_db():
    """初始化数据库结构"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 1. 论文表 (Papers)
    # status: 'pending' (待读), 'processing' (正在读), 'done' (已读), 'error' (失败)
    c.execute('''
        CREATE TABLE IF NOT EXISTS papers (
            id TEXT PRIMARY KEY,
            title TEXT,
            url TEXT,
            local_path TEXT,
            parent_id TEXT,  -- 是哪篇论文引用了它 (溯源)
            status TEXT DEFAULT 'pending',
            score REAL,
            summary TEXT,
            added_time DATETIME,
            processed_time DATETIME
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"💾 [记忆体] 数据库已就绪: {DB_PATH}")

def add_paper_to_queue(paper_info, parent_id=None):
    """
    将发现的新论文加入待办列表
    :param paper_info: 包含 id, title, url 的字典
    :param parent_id: 推荐这篇论文的“父论文”ID
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # 检查是否已经存在 (避免重复研究)
        c.execute("SELECT id FROM papers WHERE id = ?", (paper_info['id'],))
        if c.fetchone():
            # print(f"   ⏩ 已在记忆中: {paper_info['title'][:20]}...")
            return False
            
        now = datetime.now().isoformat()
        c.execute('''
            INSERT INTO papers (id, title, url, parent_id, status, added_time)
            VALUES (?, ?, ?, ?, 'pending', ?)
        ''', (paper_info['id'], paper_info['title'], paper_info.get('url'), parent_id, now))
        
        conn.commit()
        print(f"📥 [新发现] 加入队列: {paper_info['title'][:30]}...")
        return True
    except Exception as e:
        print(f"❌ 数据库写入错误: {e}")
        return False
    finally:
        conn.close()

def get_next_task():
    """获取下一个要处理的任务 (FIFO)"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # 让结果像字典一样访问
    c = conn.cursor()
    
    # 找一个状态为 pending 的
    c.execute("SELECT * FROM papers WHERE status = 'pending' ORDER BY added_time ASC LIMIT 1")
    row = c.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def update_paper_status(paper_id, status, result_data=None, local_path=None):
    """更新论文状态 (例如：读完了，填入分数和摘要)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    now = datetime.now().isoformat()
    
    if status == 'done' and result_data:
        c.execute('''
            UPDATE papers 
            SET status = ?, 
                score = ?, 
                summary = ?, 
                local_path = ?,
                processed_time = ?
            WHERE id = ?
        ''', (status, result_data.get('score', 0), result_data.get('summary', ''), local_path, now, paper_id))
    else:
        c.execute("UPDATE papers SET status = ?, processed_time = ? WHERE id = ?", (status, now, paper_id))
        
    conn.commit()
    conn.close()

def get_statistics():
    """获取当前的工作进度"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT status, COUNT(*) FROM papers GROUP BY status")
    stats = dict(c.fetchall())
    conn.close()
    return stats

# === 自测模块 ===
if __name__ == "__main__":
    init_db()
    # 模拟加入一个任务
    fake_paper = {"id": "2401.00001", "title": "Test Paper regarding AI", "url": "http://arxiv..."}
    add_paper_to_queue(fake_paper)
    
    task = get_next_task()
    print(f"🎯 下一个任务: {task['title']}")
    
    update_paper_status(task['id'], "done", {"score": 9.9, "summary": "这是一个测试"}, "path/to/pdf")
    print("📊 统计:", get_statistics())