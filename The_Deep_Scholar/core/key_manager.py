# -*- coding: utf-8 -*-
"""
【军火库】Key Manager (Final Version)
功能：统一管理 API 连接、网络代理和模型配置。
"""
import os
import sys
from openai import OpenAI

# ================= 🔧 配置区 =================
# 1. 中转地址
API_BASE_URL = "https://twob.pp.ua/v1"

# 2. 你的 Key
API_KEY = "AIzaSy..."  # ⚠️ 请填入你的 Key

# 3. 指定模型 (Gemini 3 Pro Preview)
TARGET_MODEL = "[次]gemini-3-pro-preview"

# 4. 本地代理 (解决网络超时)
PROXY_URL = "http://127.0.0.1:7897" 
# ============================================

def init_proxy():
    """强制注入代理配置"""
    if PROXY_URL:
        os.environ["http_proxy"] = PROXY_URL
        os.environ["https_proxy"] = PROXY_URL

def get_client():
    """返回配置好的 OpenAI 客户端"""
    init_proxy()
    return OpenAI(
        api_key=API_KEY,
        base_url=API_BASE_URL,
        timeout=90.0, # 给 Gemini 3 足够的思考时间
        max_retries=3
    )

def get_model_name():
    return TARGET_MODEL

# === 自检模块 (直接运行此文件可测试连接) ===
if __name__ == "__main__":
    print("🏥 正在检查军火库状态...")
    try:
        client = get_client()
        print(f"🔗 连接地址: {API_BASE_URL}")
        print(f"🔫 目标模型: {TARGET_MODEL}")
        
        response = client.chat.completions.create(
            model=TARGET_MODEL,
            messages=[{"role": "user", "content": "Ping. Are you Gemini 3?"}]
        )
        print("✅ 连接成功！AI 回复: " + response.choices[0].message.content)
    except Exception as e:
        print(f"❌ 连接失败: {e}")