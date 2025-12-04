from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_chroma import Chroma
from llm import LLMProcessor
import re


from pathlib import Path
from os import listdir
from os.path import isfile, join

from pdf_processor import PDFProcessor

EMBEDDING_MODEL = "paraphrase-multilingual-mpnet-base-v2"
COLLECTION_NAME = "manuals"
PERSIST_DIRECTORY = "./vectordb"


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
    embeddings = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL)

    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=persist_directory,
    )

    return vectordb


def load_vector_db(persist_directory=PERSIST_DIRECTORY):
    embeddings = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL)

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


def map_result(result):
    return {
        "text": result.page_content,
        "source": result.metadata.get("source"),
        "page": result.metadata.get("page"),
        "title": result.metadata.get("title"),
        "models": result.metadata.get("models"),
    }


def search_db(query, vectordb, reranker, processor, k=5, optimize=True, rerank=False):
    if not optimize:
        results = vectordb.similarity_search(query, k=k)
        results = results if not rerank else reranker.rerank(query, results, top_n=5)
        return [map_result(doc) for doc in results]

    enhanced_result = processor.enhance_query(query)
    enhanced_query = enhanced_result["query"]
    detected_model = enhanced_result["model"]

    if detected_model:
        initial_results = vectordb.similarity_search(enhanced_query, k=50)

        initial_results = (
            initial_results
            if not rerank
            else reranker.rerank(query, initial_results, top_n=5)
        )

        pattern = re.compile(re.escape(detected_model), re.IGNORECASE)
        filtered = [
            doc
            for doc in initial_results
            if model_matches(doc.metadata.get("models"), pattern)
        ]

        initial_results = filtered if filtered else initial_results[:5]

        return [map_result(doc) for doc in initial_results]
    else:
        initial_results = vectordb.similarity_search(
            enhanced_query,
            k=50,
        )

    initial_results = (
        initial_results
        if not rerank
        else reranker.rerank(query, initial_results, top_n=5)
    )

    return [map_result(doc) for doc in initial_results]


if __name__ == "__main__":
    MANUALS_PATH = "./manuals"
    vectordb = create_or_load_db(MANUALS_PATH)
