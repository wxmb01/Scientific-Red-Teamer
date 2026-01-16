# -*- coding: utf-8 -*-
"""
【状态管理器】State Manager (V4.0 核心)
功能：维护 Agent 的"意识流"。
实现 "Continuity" (连续性)：把当前的假设、策略、失败次数持久化到磁盘。
"""
import json
import os
import time

STATE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "agent_state.json")

class ResearchState:
    def __init__(self, goal):
        self.goal = goal
        self.current_hypothesis = "尚未形成具体假设"
        self.known_facts = [] # 已验证的事实
        self.failed_attempts = 0 # 连续失败计数 (用于触发 Self-correct)
        self.strategy = "broad_search" # 当前策略: broad_search, deep_dive, verify_fact
        self.last_thought = "初始化完成，准备开始。"
        self.step_count = 0

    def to_dict(self):
        return self.__dict__

def save_state(state):
    """保存现场 (Snapshot)"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state.to_dict(), f, ensure_ascii=False, indent=2)
    # print(f"💾 [State] 状态已保存 (Step {state.step_count})")

def load_state():
    """恢复现场"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 恢复对象
                state = ResearchState(data.get('goal', 'Unknown'))
                state.current_hypothesis = data.get('current_hypothesis')
                state.known_facts = data.get('known_facts', [])
                state.failed_attempts = data.get('failed_attempts', 0)
                state.strategy = data.get('strategy', 'broad_search')
                state.last_thought = data.get('last_thought')
                state.step_count = data.get('step_count', 0)
                print(f"🔄 [State] 成功恢复之前的研究进度！(Step {state.step_count})")
                return state
        except Exception as e:
            print(f"⚠️ 状态文件损坏，重新开始: {e}")
    return None

def update_hypothesis(state, new_finding):
    """更新假设 (这是 Continuity 的关键)"""
    state.current_hypothesis = f"基于发现 '{new_finding}'，我目前的假设是..." 
    # 在实际 V4 中，这里应该调用 LLM 来综合生成新假设
    save_state(state)