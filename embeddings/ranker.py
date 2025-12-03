from sentence_transformers import CrossEncoder
from typing import List
from langchain_core.documents import Document


class LocalReranker:
    def __init__(self, model_name="BAAI/bge-reranker-v2-m3"):
        self.model = CrossEncoder(model_name, max_length=512)
        self.model_name = model_name

    def rerank(self, query, documents, top_n=5):
        if not documents:
            return []

        pairs = [[query, doc.page_content] for doc in documents]

        scores = self.model.predict(pairs)

        doc_score_pairs = list(zip(documents, scores))
        doc_score_pairs.sort(key=lambda x: x[1], reverse=True)

        ranked_docs = [doc for doc, score in doc_score_pairs[:top_n]]

        for i, (doc, score) in enumerate(doc_score_pairs[:top_n]):
            doc.metadata["rerank_score"] = float(score)
            doc.metadata["rerank_position"] = i + 1

        return ranked_docs

    def rerank_with_scores(self, query: str, documents, top_n=5):
        if not documents:
            return []

        pairs = [[query, doc.page_content] for doc in documents]
        scores = self.model.predict(pairs)

        doc_score_pairs = list(zip(documents, scores))
        doc_score_pairs.sort(key=lambda x: x[1], reverse=True)

        for i, (doc, score) in enumerate(doc_score_pairs[:top_n]):
            doc.metadata["rerank_score"] = float(score)
            doc.metadata["rerank_position"] = i + 1

        return doc_score_pairs[:top_n]


def create_reranker(model_name="BAAI/bge-reranker-v2-m3"):
    return LocalReranker(model_name=model_name)
