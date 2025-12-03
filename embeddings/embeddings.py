from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_chroma import Chroma
from llm import LLMProcessor


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


if __name__ == "__main__":
    MANUALS_PATH = "./manuals"
    vectordb = create_or_load_db(MANUALS_PATH)

    enhanced_result = LLMProcessor().enhance_query(
        "How do i connect the pipes in my Everwell model MRTH?"
    )
    enhanced_query = enhanced_result["query"]
    detected_model = enhanced_result["model"]

    print(f"Enhanced Query: {enhanced_query}")
    print(f"Detected Model: {detected_model}")

    results = vectordb.similarity_search(enhanced_query, k=3)

    for doc in results:
        print("Texto:", doc.page_content[:120], "...")
        print("PDF:", doc.metadata.get("source"))
        print("Página:", doc.metadata.get("page"))
        print("Models:", doc.metadata.get("models"))
        print("-" * 40)
