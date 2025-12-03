from langchain_ollama import ChatOllama
from langchain.messages import AIMessage


class LLMProcessor:
    def __init__(self):
        self.model = ChatOllama(
            model="qwen2.5:3b",
            temperature=0.2,
            validate_model_on_init=True,
            num_predict=256,
        )

    def enhance_query(self, query):
        messages = [
            (
                "system",
                """You are an expert at enhancing search queries for better retrieval of technical documents.
                   Given a user query, add relevant technical terms and synonyms to improve search results.
                   Return the enhanced query only.""",
            ),
            ("user", f"Original Query: {query}"),
        ]

        try:
            response = self.model.invoke(messages)

            if isinstance(response, AIMessage):
                if response.content:
                    return response.content
                else:
                    print("WARNING: Empty response for query enhancement")
                    return query
            else:
                print(
                    f"Unexpected response type for query enhancement: {type(response)}"
                )
                return query

        except Exception as e:
            print(f"Error enhancing query '{query}': {e}")
            return query

    def extract_models(self, doc):
        messages = [
            (
                "system",
                """Extract the equipment model number from this content.
                    Return ONLY the model number, nothing else.
                    If multiple models are listed, return them comma-separated.
                    If no model found, return UNKNOWN""",
            ),
            ("user", f"Content: {doc.page_content}"),
        ]

        try:
            response = self.model.invoke(messages)

            if isinstance(response, AIMessage):
                if response.content:
                    return response.content
                else:
                    print(f'WARNING: Empty response for {doc.metadata["source"]}')
                    print(f"Response object: {response}")
                    return "UNKNOWN"
            else:
                print(
                    f'Unexpected response type for document {doc.metadata["source"]}: {type(response)}'
                )
                return "UNKNOWN"

        except Exception as e:
            print(f"Error processing document {doc.metadata['source']}: {e}")
            return "UNKNOWN"
