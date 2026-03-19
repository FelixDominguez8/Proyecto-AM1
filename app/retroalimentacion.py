import os
import glob
import json
import requests
from dotenv import load_dotenv

# 1. Carga de configuración (.env.local está una carpeta arriba de /app)
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env.local')
load_dotenv(dotenv_path)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def leer_feedbacks():
    # Buscamos archivos .txt en tecnico_bot/feedback/
    path_feedback = os.path.join(os.path.dirname(__file__), '..', 'feedback', '*.txt')
    archivos = glob.glob(path_feedback)
    
    reportes_acumulados = ""
    for archivo in archivos:
        with open(archivo, 'r', encoding='utf-8') as f:
            reportes_acumulados += f.read() + "\n\n" + ("="*30) + "\n\n"
            
    return reportes_acumulados, len(archivos)

def analizar_con_llama4(texto_reportes):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt_sistema = """Eres un Ingeniero de Sistemas Senior. Tu ética profesional te impide sugerir cambios en componentes que están funcionando correctamente. 

    ARQUITECTURA:
    - OCR: 'Tesstrain' (Captura de placas).
    - RAG: 'ColPali' (Búsqueda en PDFs).
    - LLM: 'Llama 4 Scout' (Razonamiento y respuesta).

    TU MISIÓN:
    Realiza una auditoría de inferencia basada exclusivamente en la evidencia de los reportes (.txt). 

    REGLAS CRÍTICAS DE ESPECIFICIDAD:
    1. NO sugieras cambios por sistema. Si la evidencia no apunta a un fallo en un componente, márcalo como [ESTADO: ÓPTIMO] y no propongas modificaciones para él.
    2. Identifica la CAUSA RAÍZ. Si Tesstrain leyó mal, el problema nace ahí; no culpes al RAG de no encontrar un manual de un modelo que fue mal leído.
    3. Los cambios deben ser parámetros técnicos reales (ej. "Temperature -> 0.2", "Top_P -> 0.8", "Añadir X imágenes al dataset", "Aumentar k-neighbors a X").

    FORMATO DE REPORTE:
    # INFORME DE AUDITORÍA TÉCNICA

    ## 1. Análisis de Causa Raíz
    (Explica aquí detalladamente qué falló en los reportes negativos y por qué deduces que es ese componente específico).

    ## 2. Tabla de Modificaciones Requeridas
    | Componente | Variable/Parámetro | Valor Sugerido | Justificación Técnica |
    | :--- | :--- | :--- | :--- |
    | (Solo los que fallaron) | (Nombre del parámetro) | (Valor exacto) | (Por qué este cambio arregla el fallo detectado) |

    ## 3. Componentes en Estado Óptimo
    (Lista aquí los componentes que NO necesitan cambios según la evidencia actual)."""

    data = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": f"Realiza una auditoría de inferencia sobre estos reportes técnicos:\n\n{texto_reportes}"}
        ],
        "temperature": 0.2, # Permitimos flexibilidad para la inferencia técnica
        "max_tokens": 3000
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Error en la petición a Groq: {e}"

if __name__ == "__main__":
    print("📂 Accediendo a carpeta de feedback...")
    datos, cantidad = leer_feedbacks()
    
    if cantidad == 0:
        print("⚠️ No hay archivos nuevos para analizar.")
    else:
        print(f"🤖 Analizando {cantidad} reportes con Llama 4 Scout...")
        analisis = analizar_con_llama4(datos)
        
        # Guardamos el resultado en un archivo Markdown
        reporte_final = os.path.join(os.path.dirname(__file__), 'reporte_mejoras.md')
        with open(reporte_final, "w", encoding="utf-8") as f:
            f.write(analisis)
            
        print(f"\n✅ Análisis completado con éxito.")
        print(f"📝 Reporte generado en: {reporte_final}")