from sentence_transformers import SentenceTransformer
import faiss
import pickle

EMB_MODEL = 'all-MiniLM-L6-v2'
INDEX_PATH = 'emb_index.faiss'
META_PATH = 'emb_meta.pkl'

def build_embeddings(docs, force_rebuild=False):
    model = SentenceTransformer(EMB_MODEL)

    texts = [d['text'] for d in docs]
    ids = [d['id'] for d in docs]
    decisions = [d.get('decision', None) for d in docs]
    companys = [d.get('company', None) for d in docs]

    embs = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    dim = embs.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embs)

    meta = {'ids': ids, 'companys': companys, 'texts': texts, 'decisions':decisions}
    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, 'wb') as f:
        pickle.dump(meta, f)

    return model, index, meta

def query_faiss(index, meta, model, query, top_k=5):
    q_emb = model.encode([query], convert_to_numpy=True)
    D, I = index.search(q_emb, top_k)
    results = []
    for dist_list, idx_list in zip(D, I):
        for d, i in zip(dist_list, idx_list):
            results.append({'id': meta['ids'][i],'company': meta['companys'][i], 'text': meta['texts'][i], 'decision': meta['decisions'][i], 'score': float(d)})
    return results
