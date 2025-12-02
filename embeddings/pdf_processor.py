import re
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders.parsers import TesseractBlobParser
from langchain_text_splitters import RecursiveCharacterTextSplitter


class PDFProcessor:
    def __init__(self, chunk_size=800, overlap=50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def clean_pdf_text(self, text: str) -> str:
        # Normalizar espacios en blanco
        text = re.sub(r"\s+", " ", text)

        # Quitar guiones de separación silábica (ej: "proce-\nsamiento" -> "procesamiento")
        text = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", text)

        # Normalizar saltos de línea (quitar los que están en medio de párrafos)
        text = re.sub(r"(?<=[a-z,])\n(?=[a-z])", " ", text)

        # Preservar saltos de línea importantes (títulos, listas)
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Quitar caracteres de control raros
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)

        # 6. Normalizar comillas y símbolos comunes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(""", "'").replace(""", "'")
        text = text.replace("–", "-").replace("—", "-")

        # Quitar espacios antes de puntuación
        text = re.sub(r"\s+([.,;:!?])", r"\1", text)

        return text.strip()

    def process(self, pdf_path):
        loader = PyMuPDFLoader(
            pdf_path,
            mode="page",
            images_parser=TesseractBlobParser(),
        )

        docs = loader.load()

        for doc in docs:
            doc.page_content = self.clean_pdf_text(doc.page_content)

        og_size = len(docs)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.overlap
        )

        chunks = text_splitter.split_documents(docs)

        print(f"Procesado {pdf_path}: {og_size} páginas -> {len(chunks)} chunks")

        return chunks
