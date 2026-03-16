from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
from typing import Annotated
from pydantic import BaseModel
from embeddings import create_or_load_db, search_db
from llm import LLMProcessor
from ranker import create_reranker
from colpali import ColPaliEmbedder, get_result_image_path

app = FastAPI()


class FilterParams(BaseModel):
    query: str
    model: str = 'colpali'


@app.get("/")
def read_root(filter_query: Annotated[FilterParams, Query()]):
    results = []
    # print(f"Query: {filter_query.query} | Model: {filter_query.model}")

    if filter_query.model == 'colpali':
        colpali_model = ColPaliEmbedder()

        results = colpali_model.search(filter_query.query)

    elif filter_query.model == 'text':
        vectordb = create_or_load_db()
        reranker = create_reranker()
        processor = LLMProcessor()
        results = search_db(
            filter_query.query, vectordb, reranker, processor, k=5, rerank=False, optimize=False
        )
    else:
        raise HTTPException(status_code=400, detail='Modelo desconocido, modelos disponibles: colpali, text')

    
    return results


@app.get("/image/{doc_id}")
def get_image(doc_id: str):
    try:
        path = get_result_image_path(doc_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return FileResponse(path, media_type="image/jpeg")