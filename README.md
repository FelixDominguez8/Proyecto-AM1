# Proyecto-AM1
Este proyecto es un chatbot para técnicos. El punto del sistema es poder poner manuales técnicos de diferentes electrodomésticos y en general cualquier cosa que tenga manuales técnicos, en el caso del proyecto especializado en aires acondicionados, y que se puedan crear embeddings que se guarden en una base de datos que luego sea tomada por el frontend a base de lo que el usuario está buscando por medio de un sistema de RAG. Este proyecto se hizo junto a mi compañero de clase, Samuel Rocha, para ambos Aprendizaje de Maquina 1 y 2, con cada uno siendo una aplicación distinta del mismo sistema y con algunas cosas extras.

### División del Trabajo:
- Felix Dominguez: Frontend, LLM Generador, Retroalimentación, OCR
- Samuel Rocha: Sistema de RAG ambas original y versión visual

### Diferencias entre versiones
V1: La primera versión hecha para la clase de Aprendizaje de Maquina 1, era la versión base del proyecto. Esta se basada en un sistema más directo de la implementación de este, en el backend se usó un modelo sencillo para hacer los embeddings a base de los manuales que estaba en el sistema, este los convertía a embeddings que eran guardados en una base de datos vectorial, después estos esperaban a que el usuario mandara un mensaje, a base de este mensaje que llamaba al sistema de RAG el cual miraba cuales son los embeddings que más aplicaban al query mandado y enviaba los 5 más relacionados de vuelta, en el frontend se utilizaba Llama 4 Scout por medio de Groq, para que este tomara el contexto, mirara el formato de respuesta y brindara una respuesta basándose en la información del RAG.

V2: La versión 2 fue una expansión del concepto inicial. El principal cambio fue la diferencia entre el modelo de embeddings, a comparación del original este debía tener una base de visión por computadora y por ende decidimos utilizar ColPali para este y generar embeddings visuales de los manuales y hacer que el sistema del RAG funcione a base de ello. Además de ello se agregaron otras funcionalidades, como una sección para subir etiquetas técnicas de los dispositivos y detectar el texto para entender con mayor exactitud el dispositivo y el problema a base de un OCR con Tesseract, también se agregó un ligera versión de feedback, en donde el usuario podía darle un me gusta o un no me gusta y brindar un mensaje del porque al feedback dado y luego un modelo tomaría el mensaje generado por el llm, el feedback y el mensaje y base de eso generar un reporte de que podría ser lo que paso y que se podría hacer para mejorar las respuestas

### Imágenes
<img width="1333" height="632" alt="Proyecto Final" src="https://github.com/user-attachments/assets/8eecc729-95fc-465c-9647-037b1b1ef729" />
<img width="1475" height="697" alt="Proyecto Final AM2" src="https://github.com/user-attachments/assets/f81c09f3-68e3-4b5f-ba3e-a2de03dd7c4e" />

### Detalles Importantes
El proyecto en su versión actual no funciona como tal, debido a que el sistema se basaba en Llama 4 Scout en Groq, el cual hace unos meses fue deprecado por Groq hasta recientemente, para hacerlo funcionar se puede intentar con lo que probablemente es el modelo más similar a ese en Groq, que es: qwen/qwen3.8-27b, y cambiarlo en app/api/chat/route.ts, pero eso no ha sido probado y todo el sistema fue hecho desde el inicio para que funcionara con Scout en la versión gratis de Groq, para versiones empresariales, este no fue eliminado de manera directa

## Para correr el sistema
Si incluso después del mensaje anterior se intenta correr el sistema, para correr el sistema se necesitan correr los siguientes comandos:
- En la carpeta inicial:

```npm run dev```

- En ./Embeddings

```python -m fastapi dev server.py```

También para la primera versión que es mucho más sencilla cuyo último commit antes de la segunda versión se llama como Ya no más (9ce12ac18786daf528fc4f8ea2bf1d43343d15d8) en la rama Main, se puede correr el archivo embeddings.py con solo:

```python Embeddings.py```

Pero en la segunda versión no es tan fácil, debido a lo pesado que es ColPali mi compañero incluso con una tarjeta gráfica dedicada no pudo generar los emebddings y por ende utilizo una instancia de qdrant, para si quiera generarlos, por ende, no es tan sencillo generar los embeddings de la versión más reciente.
