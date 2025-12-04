from fastapi import FastAPI, Query
from typing import Annotated
from pydantic import BaseModel
from embeddings import create_or_load_db, search_db
from llm import LLMProcessor
from ranker import create_reranker
import re

app = FastAPI()


class _Config:
    def __init__(self):
        self.vectordb = create_or_load_db()
        self.processor = LLMProcessor()
        self.reranker = create_reranker()


config = _Config()


class FilterParams(BaseModel):
    query: str


@app.get("/")
def read_root(filter_query: Annotated[FilterParams, Query()]):

    # vectordb = create_or_load_db()
    reranker = None
    # processor = LLMProcessor()

    results = search_db(
        filter_query.query,
        config.vectordb,
        config.reranker,
        config.processor,
        k=5,
        rerank=True,
        optimize=True,
    )

    return results
