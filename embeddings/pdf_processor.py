import re
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders.parsers import TesseractBlobParser
from langchain_text_splitters import RecursiveCharacterTextSplitter


class PDFProcessor:
    def __init__(self, chunk_size=500, overlap=50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def clean_text(self, text):
        text = re.sub(r"\n\s*\n", "\n\n", text)
        text = re.sub(r" +", " ", text)
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
        return text.strip()

    def process(self, pdf_path):
        loader = PyMuPDFLoader(
            pdf_path,
            mode="page",
            images_parser=TesseractBlobParser(),
        )

        docs = loader.load()

        og_size = len(docs)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.overlap
        )

        chunks = text_splitter.split_documents(docs)

        print(f"Procesado {pdf_path}: {og_size} páginas -> {len(chunks)} chunks")

        return chunks
