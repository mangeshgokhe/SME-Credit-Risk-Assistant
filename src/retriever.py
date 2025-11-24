from src.embeddings import build_embeddings, query_faiss

class Retriever:
    def __init__(self, docs):
        self.docs = docs
        self.model, self.index, self.meta = build_embeddings(self.docs)

    def retrieve(self, query, top_k=1):
        return query_faiss(self.index, self.meta, self.model, query, top_k=top_k)
