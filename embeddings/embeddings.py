from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma

from pathlib import Path
from os import listdir
from os.path import isfile, join

from pdf_processor import PDFProcessor

EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


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


def create_vector_db(docs, persist_directory="./vectordb"):
    embeddings = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL)

    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name="mis_docs",
        persist_directory=persist_directory,
    )

    vectordb.persist()

    return vectordb


def load_vector_db(persist_directory="./vectordb"):
    embeddings = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL)

    vectordb = Chroma(
        collection_name="mis_docs",
        embedding_function=embeddings,
        persist_directory=persist_directory,
    )

    return vectordb


if __name__ == "__main__":
    MANUALS_PATH = "./manuals"
    docs = preprocess_manuals(MANUALS_PATH)

    vectordb = create_vector_db(docs)

    results = vectordb.similarity_search("Veo las luz del timer parpadeando", k=3)

    for doc in results:
        print("Texto:", doc.page_content[:120], "...")
        print("PDF:", doc.metadata.get("source"))
        print("Página:", doc.metadata.get("page"))
        print("-" * 40)
