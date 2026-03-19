import re
from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


from pathlib import Path
from os import listdir
from os.path import isfile, join

from pdf_processor import PDFProcessor

EMBEDDING_MODEL = "paraphrase-multilingual-mpnet-base-v2"
COLLECTION_NAME = "manuals_v1"
PERSIST_DIRECTORY = "./vectordb_v1"


def preprocess_manuals(manuals_path):
    if not Path(manuals_path).exists():
        raise FileNotFoundError(f"La ruta {manuals_path} no existe.")

    processor = PDFProcessor()

    files = [f for f in listdir(manuals_path) if isfile(join(manuals_path, f))]

    docs = []

    for file in files:
        chunks_docs = processor.process(join(manuals_path, file))
        docs.extend(chunks_docs)

    return docs


def create_vector_db(docs, persist_directory=PERSIST_DIRECTORY):
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=persist_directory,
        collection_metadata={"hnsw:space": "cosine"},
    )

    return vectordb


def load_vector_db(persist_directory=PERSIST_DIRECTORY):
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    vectordb = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=persist_directory,
    )

    return vectordb


def create_or_load_db(manuals_path=None):
    if not Path(PERSIST_DIRECTORY).exists() and manuals_path is not None:
        docs = preprocess_manuals(manuals_path)
        return create_vector_db(docs)
    else:
        return load_vector_db()


def model_matches(models, pattern):
    if not models:
        return False
    if isinstance(models, list):
        return any(pattern.search(str(model)) for model in models)
    return pattern.search(str(models))


def map_result(result, score=None):
    source_stem = Path(result.metadata.get("source")).stem
    page = result.metadata.get("page")
    doc_id = f"{source_stem}_p{page}"

    return {
        "text": result.page_content,
        "source": source_stem,
        "page": page,
        "score": score,
        "doc_id": doc_id,
        "title": result.metadata.get("title"),
        "models": result.metadata.get("models"),
    }


def search_db(query, vectordb, reranker, processor, k=5, optimize=True, rerank=True):
    if not optimize:
        results_with_scores = vectordb.similarity_search_with_relevance_scores(query, k=k)
        if rerank:
            docs = [doc for doc, _ in results_with_scores]
            reranked = reranker.rerank(query, docs, top_n=5)
            return [map_result(doc, doc.metadata.get("rerank_score")) for doc in reranked]

        return [map_result(doc, score) for doc, score in results_with_scores]

    enhanced_result = processor.enhance_query(query)
    enhanced_query = enhanced_result["query"]
    detected_model = enhanced_result["model"]

    if detected_model:
        initial_results_with_scores = vectordb.similarity_search_with_relevance_scores(enhanced_query, k=50)

        pattern = re.compile(re.escape(detected_model), re.IGNORECASE)
        filtered = [
            (doc, score)
            for doc, score in initial_results_with_scores
            if model_matches(doc.metadata.get("models"), pattern)
        ]

        initial_results_with_scores = filtered if filtered else initial_results_with_scores[:5]

    else:
        initial_results_with_scores = vectordb.similarity_search_with_relevance_scores(
            enhanced_query,
            k=5,
        )

    if rerank:
        docs = [doc for doc, _ in initial_results_with_scores]
        reranked = reranker.rerank(query, docs, top_n=5)
        return [map_result(doc, doc.metadata.get("rerank_score")) for doc in reranked]

    return [map_result(doc, score) for doc, score in initial_results_with_scores]


if __name__ == "__main__":
    MANUALS_PATH = "./manuals"
    vectordb = create_or_load_db(MANUALS_PATH)
