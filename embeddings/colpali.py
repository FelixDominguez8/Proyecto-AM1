import sys
from pathlib import Path
from typing import Generator, List, Tuple

import torch
from colpali_engine.models import ColIdefics3, ColIdefics3Processor
from pdf2image import convert_from_path, pdfinfo_from_path
from PIL import Image
from tqdm import tqdm
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import (
    BinaryQuantization,
    BinaryQuantizationConfig,
    Distance,
    MultiVectorComparator,
    MultiVectorConfig,
    PointStruct,
    VectorParams,
)
import argparse


from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "vidore/colSmol-500M"
QDRANT_COLLECTION = "hvac_index" 
BATCH_SIZE = 30
EMBEDDING_DIM = 128


def iter_pdf_batches(
    pdf_paths: List[Path],
    dpi: int = 150,
    batch_size: int = BATCH_SIZE,
) -> Generator[Tuple[List[Image.Image], List[dict]], None, None]:
    batch_images: List[Image.Image] = []
    batch_meta: List[dict] = []

    for doc_id, pdf_path in enumerate(pdf_paths):
        # Carga el PDF en chunks de `batch_size` páginas para no saturar RAM
        total_pages = pdfinfo_from_path(str(pdf_path))["Pages"]

        for chunk_start in range(1, total_pages + 1, batch_size):
            chunk_end = min(chunk_start + batch_size - 1, total_pages)
            chunk = convert_from_path(
                str(pdf_path), dpi=dpi, first_page=chunk_start, last_page=chunk_end
            )
            for i, img in enumerate(chunk):
                page_num = chunk_start - 1 + i  # 0-indexed
                batch_images.append(img)
                batch_meta.append(
                    {
                        "doc_id": doc_id,
                        "page_num": page_num,
                        "source": Path(pdf_path).name,
                    }
                )
                if len(batch_images) == batch_size:
                    yield batch_images, batch_meta
                    batch_images = []
                    batch_meta = []

    if batch_images:
        yield batch_images, batch_meta


class ColPaliEmbedder:
    def __init__(self):
        # self.qdrant = QdrantClient(
        #     url=os.getenv("QDRANT_URL"),
        #     api_key=os.getenv("QDRANT_API"),
        # )
        self.qdrant = QdrantClient(url="http://localhost:6333")
        self.model = ColIdefics3.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.bfloat16,
            device_map="cuda:0",
        ).eval()
        self.processor = ColIdefics3Processor.from_pretrained(MODEL_NAME)

    def create_collection(self):
        """Crea la coleccion en Qdrant con soporte multi-vector."""

        self.qdrant.recreate_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=EMBEDDING_DIM,
                distance=Distance.COSINE,
                on_disk=True,
                quantization_config=BinaryQuantization(
                    binary=BinaryQuantizationConfig(always_ram=True)
                ),
                multivector_config=MultiVectorConfig(
                    comparator=MultiVectorComparator.MAX_SIM
                ),
            ),
        )
        print(f"Coleccion '{QDRANT_COLLECTION}' creada en Qdrant")


    def load_pdfs(self, dir_path: str) -> List[Path]:
        path = Path(dir_path)
        if not path.is_dir():
            raise ValueError(f"'{dir_path}' no es un directorio")
        pdfs = sorted(path.glob("*.pdf"))
        if not pdfs:
            print("No hay PDFs en el directorio")

        print(f"Cargando {len(pdfs)} PDFs")
        return pdfs

    def embed_batch(self, images: List[Image.Image], batch_meta: List[dict]) -> List[List[float]]:
        try:
            with torch.no_grad():
                inputs = self.processor.process_images(images).to(self.model.device)
                embeddings = self.model(**inputs)
                points = [
                    PointStruct(
                        id=m["doc_id"] * 10_000 + m["page_num"],
                        vector=emb,
                        payload=m,
                    )
                    for m, emb in zip(batch_meta, embeddings)
                ]
                self.qdrant.upsert(collection_name=QDRANT_COLLECTION, points=points)
                result = [emb.float().cpu().tolist() for emb in embeddings]
            del inputs
            torch.cuda.empty_cache()
            return result
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            if len(images) == 1:
                print("WARN: OOM con 1 imagen, procesando en CPU")
                self.model.to("cpu")
                result = self.embed_batch(images, batch_meta)
                self.model.to("cuda:0")
                return result
            mid = len(images) // 2
            print(
                f"WARN: OOM con batch={len(images)}, dividiendo en {mid}+{len(images) - mid}..."
            )
            return self.embed_batch(images[:mid], batch_meta[:mid]) + self.embed_batch(images[mid:], batch_meta[mid:])

    def search(self, query: str, k: int = 5):

        with torch.no_grad():
            inputs = self.processor.process_queries([query]).to(self.model.device)
            query_emb = self.model(**inputs)[0].float().cpu().tolist()
        del inputs
        torch.cuda.empty_cache()

        results = self.qdrant.query_points(
            collection_name=QDRANT_COLLECTION,
            query=query_emb,
            limit=k,
            with_payload=True,
        )
        return results.points


    def print_shape(self, dir_path: str):
        pdfs = self.load_pdfs(dir_path)
        if not pdfs:
            return

        images = convert_from_path(str(pdfs[0]), dpi=70, last_page=1)
        images[0].show()
        emb = self.embed_batch(images)[0]

        arr = np.array(emb)
        print(f"Shape embedding: {arr.shape}")

    def embed(self, dir_path: str):
        pdfs = self.load_pdfs(dir_path)
        self.create_collection()

        logging_data = {"chunks": 0, "sources": []}
        for batch_imgs, batch_meta in tqdm(iter_pdf_batches(pdfs, batch_size=1)):
            print("\n\n---"*10, f"Embedding Chunk {logging_data['chunks']}", "---"*10, "\n\n")
            for meta in batch_meta:
                print(
                    f"Batch {meta["doc_id"]}, source = {meta["source"]}, page = {meta['page_num']}"
                )

            self.embed_batch(batch_imgs, batch_meta)

            logging_data["chunks"] += 1

        print(f"Total chunks {logging_data['chunks']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="RAG")

    parser.add_argument('-e', '--embed')
    parser.add_argument('-q', '--query')

    args = parser.parse_args()

    if not args.query and not args.embed:
        parser.print_help()
        sys.exit(1)

    embedder = ColPaliEmbedder()

    if args.embed:
        embedder.embed(args.embed)
    
    if args.query:
        points = embedder.search(args.query)

        for point in points:
            print(point.payload)

        

