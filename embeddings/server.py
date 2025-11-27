from fastapi import FastAPI, Query
from typing import Annotated
from pydantic import BaseModel, Field
from embeddings import load_vector_db

app = FastAPI()


def map_result(result):
    return {
        "text": result.page_content,
        "source": result.metadata.get("source"),
        "page": result.metadata.get("page"),
        "title": result.metadata.get("title"),
    }


class FilterParams(BaseModel):
    query: str


@app.get("/")
def read_root(filter_query: Annotated[FilterParams, Query()]):

    vectordb = load_vector_db()

    results = vectordb.similarity_search(
        filter_query.query,
        k=3,
    )

    return [map_result(result) for result in results]
