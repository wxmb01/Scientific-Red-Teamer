# -*- coding: utf-8 -*-
"""
【The Red Team Engine - Turbo V6.0】
Optimization: High concurrency, low latency, instant start.
"""
import time
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import db_manager
import arxiv_client
import scholar_brain
import state_manager
import strategic_brain

# 🔥 TURBO SETTINGS
STRATEGY_CHECKPOINT_INTERVAL = 5 # Less meetings, more work
MAX_STEPS = 100 

def start_autonomous_system(goal="Hypothesis to Attack"):
    db_manager.init_db()
    
    state = state_manager.load_state()
    if not state:
        print(f"🛡️ [Red Team] TURBO MODE Initiated on: {goal}")
        state = state_manager.ResearchState(goal)
        state_manager.save_state(state)
        # Initial Attack
        perform_search(goal + " limitations failures", state)
    else:
        print(f"🛡️ [Red Team] Resuming Audit on: {state.goal}")

    while state.step_count < MAX_STEPS:
        
        # === Phase 0: Strategic Checkpoint ===
        if state.step_count > 0 and state.step_count % STRATEGY_CHECKPOINT_INTERVAL == 0:
            print(f"\n🛑 === [CheckPoint] Strategic Attack Review ===")
            recent_summary = "Recent Evidence:\n" + "\n".join(state.known_facts[-3:]) 
            
            guidance = strategic_brain.get_strategic_guidance(state.to_dict(), recent_summary)
            
            if guidance:
                print(f"🧠 [Commander] Reflection: {guidance.get('reflection', 'N/A')}")
                
                state.last_thought = f"Strategic Review: {guidance.get('reflection')}"
                state.strategy = guidance.get('status_check', 'attacking')
                
                if guidance.get('new_search_queries'):
                    print(f"🔧 [Correction] Pivoting Attack: {guidance['new_search_queries']}")
                    for q in guidance['new_search_queries']:
                        perform_search(q, state)
                
                state_manager.save_state(state)
            print("==============================================\n")

        state.step_count += 1
        print(f"⚡ === Step {state.step_count} (Phase: {state.strategy}) ===")
        
        # === Phase 1: Get Task ===
        task = db_manager.get_next_task()
        
        # === Phase 2: Self-Correction ===
        if not task:
            state.failed_attempts += 1
            print(f"⚠️ Queue Empty (Attempt {state.failed_attempts})")
            
            if state.failed_attempts >= 2:
                print("🤔 [Self-Correct] Generating critical queries...")
                new_queries = strategic_brain.refine_search_query(state.goal, state.goal)
                if new_queries:
                    print(f"✨ New Attack Vectors: {new_queries}")
                    for q in new_queries:
                        perform_search(q, state)
                    state.failed_attempts = 0
                else:
                    time.sleep(1) # Reduced sleep
            continue
        
        state.failed_attempts = 0
        paper_id = task['id']
        paper_title = task['title']
        target_path = task['url']
        
        print(f"📋 [Auditing] {paper_title[:50]}...")
        
        if not target_path or not os.path.exists(target_path):
             print(f"⬇️ Acquiring Evidence: {paper_id}")
             papers = arxiv_client.search_papers(paper_id, max_results=1)
             if papers: target_path = papers[0]['path']
             else:
                 print("❌ Failed to acquire.")
                 db_manager.update_paper_status(paper_id, "error")
                 continue
        
        db_manager.update_paper_status(paper_id, "processing")
        
        # Level 2 Auditing
        analysis = scholar_brain.brain_process_paper(target_path, state.goal)
        
        if "error" not in analysis:
            score = analysis.get('score', 0)
            signature = analysis.get('thought_signature', '')
            
            print(f"✍️ [Forensic Note] {signature[:100]}...")
            db_manager.update_paper_status(paper_id, "done", result_data=analysis, local_path=target_path)
            
            if score > 5.0: 
                fact = f"[{paper_title}] -> {analysis.get('flaws') or analysis.get('summary')}"
                state.known_facts.append(fact)
                state.current_hypothesis = f"Evidence from {paper_title} suggests flaws in {state.goal}"
            
            new_leads = analysis.get('suggested_queries', [])
            if new_leads:
                perform_search(new_leads[0], state, parent_id=paper_id)
                
            state_manager.save_state(state)
        else:
            db_manager.update_paper_status(paper_id, "error")

        # 🔥 TURBO: Almost no sleep between tasks
        time.sleep(0.1)

def perform_search(query, state, parent_id=None):
    print(f"🕵️‍♀️ [Scan] Query: '{query}'")
    # 🔥 TURBO: Grab 5 papers at once to keep the queue full
    papers = arxiv_client.search_papers(query, max_results=5)
    count = 0
    for p in papers:
        filename = os.path.basename(p['path'])
        clean_id = filename.split("_")[0]
        info = {"id": clean_id, "title": p['title'], "url": p['path']}
        if db_manager.add_paper_to_queue(info, parent_id=parent_id):
            count += 1
            
    if count > 0:
        state.last_thought = f"Found {count} potential evidence docs for '{query}'."
        state_manager.save_state(state)
    print(f"📥 Queued {count} Targets")

if __name__ == "__main__":
    # 🔥 AUTO-CLEANUP: Wipe memory for a fresh speed run
    if os.path.exists("data/scholar_memory.db"):
        try: os.remove("data/scholar_memory.db")
        except: pass
    if os.path.exists("data/agent_state.json"):
        try: os.remove("data/agent_state.json")
        except: pass
        
    # 🔥 FASTEST ATTACK TOPIC:
    target = "Large Language Models often hallucinate and fail in simple reasoning"
    start_autonomous_system(target)