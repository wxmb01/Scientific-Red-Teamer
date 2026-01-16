# 🛡️ Scientific Red Teamer
> **An Autonomous Hypothesis Stress-Testing Agent powered by Gemini 3**

[![Built with Gemini 3](https://img.shields.io/badge/Built%20with-Gemini%203-blue)](https://ai.google.dev/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-yellow)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)](https://streamlit.io/)

## 💡 Inspiration
In the era of AI-generated content, scientific hallucinations are proliferating. Researchers don't need another tool to *summarize* papers; they need a tool to **challenge** them. 

We built the **Scientific Red Teamer** to act as an autonomous "Devil's Advocate"—a system designed specifically to find counter-evidence, detect logical gaps, and stress-test hypotheses using recursive literature auditing.

## 🚀 Key Features

* **🕵️ Turbo Auditing Engine**: Scans arXiv papers at high speed using **Level 1 Triage** (Abstract analysis) to filter for critical signals instantly.
* **🧠 L1-L3 Hierarchical Thinking**: 
    * **L1**: Rapid vulnerability scanning.
    * **L2**: Deep forensic auditing of methodology and data.
    * **L3**: Metacognitive "Strategic Review" to self-correct search bias.
* **🕸️ Live Evidence Graph**: Visualizes the recursive discovery path using **Graphviz**, highlighting high-impact counter-evidence (Red Nodes) in real-time.
* **⚡ Human-in-the-Loop**: A "Command Center" UI that allows users to inject strategic directives (e.g., "Focus on reproducibility") to steer the agent mid-run.
* **📄 Forensic Reporting**: Auto-generates a comprehensive **Markdown Audit Report** synthesizing all findings.

## ⚙️ Architecture

The system utilizes a **Recursive OODA Loop** (Observe, Orient, Decide, Act):
1.  **Brain**: Google **Gemini 3 Pro** (via API) for long-context reasoning and structured JSON output.
2.  **Memory**: SQLite & JSON State Machine for long-term persistence and crash recovery.
3.  **Tools**: `arXiv API` for real-time literature retrieval.
4.  **UI**: Streamlit for the "Red Team Command Center".

## 🛠️ Installation & Usage

### Prerequisites
* Python 3.8+
* A Google Gemini API Key

### Quick Start

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/wxmb01/Scientific-Red-Teamer.git](https://github.com/wxmb01/Scientific-Red-Teamer.git)
    cd Scientific-Red-Teamer
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: You need to install Graphviz on your system if you want the graph visualization)*

3.  **Setup API Key**
    Create a `key_manager.py` file or set your environment variable:
    ```python
    # inside key_manager.py
    import os
    def get_client():
        # ... setup google genai client with your key ...
        pass
    ```

4.  **Run the Engine (Backend)**
    ```bash
    python core/research_loop.py
    ```

5.  **Launch the Command Center (Frontend)**
    ```bash
    streamlit run app.py
    ```

## 📸 Screenshots

<img width="2541" height="1461" alt="QQ20260117-014403" src="https://github.com/user-attachments/assets/af3ebfb5-6bba-46a2-a0e6-d53a8f79e8fc" />

<img width="2538" height="1378" alt="QQ20260117-014415" src="https://github.com/user-attachments/assets/2cf643e7-7eea-4cab-9b6e-8ceeb4e0914b" />


## 📄 License
MIT License
