# -*- coding: utf-8 -*-
"""
【Scholar Brain - Turbo Red Team Edition】
Persona: Scientific Red Teamer.
Optimization: Reads only the first 5000 chars (Abstract/Intro) for ultra-fast auditing.
"""
import json
import time
import sys
import os
import re

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import key_manager
import pdf_reader 

def extract_json_content(text):
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return None
    except Exception:
        return None

# === Level 1: Vulnerability Scan (Triage) ===
def assess_relevance(paper_title, paper_summary, target_hypothesis):
    """
    Decide if this paper contains potential counter-evidence.
    """
    client = key_manager.get_client()
    model = key_manager.get_model_name()
    
    system_prompt = f"""
    You are a Scientific Red Teamer. Target Hypothesis to Attack: "{target_hypothesis}".
    Scan this abstract to see if it offers CRITICAL perspectives, COUNTER-EVIDENCE, or reveals LIMITATIONS.
    
    Return strict JSON:
    {{
        "decision": "accept", 
        "reason": "Why is this relevant? (English, 1 sentence)"
    }}
    
    Criteria:
    1. REJECT if purely promotional.
    2. ACCEPT if it mentions limitations, failures, or alternative theories.
    """
    
    user_prompt = f"Title: {paper_title}\nAbstract: {paper_summary}"
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1
        )
        return extract_json_content(response.choices[0].message.content)
    except Exception:
        return {"decision": "accept", "reason": "Potential signal detected (Error fallback)."}

# === Level 2: Critical Deep Dive (Turbo Mode) ===
def brain_process_paper(file_path, target_hypothesis):
    filename = os.path.basename(file_path)
    raw_text = pdf_reader.read_pdf(file_path)
    
    if not raw_text or len(raw_text) < 100:
        return {"error": "Cannot read PDF content", "score": 0}

    # 🔥 TURBO PATCH: Only read the first 5000 characters (Abstract + Intro)
    # This is enough to find the "Main Contribution" and "Limitations" without reading the whole math proofs.
    input_text = raw_text[:5000] 
    
    client = key_manager.get_client()
    model = key_manager.get_model_name()

    # === RED TEAM PROMPT ===
    system_prompt = f"""
    You are 'The Red Teamer', an autonomous scientific critic. 
    Target Hypothesis to Stress-Test: "{target_hypothesis}".
    
    Based on the Abstract and Introduction provided, AUDIT this paper.
    Look for: Logical fallacies, claimed limitations, or contradictions to the target.

    Return strict JSON:
    {{
        "title": "Paper Title (English)",
        "score": 8.5, // Critical Impact Score (10 = Total Refutation)
        "summary": "Brief Context (English)",
        "flaws": "List potential flaws or limitations mentioned (English)",
        "contradiction": "Does this contradict the target hypothesis? (Yes/No + Reason)",
        "thought_signature": "Use First Person ('I'). Explain why this evidence makes us skeptical of the target. Be harsh and quick.",
        "suggested_queries": [
            "2-3 English search queries to find MORE counter-evidence"
        ]
    }}
    """

    try:
        start_time = time.time()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Paper Extract (Start):\n{input_text}..."}
            ],
            temperature=0.2
        )
        end_time = time.time()
        
        result_json = extract_json_content(response.choices[0].message.content)
        
        if result_json:
            result_json['cost_time'] = f"{end_time - start_time:.2f}s"
            return result_json
        else:
            return {"error": "JSON parsing failed"}

    except Exception as e:
        return {"error": str(e)}