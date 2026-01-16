# -*- coding: utf-8 -*-
"""
【真理之眼】PDF Reader
功能：读取 PDF 文件，提取纯文本。
"""
import PyPDF2
import os

def read_pdf(file_path):
    """
    读取 PDF 并返回文本内容
    :param file_path: PDF 文件的完整路径
    :return: 提取出的纯文本 (String)
    """
    if not os.path.exists(file_path):
        print(f"❌ 错误：找不到文件 {file_path}")
        return ""

    print(f"📖 正在阅读: {os.path.basename(file_path)} ...")
    text_content = ""
    
    try:
        with open(file_path, 'rb') as f:
            # 创建阅读器对象
            reader = PyPDF2.PdfReader(f)
            
            # 获取总页数
            num_pages = len(reader.pages)
            # print(f"   📄 共 {num_pages} 页")
            
            # 逐页提取文字
            for i in range(num_pages):
                page = reader.pages[i]
                text = page.extract_text()
                if text:
                    text_content += text + "\n"
                    
        return text_content

    except Exception as e:
        print(f"❌ 读取失败: {e}")
        return ""

# === 自测模块 ===
if __name__ == "__main__":
    # 自动去 workspace 找一本书来试读
    # 1. 找到 workspace 路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    workspace = os.path.join(project_root, "workspace")
    
    # 2. 扫描里面的 PDF
    if os.path.exists(workspace):
        files = [f for f in os.listdir(workspace) if f.endswith(".pdf")]
        if files:
            # 挑第一本
            target_file = os.path.join(workspace, files[0])
            content = read_pdf(target_file)
            
            print("\n" + "="*30)
            print(f"👀 [预览前 500 字] \n{content[:500]}")
            print("="*30)
        else:
            print("⚠️ workspace 里没有 PDF，请先运行 arxiv_client.py")
    else:
        print("⚠️ 找不到 workspace 文件夹")