from langchain_ollama import ChatOllama
from langchain.messages import AIMessage
import re


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
                """Eres un optimizador de consultas para un sistema de búsqueda de manuales técnicos HVAC/refrigeración.

                Tu tarea: reformular la consulta del usuario para maximizar la recuperación de información relevante.

                Reglas:
                - Expande abreviaciones técnicas (AC→aire acondicionado, BTU, CFM, etc.)
                - Añade sinónimos técnicos relevantes
                - Incluye términos en inglés Y español si aplica
                - Mantén la intención original
                - NO respondas la pregunta, solo reformúlala
                - Si detectas un número de modelo, extráelo y añádelo al FINAL en formato [MODEL:modelo_detectado]
                - Responde ÚNICAMENTE con la consulta optimizada, sin explicaciones""",
            ),
            ("user", f"Original Query: {query}"),
        ]

        try:
            response = self.model.invoke(messages)

            if isinstance(response, AIMessage):
                if response.content:
                    enhanced_text = response.content
                    return self.parse_enhanced_query(enhanced_text, query)
                else:
                    print("WARNING: Empty response for query enhancement")
                    return {"query": query, "model": None}
            else:
                print(
                    f"Unexpected response type for query enhancement: {type(response)}"
                )
                return {"query": query, "model": None}

        except Exception as e:
            print(f"Error enhancing query '{query}': {e}")
            return {"query": query, "model": None}

    def parse_enhanced_query(self, enhanced_text, _):
        model_pattern = r"\[MODEL:([^\]]+)\]"
        match = re.search(model_pattern, enhanced_text)

        if match:
            model = match.group(1).strip()
            clean_query = re.sub(model_pattern, "", enhanced_text).strip()
            return {"query": clean_query, "model": model}
        else:
            return {"query": enhanced_text, "model": None}

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
                    return "UNKNOWN"
            else:
                print(
                    f'Unexpected response type for document {doc.metadata["source"]}: {type(response)}'
                )
                return "UNKNOWN"

        except Exception as e:
            print(f"Error processing document {doc.metadata['source']}: {e}")
            return "UNKNOWN"
