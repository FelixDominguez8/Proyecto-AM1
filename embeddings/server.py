from fastapi import FastAPI, Query
from typing import Annotated
from pydantic import BaseModel
from embeddings import create_or_load_db, search_db
from llm import LLMProcessor
from ranker import create_reranker
import re

app = FastAPI()


class FilterParams(BaseModel):
    query: str


@app.get("/")
def read_root(filter_query: Annotated[FilterParams, Query()]):

    vectordb = create_or_load_db()
    reranker = create_reranker()
    processor = LLMProcessor()

    results = search_db(
        filter_query.query, vectordb, reranker, processor, k=5, rerank=False
    )

    return results
