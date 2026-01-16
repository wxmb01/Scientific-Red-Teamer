# -*- coding: utf-8 -*-
"""
【The Writer Agent - Red Team Edition】
Function: Synthesize critical findings into a 'Hypothesis Stress-Test Report'.
"""
import sqlite3
import os
import sys
import datetime

# Path Fix
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import key_manager

DB_PATH = os.path.join(os.path.dirname(current_dir), "data", "scholar_memory.db")
REPORT_DIR = os.path.join(os.path.dirname(current_dir), "workspace")

def fetch_all_findings():
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Fetch score as 'Critical Impact Score'
    cursor.execute("SELECT title, summary, score, url FROM papers WHERE status='done' ORDER BY score DESC")
    rows = cursor.fetchall()
    conn.close()
    
    papers = []
    for r in rows:
        papers.append({
            "title": r["title"],
            "summary": r["summary"], 
            "score": r["score"],
            "url": r["url"]
        })
    return papers

def generate_report(target_hypothesis="Unknown"):
    papers = fetch_all_findings()
    
    if not papers:
        return "No evidence collected yet."

    print(f"✍️ [Writer] Compiling Red Team Audit Report...")
    
    papers_text = ""
    for idx, p in enumerate(papers, 1):
        papers_text += f"""
        {idx}. Title: {p['title']} (Critical Impact: {p['score']}/10)
           Findings/Flaws: {p['summary']}
        """

    client = key_manager.get_client()
    model = key_manager.get_model_name()

    system_prompt = f"""
    You are a Lead Scientific Auditor.
    The user submitted the hypothesis: "{target_hypothesis}".
    Your job is to write a "Hypothesis Stress-Test Report" based on the red team's findings.

    Requirements:
    1. **Title**: "Scientific Red Team Audit: [Hypothesis Name]"
    2. **Verdict**: START with a clear verdict (e.g., "Hypothesis Credible", "Significant Risks Detected", or "Hypothesis Debunked").
    3. **Key Vulnerabilities**: List the major flaws, contradictions, or limitations found in the literature.
    4. **Evidence Analysis**: Group the papers that provide counter-evidence.
    5. **Tone**: Critical, Objective, Forensic.
    6. **Language**: STRICTLY ENGLISH.
    
    Base your report ONLY on the provided evidence notes.
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Red Team Evidence Logs:\n{papers_text}"}
            ],
            temperature=0.3
        )
        
        report_content = response.choices[0].message.content
        
        if not os.path.exists(REPORT_DIR):
            os.makedirs(REPORT_DIR)
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"RedTeam_Audit_{timestamp}.md"
        file_path = os.path.join(REPORT_DIR, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(report_content)
            
        print(f"✅ [Writer] Audit saved to: {file_path}")
        return report_content, file_path

    except Exception as e:
        return f"Report generation failed: {str(e)}", None

if __name__ == "__main__":
    generate_report("LLMs can reason like humans")