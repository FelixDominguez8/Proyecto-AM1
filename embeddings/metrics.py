from typing import List, Dict, Set
from collections import defaultdict
from embeddings import create_or_load_db, search_db
from ranker import create_reranker
from llm import LLMProcessor
import numpy as np


class RetrievalMetrics:
    def __init__(self):
        self.results = defaultdict(list)

    def mrr(self, retrieved, relevant):
        for idx, doc in enumerate(retrieved, start=1):
            if (
                doc.metadata.get("source", "") == relevant["source"]
                and doc.metadata.get("page", "") == relevant["page"]
            ):
                return 1.0 / idx

        return 0.0

    def evaluate_query(
        self, query: str, retrieved: List[str], relevant: Set[str], k: int = 5
    ) -> Dict[str, float]:
        metrics = {
            "mrr": self.mrr(retrieved, relevant),
        }

        self.results[query] = metrics
        return metrics

    def aggregate_metrics(self) -> Dict[str, float]:
        if not self.results:
            return {}

        all_metrics = defaultdict(list)

        for query_metrics in self.results.values():
            for metric_name, value in query_metrics.items():
                all_metrics[metric_name].append(value)

        return {
            metric_name: np.mean(values) for metric_name, values in all_metrics.items()
        }

    def print_report(self):
        if not self.results:
            print("No hay resultados para evaluar")
            return

        print("\n" + "=" * 60)
        print("REPORTE DE EVALUACI�N DEL RAG")
        print("=" * 60)

        for query, metrics in self.results.items():
            print(f"\nQuery: {query}")
            print("-" * 60)
            for metric_name, value in metrics.items():
                print(f"  {metric_name:.<20} {value:.3f}")

        print("\n" + "=" * 60)
        print("PROMEDIOS GENERALES")
        print("=" * 60)

        avg_metrics = self.aggregate_metrics()
        for metric_name, value in avg_metrics.items():
            print(f"  {metric_name:.<20} {value:.3f}")

        print()


