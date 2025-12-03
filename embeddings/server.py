from fastapi import FastAPI, Query
from typing import Annotated
from pydantic import BaseModel
from embeddings import create_or_load_db
from llm import LLMProcessor

app = FastAPI()


def map_result(result):
    return {
        "text": result.page_content,
        "source": result.metadata.get("source"),
        "page": result.metadata.get("page"),
        "title": result.metadata.get("title"),
        "models": result.metadata.get("models"),
    }


class FilterParams(BaseModel):
    query: str


@app.get("/")
def read_root(filter_query: Annotated[FilterParams, Query()]):

    vectordb = create_or_load_db()

    enhanced_query = LLMProcessor().enhance_query(filter_query.query)

    print(f"Enhanced Query: {enhanced_query}")

    initial_results = vectordb.similarity_search(
        enhanced_query,
        k=5,
    )

    return [map_result(result) for result in initial_results]
