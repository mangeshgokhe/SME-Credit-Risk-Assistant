import pandas as pd
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
client = OpenAI(
    base_url="http://localhost:11434/v1"
)

class RetrieverAgent:
    def __init__(self, retriever):
        self.retriever = retriever

    def retrieve(self, query, top_k=5):
        return self.retriever.retrieve(query, top_k=top_k)

class AnalystAgent:
    def __init__(self, kg, financials_csv):
        self.kg = kg
        self.df = pd.read_csv(financials_csv)

    def risk_assess(self, company_name):
        dfc = self.df[self.df['company'].str.lower() == company_name.lower()]
        if dfc.empty:
            return {'score': None, 'reason': 'No financials found'}
        latest = dfc.sort_values('year', ascending=False).iloc[0]
        try:
            d_e = float(latest['total_debt'])/max(1.0, float(latest['total_equity']))
        except:
            d_e = None
        try:
            current_ratio = float(latest['current_assets'])/max(1.0, float(latest['current_liabilities']))
        except:
            current_ratio = None

        score = 100
        reasons = []
        if d_e is not None:
            if d_e > 3.0:
                score -= 40
                reasons.append(f'D/E high: {d_e:.2f}')
            elif d_e > 2.0:
                score -= 20
                reasons.append(f'D/E moderate: {d_e:.2f}')
        else:
            reasons.append('D/E unavailable')
        if current_ratio is not None and current_ratio < 1.0:
            score -= 30
            reasons.append(f'Current ratio low: {current_ratio:.2f}')
        return {'score': score, 'd_e': d_e, 'current_ratio': current_ratio, 'reason': '; '.join(reasons)}

    def synthesize_memo(self, company_name, retrieved_texts, risk_assessment, kg_insights, use_ollama):
        # If Ollama checkbock checked the it will generate polished memo; otherwise fallback to local template
        if use_ollama:
            prompt = self._build_prompt(company_name, retrieved_texts, risk_assessment, kg_insights)
            try:
                resp = client.chat.completions.create( 
                    model='llama3.2:3b', 
                    messages=[{'role':'system','content':'You are a credit analyst assistant.'},
                              {'role':'user','content':prompt}], 
                    max_tokens=500, 
                    temperature=0.0 )
                text = resp.choices[0].message.content
                #LLM 2
                resp1 = client.chat.completions.create( 
                    model='llama3.2:3b', 
                    messages=[{'role':'system','content':'You are a credit analyst assistant.'},
                              {'role':'user','content':text}], 
                    max_tokens=500, 
                    temperature=0.0 )
                LLM2 = resp1.choices[0].message.content
                return {'memo': text, 'LLM2': LLM2, 'source': 'ollama'}
            except Exception as e:
                return {'memo': f'Ollama error: {e}', 'source': 'ollama_error'}
        memo = {
            'company': company_name,
            'summary': f'Automated memo for {company_name}',
            'retrieved_evidence': [r['id'] for r in retrieved_texts],
            'risk': risk_assessment,
            'kg_insights': kg_insights,
            'verdict': 'Approve' if (risk_assessment.get('score') is None or risk_assessment.get('score',0)>=80) else 'Reject'
        }
        return {'memo': memo, 'source': 'local'}

    def _build_prompt(self, company_name, retrieved_texts, risk_assessment, kg_insights):
        parts = [
            f'Company: {company_name}',
            'Risk assessment:',
            str(risk_assessment),
            'KG insights:',
            str(kg_insights),
            'Retrieved evidence IDs:',
            ','.join([r['id'] for r in retrieved_texts])
        ]
        return '\n'.join(parts)
