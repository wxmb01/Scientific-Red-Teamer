# -*- coding: utf-8 -*-
"""
【触手模块】arXiv Client (网络增强版)
功能：搜索论文，下载 PDF，提取元数据。
已集成：SSL 修复 + 强制代理。
"""
import arxiv
import os
import ssl

# ================= 🚑 网络急救包 =================
# 1. SSL 证书修复
ssl._create_default_https_context = ssl._create_unverified_context

# ================= 🚑 网络急救包 =================
# ... (上面的 SSL 代码不用动)

# 👇 修改这一行！把 7890 改成 7897
PROXY = "http://127.0.0.1:7897" 

os.environ["http_proxy"] = PROXY
os.environ["https_proxy"] = PROXY
# =================================================
# 设定下载目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DOWNLOAD_DIR = os.path.join(PROJECT_ROOT, "workspace")

def search_papers(query, max_results=3):
    """
    搜索并下载论文
    """
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    print(f"🔍 [代理已开启] 正在 arXiv 搜索: '{query}' ...")
    
    # 构造客户端 (调整超时时间)
    client = arxiv.Client(
        page_size=max_results,
        delay_seconds=3.0,
        num_retries=3
    )
    
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )

    results = []
    
    try:
        # 这里的 results() 是一个生成器，我们需要尝试遍历它
        for r in client.results(search):
            # 清洗文件名
            safe_title = "".join([c for c in r.title if c.isalnum() or c in " ._-"]).strip()
            filename = f"{r.entry_id.split('/')[-1]}_{safe_title[:50]}.pdf"
            file_path = os.path.join(DOWNLOAD_DIR, filename)
            
            paper_info = {
                "title": r.title,
                "summary": r.summary,
                "path": file_path
            }
            
            # 下载逻辑
            if not os.path.exists(file_path):
                print(f"⬇️ 下载中: {r.title[:30]}...")
                r.download_pdf(dirpath=DOWNLOAD_DIR, filename=filename)
            else:
                print(f"⏩ 已存在: {r.title[:30]}...")
                
            results.append(paper_info)
            
    except Exception as e:
        print(f"⚠️ 网络连接错误: {e}")
        # 如果是 Streamlit 调用，可以在这里抛出错误或者记录日志

    print(f"✅ 成功获取 {len(results)} 篇论文。")
    return results

if __name__ == "__main__":
    # 自测
    search_papers("Generative AI", max_results=1)