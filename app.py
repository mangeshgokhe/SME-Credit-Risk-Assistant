import streamlit as st
from src.utils import read_text_files_in_dir, read_json_files_in_dir
from src.retriever import Retriever
from src.kg import KG
from src.agents import RetrieverAgent, AnalystAgent
import os

st.set_page_config(page_title='SME Credit POC', layout='wide')

st.title('SME Credit Risk Assistant')

st.sidebar.header('Controls')
company = st.sidebar.text_input('Company name', 'King Hall and Co. Corp')
directors = st.sidebar.text_input('Directors', 'Nitin Sharma')
revenue = st.sidebar.text_input('Revenue', '3.2 Cr')
profit = st.sidebar.text_input('Profit', '22 lakh')
loanRequested = st.sidebar.text_input('Loan Requested', '50 lakh')
purpose = st.sidebar.text_input('Company name', 'Working capital')

policies = read_text_files_in_dir(os.path.join('data','policies'))
memos = read_json_files_in_dir(os.path.join('data','memos'))
memo_docs = [{'id': m.get('id'), 'company': m.get('company'), 'text': m.get('summary','') + '\n' + m.get('notes',''), 'decision': m.get('decision')} for m in memos]
if company:
    memo_docs = [d for d in memo_docs if d.get('company') == company]
docs = policies + memo_docs

top_k = st.sidebar.slider('Top K retrieval', 1, 5, 2)
use_ollama = st.sidebar.checkbox('Use Ollama to generate published memo', value=False)

required_fields = {
    "Company name": company,
    "Directors": directors,
    "Revenue": revenue,
    "Profit": profit,
    "Loan Requested": loanRequested,
    "Purpose": purpose,
}

missing = [name for name, value in required_fields.items() if not value.strip()]
disable_button = len(missing) > 0

if disable_button:
    st.sidebar.warning(f"Missing required fields: {', '.join(missing)}")

run = st.sidebar.button('Run Analysis', disabled=disable_button)

if run:
    with st.spinner('Building retriever and KG (first run may take time)...'):
        retriever = Retriever(docs)
        r_agent = RetrieverAgent(retriever)
        kg = KG()
        kg.load_from_csv(os.path.join('data','kg_nodes.csv'), os.path.join('data','kg_edges.csv'))
        analyst = AnalystAgent(kg, os.path.join('data','financials.csv'))

        query = (
            f"Should we approve this SME loan for {company}, whose directors are {directors}, "
            f"request of {loanRequested} for {purpose}? Provide policy-aligned justification and reason for approved or reject"
        )

    retrieved = r_agent.retrieve(query, top_k=top_k)
    st.subheader('Retrieved Evidence')
    for r in retrieved:
        st.markdown(f"**{r['id']}** — score: {r['score']:.4f}\n\n{r['text']}")
    risk = analyst.risk_assess(company)
    st.subheader('Risk Assessment')
    st.json(risk)
    comp_node = kg.find_company_node(company)
    kg_insights = {}
    if comp_node:
        kg_insights['directors'] = kg.get_company_directors(comp_node)
    st.subheader('KG Insights')
    st.json(kg_insights)
    memo = analyst.synthesize_memo(company, retrieved, risk, kg_insights, use_ollama)
    st.subheader('Final Memo LLM1')
    if memo.get('source') == 'ollama':
        st.markdown(memo['memo'])
        st.subheader('Final Memo LLM2')
        st.markdown(memo['LLM2'])
    else:
        st.json(memo['memo'])
