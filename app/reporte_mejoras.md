# INFORME DE AUDITORÍA TÉCNICA

## 1. Análisis de Causa Raíz

Se han revisado tres reportes de feedback relacionados con las respuestas proporcionadas por el asistente sobre información de modelos de aire acondicionado y procedimientos de instalación. 

- En el primer reporte, la respuesta fue bien recibida, proporcionando detalles técnicos precisos sobre el modelo de aire acondicionado "MAW10V1QWT".
- En el segundo reporte, la respuesta también fue positiva, ofreciendo instrucciones claras para quitar e instalar el panel frontal de un Daikin FTXN.
- Sin embargo, en el tercer reporte, la respuesta fue negativa. El técnico indicó que la información proporcionada sobre el modelo "Kematna 16201K1G1F" fue muy diferente a la de la placa del equipo.

La causa raíz del problema en el tercer reporte parece estar en la capacidad del sistema para leer y procesar correctamente la información de la placa del modelo "Kematna 16201K1G1F". Si la información proporcionada por el sistema no coincide con la de la placa, es probable que el problema esté en la etapa de captura de datos, es decir, en el componente OCR ('Tesstrain').

## 2. Tabla de Modificaciones Requeridas

| Componente | Variable/Parámetro | Valor Sugerido | Justificación Técnica |
| :--- | :--- | :--- | :--- |
| Tesstrain (OCR) | Mejora en el dataset de entrenamiento | Añadir más imágenes de placas de modelos de aire acondicionado, especialmente del modelo "Kematna" | La mejora en la precisión del OCR para leer placas de modelos de diferentes fabricantes, como "Kematna", podría reducir errores en la captura de información. |

## 3. Componentes en Estado Óptimo

- **RAG ('ColPali')**: No se encontraron evidencias de fallos en la búsqueda de PDFs o información relacionada con los modelos de aire acondicionado. Por lo tanto, se considera que está funcionando correctamente.
- **LLM ('Llama 4 Scout')**: Las respuestas generadas para los modelos de aire acondicionado y procedimientos de instalación parecen adecuadas y útiles, según los comentarios de los técnicos. Por lo tanto, se considera que está funcionando correctamente.

Se sugiere enfocar los esfuerzos en mejorar la precisión del componente OCR ('Tesstrain') para asegurar que la información capturada de las placas de los modelos sea precisa y coincida con la información real. Esto podría implicar expandir el dataset de entrenamiento para incluir una mayor variedad de modelos y marcas de aire acondicionado.