POC: SME Credit Risk Assistant (Simplified)

This lightweight POC demonstrates:
- In-memory Knowledge Graph (networkx)
- Dense retrieval only (SentenceTransformers + FAISS)
- Two agents: RetrieverAgent and AnalystAgent
- Streamlit UI to run a query and view evidence + memo
- Optional use of OpenAI (set OPENAI_API_KEY in .env) to generate polished memos

Setup
-----
Open Spyder app - project - new project -> existing directory
Open Anaconda promt -> Go to location where the project kept
1. Create conda env (recommended):
    conda env create -f environment.yml
    conda activate poc-sme-my-project

2. (Optional) Add OpenAI key:
    cp .env.example .env
    # edit .env and set OPENAI_API_KEY=

Run
---
# CLI demo
python main.py

# Streamlit UI (recommended)
open new annaconda
streamlit run app.py

Notes
-----
- This is a small-scale POC with synthetic sample data in `data/`.
- No external databases or services required (embeddings built locally).
- If OPENAI_API_KEY is set, AnalystAgent will call OpenAI to produce the final memo; otherwise a local heuristic memo is generated.
