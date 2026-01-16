# -*- coding: utf-8 -*-
"""
【Strategic Brain - Red Team Edition】
Persona: Devil's Advocate Supervisor.
Goal: Direct the swarm to disprove the user's hypothesis.
"""
import json
import os
import sys
import re

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import key_manager

def get_strategic_guidance(current_state_dict, recent_papers_summary):
    client = key_manager.get_client()
    model = key_manager.get_model_name()
    
    goal = current_state_dict.get('goal', 'Unknown')
    hypothesis = current_state_dict.get('current_hypothesis', 'None')
    
    print("🧠 [Level 3] Summoning Red Team Commander...")

    # 1. System Instruction (The Skeptic)
    system_instruction = """
    You are the 'Red Team Commander'. 
    User's Hypothesis: "{hypothesis}" (The goal is to ATTACK this).
    
    Your job is to identify gaps in our current attack strategy.
    Are we finding enough negative results? Are we just finding confirmation?
    
    Return strict JSON (No Markdown):
    {
        "reflection": "Reflection on the attack progress. Are we successfully challenging the hypothesis?",
        "status_check": "attacking", // or "stalled"
        "next_focus": "Where should we look next for failure cases? (e.g., 'Check for reproducibility failures')",
        "new_search_queries": ["List English queries focused on LIMITATIONS, FAILURES, and CONTRADICTIONS"]
    }
    """

    user_content = f"""
    [Target Hypothesis]: {goal}
    [Current Attack Status]: {hypothesis}
    
    [Evidence Collected So Far]:
    {recent_papers_summary}
    
    Please provide strategic attack directives.
    """
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_content}
            ],
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            return json.loads(match.group(0))
            
    except Exception as e:
        print(f"❌ Strategic decision failed: {e}")
    
    return None

def refine_search_query(failed_query, goal):
    """
    Refine queries to be more critical.
    """
    client = key_manager.get_client()
    model = key_manager.get_model_name()
    
    prompt = f"""
    We are trying to find counter-evidence for "{goal}" using query "{failed_query}", but found nothing.
    Please generate 3 CRITICAL search terms focused on limitations, failures, or debunking.
    Return strictly a Python string list: ["term1", "term2", "term3"]
    """
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
        import ast
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            return ast.literal_eval(match.group(0))
    except Exception:
        pass
    return [goal + " limitations"]