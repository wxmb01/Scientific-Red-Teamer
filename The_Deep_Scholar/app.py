# -*- coding: utf-8 -*-
import streamlit as st
import sqlite3
import pandas as pd
import os
import time
import json
import sys
import graphviz # Streamlit native support

# Core imports
sys.path.append(os.path.join(os.path.dirname(__file__), "core"))
import writer_agent

# === Page Config ===
st.set_page_config(
    page_title="Scientific Red Team - Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === Paths ===
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(CURRENT_DIR, "data", "scholar_memory.db")
STATE_PATH = os.path.join(CURRENT_DIR, "data", "agent_state.json")

# === Styling ===
st.markdown("""
<style>
    .stProgress > div > div > div > div { background-color: #D32F2F; }
    .state-box {
        padding: 20px;
        background-color: #fff1f0;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 20px;
    }
    .metric-label { font-size: 0.8em; color: #555; }
    div[data-testid="stMetricValue"] { color: #D32F2F; }
    h1, h2, h3 { font-family: 'Helvetica Neue', sans-serif; }
</style>
""", unsafe_allow_html=True)

# === Data Functions ===
def load_db_data():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame(), pd.DataFrame()
    try:
        conn = sqlite3.connect(DB_PATH)
        # Fetch parent_id for graph visualization
        df_done = pd.read_sql_query("SELECT id, title, score, summary, processed_time, parent_id FROM papers WHERE status='done' ORDER BY processed_time DESC", conn)
        df_pending = pd.read_sql_query("SELECT title, status FROM papers WHERE status!='done' ORDER BY added_time ASC", conn)
        conn.close()
        return df_done, df_pending
    except:
        return pd.DataFrame(), pd.DataFrame()

def load_agent_state():
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return None

def inject_human_command(command, new_strategy):
    state = load_agent_state()
    if state:
        state['last_thought'] = f"[Commander Override] {command}"
        state['current_hypothesis'] = f"[Directed Attack] {command}"
        if new_strategy != "Keep Current":
            state['strategy'] = new_strategy
        with open(STATE_PATH, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        return True
    return False

# === Graph Visualization Function ===
def render_evidence_graph(df):
    if df.empty:
        return
    
    graph = graphviz.Digraph()
    graph.attr(rankdir='LR', bgcolor='transparent')
    graph.attr('node', shape='box', style='filled', fontname='Helvetica')
    
    # Root Node
    graph.node('ROOT', 'Target Hypothesis', fillcolor='#333333', fontcolor='white', shape='octagon')
    
    for _, row in df.iterrows():
        # Truncate title
        short_title = (row['title'][:20] + '..') if len(row['title']) > 20 else row['title']
        node_id = str(row['id'])
        
        # Color based on Impact Score
        score = row['score'] if row['score'] else 0
        if score >= 8.0:
            color = '#ffcccb' # Light Red
            border = '#D32F2F'
        elif score >= 5.0:
            color = '#ffffff'
            border = '#999999'
        else:
            color = '#f0f0f0'
            border = '#cccccc'
            
        label = f"{short_title}\n(Impact: {score})"
        graph.node(node_id, label, fillcolor=color, color=border)
        
        # Edges
        parent = row['parent_id']
        if parent:
            graph.edge(str(parent), node_id)
        else:
            graph.edge('ROOT', node_id)
            
    st.graphviz_chart(graph, use_container_width=True)

# === Sidebar ===
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3557/3557635.png", width=50)
    st.title("🛡️ Red Team OS")
    st.caption("v6.0 Turbo Edition")
    st.markdown("---")
    
    st.subheader("⚡ Override Controls")
    human_msg = st.text_input("Inject Vector", placeholder="e.g., 'Check reproducibility'")
    new_strat = st.selectbox("Strategy", ["Keep Current", "broad_scan", "deep_audit"])
    
    if st.button("🚨 EXECUTE ORDER"):
        if inject_human_command(human_msg, new_strat):
            st.success("Order Sent.")
            time.sleep(1)
            st.rerun()

    st.markdown("---")
    if st.button("📄 Generate Audit Report"):
        with st.spinner("Compiling Forensics..."):
            current_state = load_agent_state()
            goal = current_state.get('goal', "Hypothesis") if current_state else "Hypothesis"
            report_text, file_path = writer_agent.generate_report(goal)
            if file_path:
                st.session_state['report_text'] = report_text
                st.session_state['report_path'] = file_path
                st.success("Report Ready.")

# === Main Layout ===
st.title("🛡️ Scientific Red Teamer")
st.caption("Autonomous Hypothesis Stress-Testing System (Powered by Gemini 3)")

df_done, df_pending = load_db_data()
agent_state = load_agent_state()

# 1. State Monitor
if agent_state:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Audit Steps", agent_state.get('step_count', 0))
    c2.metric("Phase", agent_state.get('strategy', 'Unknown').upper())
    c3.metric("Evidence", f"{len(df_done)} Docs")
    c4.metric("Resistance", agent_state.get('failed_attempts', 0))

    st.markdown(f"""
    <div class="state-box">
        <h4 style="margin-top:0;">🎯 Target Hypothesis</h4>
        <p style="font-size:18px; font-weight: 500; color: #b71c1c;">{agent_state.get('current_hypothesis', 'Initializing...')}</p>
        <hr style="border-top: 1px solid #ffcdcd;">
        <small>💭 <b>System Thought:</b> {agent_state.get('last_thought', 'Waiting...')}</small>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("⚠️ Backend Offline. Run 'research_loop.py' to start.")

# 2. Evidence Graph (NEW FEATURE)
if not df_done.empty:
    with st.expander("🕸️ Evidence Trail (Knowledge Graph)", expanded=True):
        st.caption("Visualizing the recursive discovery path. Red nodes indicate high-impact counter-evidence.")
        render_evidence_graph(df_done)

# 3. Report Download
if 'report_text' in st.session_state:
    with st.expander("📄 Forensic Report", expanded=True):
        st.markdown(st.session_state['report_text'])
        with open(st.session_state['report_path'], "rb") as file:
            st.download_button("⬇️ Download .md", file, os.path.basename(st.session_state['report_path']))

# 4. Logs
st.divider()
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🛑 Forensic Logs")
    if not df_done.empty:
        for i, row in df_done.iterrows():
            with st.expander(f"[{row['score']}/10] {row['title']}", expanded=(i==0)):
                st.markdown(f"**Findings:** {row.get('summary', '')}")
                st.caption(f"Time: {row['processed_time']}")
    else:
        st.info("Scanning...")

with col2:
    st.subheader("⏳ Scan Queue")
    if not df_pending.empty:
        st.dataframe(df_pending[['title', 'status']], hide_index=True, use_container_width=True)

time.sleep(2)
st.rerun()