def create_evaluation_dataset():
    evaluation_data = [
        {
            "source": "./manuals/01.pdf",
            "page": 18,
            "query": "¿Cuál es el rango de temperatura ambiente para que el modo de calefacción funcione correctamente en modelos T1?",
            "example_answer": "Para el modo de calefacción en modelos T1, la temperatura exterior debe estar entre -7°C y 24°C, y la temperatura de la habitación debe ser superior a 27°C.",
        },
        {
            "source": "./manuals/01.pdf",
            "page": 14,
            "query": "¿Cuánto tiempo dura el ciclo de descongelamiento durante la operación de calefacción?",
            "example_answer": "El ciclo de descongelamiento (defrost) usualmente dura entre 2 y 10 minutos. Durante este proceso, el ventilador de la unidad interior deja de funcionar y después del descongelamiento, el equipo vuelve automáticamente al modo de calefacción.",
        },
        {
            "source": "./manuals/01.pdf",
            "page": 25,
            "query": "¿Cuál es la distancia máxima permitida entre la unidad interior y exterior del aire acondicionado?",
            "example_answer": "La distancia máxima entre la unidad interior y exterior es de 15 metros, con una diferencia de nivel máxima de 5 metros.",
        },
        {
            "source": "./manuals/01.pdf",
            "page": 8,
            "query": "¿Cómo se desactiva la función AUTO-RESTART del aire acondicionado?",
            "example_answer": "Para desactivar la función AUTO-RESTART: 1) Apagar el aire acondicionado y desenchufarlo, 2) Presionar el botón de emergencia mientras se enchufa, 3) Mantener presionado el botón por más de 10 segundos hasta escuchar 4 beeps cortos. Para reactivarla, seguir el mismo procedimiento hasta escuchar 3 beeps cortos.",
        },
        {
            "source": "./manuals/01.pdf",
            "page": 28,
            "query": "¿Cada cuánto tiempo se deben reemplazar los filtros electrostáticos y desodorantes?",
            "example_answer": "Los filtros electrostáticos y desodorantes deben reemplazarse cada 6 meses, ya que no pueden lavarse ni regenerarse.",
        },
        {
            "source": "./manuals/02.pdf",
            "page": 7,
            "query": "¿Cuáles son las dimensiones del modelo FCAC-36?",
            "example_answer": "Las dimensiones del FCAC-36 son 1250mm de ancho (A), 675mm de profundidad (B) y 235mm de alto (C).",
        },
        {
            "source": "./manuals/02.pdf",
            "page": 9,
            "query": "¿Cuál es el nivel de ruido del FCAC-24 en velocidad baja?",
            "example_answer": "El nivel de ruido del FCAC-24 en velocidad baja es de 45 dB(A).",
        },
        {
            "source": "./manuals/02.pdf",
            "page": 16,
            "query": "¿Qué significa el código de error E3 en la unidad?",
            "example_answer": "El código E3 indica una falla en el sensor de temperatura del tubo del evaporador (T2).",
        },
        {
            "source": "./manuals/02.pdf",
            "page": 15,
            "query": "¿Cuál es el torque de apriete recomendado para tubería de Φ9.5mm?",
            "example_answer": "El torque de apriete para tubería de Φ9.5mm es de 25~26 N.m (255~265 kgf.cm).",
        },
        {
            "source": "./manuals/02.pdf",
            "page": 21,
            "query": "¿Cuál debe ser la pendiente mínima del tubo de drenaje?",
            "example_answer": "El tubo de drenaje debe tener una pendiente mínima de 1/100 hacia abajo.",
        },
        {
            "source": "./manuals/03.pdf",
            "page": 5,
            "query": "¿Cuál es la distancia mínima que debe haber entre la unidad interior FTXN09KEVJU o FTXN12KEVJU y el techo?",
            "example_answer": "La unidad interior debe instalarse a una distancia mínima de 1-3/16 pulgadas (30mm) del techo y 1-15/16 pulgadas (50mm) de las paredes en ambos lados.",
        },
        {
            "source": "./manuals/03.pdf",
            "page": 11,
            "query": "¿Cuál es el torque de apriete correcto para las tuercas flare en las tuberías de refrigerante del Daikin FTXN12KEVJU?",
            "example_answer": "Para el lado de gas (3/8 pulgadas / 9.5mm) el torque es de 24.1-29.4 ft·lbf (32.7-39.9 N·m). Para el lado líquido (1/4 pulgadas / 6.4mm) el torque es de 10.4-12.7 ft·lbf (14.2-17.2 N·m).",
        },
        {
            "source": "./manuals/03.pdf",
            "page": 6,
            "query": "¿Qué diámetro debe tener el agujero en la pared para instalar el Daikin FTXN09KEVJU?",
            "example_answer": "El agujero en la pared debe tener un diámetro de 2-9/16 pulgadas (65mm) y debe tener una inclinación hacia abajo en dirección al exterior.",
        },
        {
            "source": "./manuals/03.pdf",
            "page": 8,
            "query": "¿Qué tipo de cable se debe usar para el cableado entre la unidad interior y exterior del Daikin serie FTXN?",
            "example_answer": "Se debe usar cable AWG16 o AWG14 para el cableado inter-unidad. Cuando la longitud del cable excede 33 pies (10m), se debe usar AWG14.",
        },
        {
            "source": "./manuals/03.pdf",
            "page": 2,
            "query": "¿Cuál es el alcance máximo del control remoto inalámbrico del Daikin FTXN09KEVJU y FTXN12KEVJU?",
            "example_answer": "El control remoto inalámbrico tiene un alcance máximo de 23 pies (7 metros). Se debe verificar que las señales sean recibidas correctamente por la unidad interior encendiendo todas las lámparas fluorescentes de la habitación.",
        },
    ]

    return evaluation_data


def run_evaluation_example(vectordb):
    metrics = RetrievalMetrics()
    eval_dataset = create_evaluation_dataset()
    reranker = create_reranker()
    processor = LLMProcessor()

    for test_case in eval_dataset[:5]:
        query = test_case["query"]

        results = search_db(
            query, vectordb, reranker, processor, k=5, optimize_query=True
        )

        metrics.evaluate_query(query, results, test_case, k=5)

    metrics.print_report()

    return metrics


if __name__ == "__main__":
    vectordb = create_or_load_db()

    run_evaluation_example(vectordb)
