from fastapi import FastAPI, Query
from typing import Annotated
from pydantic import BaseModel
from embeddings import create_or_load_db
from llm import LLMProcessor
import re

app = FastAPI()


def _model_matches(models, pattern):
    if not models:
        return False
    if isinstance(models, list):
        return any(pattern.search(str(model)) for model in models)
    return pattern.search(str(models))


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

    enhanced_result = LLMProcessor().enhance_query(filter_query.query)
    enhanced_query = enhanced_result["query"]
    detected_model = enhanced_result["model"]

    print(f"Enhanced Query: {enhanced_query}")
    print(f"Detected Model: {detected_model}")

    if detected_model:
        initial_results = vectordb.similarity_search(enhanced_query, k=50)

        # Filter results by detected model (case insensitive, matches anywhere in string or array)
        pattern = re.compile(re.escape(detected_model), re.IGNORECASE)
        filtered = [
            doc
            for doc in initial_results
            if _model_matches(doc.metadata.get("models"), pattern)
        ]

        initial_results = filtered if filtered else initial_results[:5]

    else:
        initial_results = vectordb.similarity_search(
            enhanced_query,
            k=5,
        )

    return [map_result(result) for result in initial_results]
