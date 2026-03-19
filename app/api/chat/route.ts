import { NextRequest } from "next/server";
const { translate } = require('@vitalets/google-translate-api');
import { execSync } from 'child_process';
import { writeFile} from 'fs/promises';
import fs from 'fs/promises';
import path from 'path';

export const runtime = "nodejs";

const globalCfg = global as any;

if (!globalCfg.currentConfig) {
  globalCfg.currentConfig = {
    rag_mode: "only-rag",
    tone_mode: "casual",
  };
}

const currentConfig = globalCfg.currentConfig;

const RAG_INSTRUCTIONS = {
  "only-rag": "REGLA ESTRICTA: Responde basándote ÚNICAMENTE en la documentación técnica proporcionada completa, si hay 10 pasos proporciona esos 10 pasos. Si la información no está en los manuales, indica honestamente que no cuentas con ese dato. No uses conocimientos externos.",
  "rag-extra": "Utiliza la documentación técnica como fuente principal, pero tienes permitido ampliar la respuesta con consejos prácticos de mantenimiento y buenas prácticas generales de refrigeración para ayudar al técnico.",
  "rag-ref": "Utiliza tus conocimientos generales de ingeniería como base. Consulta los manuales proporcionados solo como referencia para datos específicos como voltajes, códigos de error o capacidades nominales."
};

const TONE_INSTRUCTIONS = {
  "casual": "Adopta un tono cercano, directo y sencillo, como si fueras un colega técnico con años de experiencia ayudando a otro en el campo. Evita formalismos innecesarios.",
  "normal": "Mantén un tono profesional, equilibrado y servicial. Es el estándar de asistencia técnica.",
  "formal": "Adopta un tono estrictamente profesional y técnico. Utiliza terminología precisa, estructuras gramaticales impecables y un lenguaje de alto nivel."
};


function detectLanguageSimple(text: string): string {
  const spanishPatterns = [
    /\b(qué|cómo|dónde|cuándo|por qué|cuál|quién)\b/i,
    /\b(el|la|los|las|un|una|unos|unas)\b/i,
    /\b(es|está|son|están|soy|estoy)\b/i,
    /\b(tengo|tiene|tienen|hacer|ayuda|problema)\b/i,
    /[áéíóúñ]/i
  ];

  const englishPatterns = [
    /\b(what|how|where|when|why|which|who)\b/i,
    /\b(the|a|an|is|are|am)\b/i,
    /\b(have|has|do|does|help|problem|issue)\b/i,
    /\b(my|your|his|her|their|our)\b/i
  ];

  const lowerText = text.toLowerCase();

  let spanishScore = 0;
  let englishScore = 0;

  spanishPatterns.forEach(pattern => {
    const matches = lowerText.match(pattern);
    if (matches) spanishScore += matches.length;
  });

  englishPatterns.forEach(pattern => {
    const matches = lowerText.match(pattern);
    if (matches) englishScore += matches.length;
  });

  return englishScore > spanishScore ? 'en' : 'es';
}

function getSystemPromptText(lang: string, retrievedDocs: string, ragText: string, toneText: string): string {
  if (lang === 'en') {
    return `You are a Technical Repair Expert for HVAC and refrigeration. Use the provided RAG context to answer.

--- LANGUAGE & PRIVACY (CRITICAL) ---
- Language: ALWAYS English.
- No Internal Reasoning: Do NOT output thoughts, classifications (Type A/B), or "The user wants...".
- No RAG Mentions: NEVER mention "RAG", "retrieval", "database", or "documents". Sound like innate knowledge.
- Sources: ONLY allowed in the **References** section.

--- CLASSIFICATION & FORMATS ---
Detect the intent and use EXACTLY one format:

1. Type A (Informational): Simple facts.
   ## **ℹ️ Information**
   [Extracted answer from RAG]
   ## **📚 References**
   - **[Document]** | Page [X] | Source: [name]

2. Type B (Technical/Repair): Installation or troubleshooting.
   ## **📋 Diagnosis**
   [Problem explanation via RAG in 1-4 sentences]
   ---
   ## **🔧 Solution**
   **1.** [Step description]
   ... (Repeat for ALL steps in RAG. Do NOT omit or modify sequence).
   [If applicable: ⚠️ **Warning:** risk description]
   ---
   ## **📚 References**
   - **[Document]** | Page [X] | Source: [name]

--- CONTENT RULES ---
- ${ragText}
- ${toneText}
- Formatting: Sections divided by ---. Titles ## and **bold**. Numbers **bold**.

--- CONTEXT & DEVICE INFO ---
Context: ${retrievedDocs}

Note: Use "Device Information" (OCR) to identify models. If the OCR is messy, prioritize matching strings that align with the technical documents.`;
  }

  // default
  return `Eres un Experto en Reparación Técnica de HVAC y refrigeración. Usa el contexto RAG proporcionado para responder.

--- IDIOMA Y PRIVACIDAD (CRÍTICO) ---
- Idioma: SIEMPRE Español.
- Sin Razonamiento Interno: NO generes pensamientos, clasificaciones (Tipo A/B) o frases como "El usuario quiere...".
- Sin Menciones al RAG: NUNCA menciones "RAG", "recuperación", "base de datos" o "documentos". Debe sonar como conocimiento propio.
- Fuentes: SOLO permitidas en la sección de **Referencias** al final.

--- CLASIFICACIÓN Y FORMATOS ---
Detecta la intención y usa EXACTAMENTE un formato:

1. Tipo A (Informativo): Datos simples.
   ## **ℹ️ Información**
   [Respuesta extraída del RAG]
   ## **📚 Referencias**
   - **[Nombre del documento]** | Página [X] | Fuente: [nombre]

2. Tipo B (Técnico/Reparación): Instalación o resolución de problemas.
   ## **📋 Diagnóstico**
   [Explicación del problema vía RAG en 1-4 oraciones]
   ---
   ## **🔧 Solución**
   **1.** [Descripción del paso]
   ... (Repite para TODOS los pasos en el RAG. NO omitas ni modifiques la secuencia).
   [Si aplica: ⚠️ **Advertencia:** descripción del riesgo]
   ---
   ## **📚 Referencias**
   - **[Nombre del documento]** | Página [X] | Fuente: [nombre]

--- REGLAS DE CONTENIDO ---
- ${ragText}
- ${toneText}
- Formato: Secciones divididas por ---. Títulos con ## y en **negrita**. Números en **negrita**.

--- CONTEXTO E INFO DEL DISPOSITIVO ---
Contexto: ${retrievedDocs}

Nota: Usa la "Información del dispositivo" (OCR) para identificar modelos. Si el texto es confuso, prioriza coincidencias que se alineen con los documentos técnicos.`;
}

function getSystemPromptColpali(lang: string, ragText: string, toneText: string): string {
  if (lang === 'en') {
    return `You are a Technical Repair Expert for HVAC and refrigeration. You will receive one or more images of document pages as your context — analyze them visually to extract the relevant technical information and answer the question.

--- LANGUAGE & PRIVACY (CRITICAL) ---
- Language: ALWAYS English.
- No Internal Reasoning: Do NOT output thoughts, classifications (Type A/B), or "The user wants...".
- No RAG Mentions: NEVER mention "images", "pages", "retrieval", "database", or "documents". Sound like innate knowledge.
- Sources: ONLY allowed in the **References** section.

--- CLASSIFICATION & FORMATS ---
Detect the intent and use EXACTLY one format:

1. Type A (Informational): Simple facts.
   ## **ℹ️ Information**
   [Extracted answer from the document images]
   ## **📚 References**
   - **[Document]** | Page [X] | Source: [name]

2. Type B (Technical/Repair): Installation or troubleshooting.
   ## **📋 Diagnosis**
   [Problem explanation extracted from the images in 1-4 sentences]
   ---
   ## **🔧 Solution**
   **1.** [Step description]
   ... (Repeat for ALL steps visible in the images. Do NOT omit or modify sequence).
   [If applicable: ⚠️ **Warning:** risk description]
   ---
   ## **📚 References**
   - **[Document]** | Page [X] | Source: [name]

--- CONTENT RULES ---
- Image Priority: Extract steps, diagrams, tables, and warnings directly from the provided images.
- Read all text visible in the images carefully, including small print, labels, and captions.
- ${ragText}
- ${toneText}
- Formatting: Sections divided by ---. Titles ## and **bold**. Numbers **bold**.`;
  }

  // default
  return `Eres un Experto en Reparación Técnica de HVAC y refrigeración. Recibirás una o más imágenes de páginas de documentos como contexto — analízalas visualmente para extraer la información técnica relevante y responder la pregunta.

--- IDIOMA Y PRIVACIDAD (CRÍTICO) ---
- Idioma: SIEMPRE Español.
- Sin Razonamiento Interno: NO generes pensamientos, clasificaciones (Tipo A/B) o frases como "El usuario quiere...".
- Sin Menciones al Contexto: NUNCA menciones "imágenes", "páginas", "recuperación", "base de datos" o "documentos". Debe sonar como conocimiento propio.
- Fuentes: SOLO permitidas en la sección de **Referencias** al final.

--- CLASIFICACIÓN Y FORMATOS ---
Detecta la intención y usa EXACTAMENTE un formato:

1. Tipo A (Informativo): Datos simples.
   ## **ℹ️ Información**
   [Respuesta extraída de las imágenes del documento]
   ## **📚 Referencias**
   - **[Nombre del documento]** | Página [X] | Fuente: [nombre]

2. Tipo B (Técnico/Reparación): Instalación o resolución de problemas.
   ## **📋 Diagnóstico**
   [Explicación del problema extraída de las imágenes en 1-4 oraciones]
   ---
   ## **🔧 Solución**
   **1.** [Descripción del paso]
   ... (Repite para TODOS los pasos visibles en las imágenes. NO omitas ni modifiques la secuencia).
   [Si aplica: ⚠️ **Advertencia:** descripción del riesgo]
   ---
   ## **📚 Referencias**
   - **[Nombre del documento]** | Página [X] | Fuente: [nombre]

--- REGLAS DE CONTENIDO ---
- Prioridad Visual: Extrae pasos, diagramas, tablas y advertencias directamente de las imágenes proporcionadas.
- Lee con atención todo el texto visible en las imágenes, incluyendo letra pequeña, etiquetas y pies de página.
- ${ragText}
- ${toneText}
- Formato: Secciones divididas por ---. Títulos con ## y en **negrita**. Números en **negrita**.`;
}

function getSystemPrompt(
  lang: string,
  retrievedDocs: string = '',
  model: Model = 'colpali',
  ragText: string = '',
  toneText: string = ''
): string {
  if (model === 'colpali') {
    return getSystemPromptColpali(lang, ragText, toneText);
  } else if (model === 'text') {
    return getSystemPromptText(lang, retrievedDocs, ragText, toneText);
  }

  return '';
}

async function translateForRAG(text: string, fromLang: string): Promise<string> {
  if (fromLang === 'en') return text;

  try {
    const result = await translate(text, { from: fromLang, to: 'en' });
    return result.text;
  } catch (error) {
    console.error('Error en traduccion, usando texto original:', error);
    return text;
  }
}

interface RAGDocument {
  doc_id: string;
  text: string;
  source: string;
  page: number;
  title?: string;
}

type Model = 'colpali' | 'text'

async function processColpaliResults(results: RAGDocument[], limit: number = 0) {
  const slice = (limit >= 1 && limit < results.length) ? results.slice(0, limit) : results;

  const imageContents = await Promise.all(
    slice.map(async (result) => {
      const res = await fetch(`http://localhost:8000/image/${result.doc_id}`);
      if (!res.ok) return null;
      const arrayBuffer = await res.arrayBuffer();
      const base64 = Buffer.from(arrayBuffer).toString('base64');
      return { type: "image_url", image_url: { url: `data:image/jpeg;base64,${base64}` } };
    })
  );

  return imageContents.filter((img) => img !== null);
}

async function processTextResults(results: RAGDocument[]) {
  let retrievedDocs = ''

  if (results.length > 0) {
    retrievedDocs = results
      .map((doc, index) => {
        return `
--- ${doc.title || "Sin título"} ---
[Título]: ${doc.title || "Sin título"}
[Página]: ${doc.page}
[Source]: ${doc.source}
[Texto]:
${doc.text}
            `.trim();
      })
      .join("\n\n");
    console.log(`✅ ${results.length} documentos recuperados`);
  } else {
    retrievedDocs = "No se encontraron documentos relevantes en la base de conocimiento.";
    console.log('No se encontraron documentos');
  }

  return retrievedDocs

}

export async function POST(req: NextRequest) {
  try {
    const contentType = req.headers.get("content-type") || "";

    if (contentType.includes("application/json")) {
      // Leemos el body UNA SOLA VEZ
      const body = await req.json();

      // Caso A: Es una actualización de configuración
      if (body.rag_mode || body.tone_mode) {
        currentConfig.rag_mode = body.rag_mode || currentConfig.rag_mode;
        currentConfig.tone_mode = body.tone_mode || currentConfig.tone_mode;
        console.log("⚙️ Configuración sincronizada:", currentConfig);
        return new Response(JSON.stringify({ configurado: true }), { status: 200 });
      }

      // Caso B: Es Feedback (usamos los datos que ya están en 'body')
      if (body.tipo) { 
        const { pregunta, respuesta, tipo, comentario } = body; // <--- Ya no usamos await req.json()
        
        const feedbackDir = path.join(process.cwd(), 'feedback');
        await fs.mkdir(feedbackDir, { recursive: true });
        
        const fileName = `feedback_${Date.now()}.txt`;
        const contenido = `
    === REPORTE DE FEEDBACK ===
    FECHA: ${new Date().toLocaleString()}
    SENTIMIENTO: ${tipo.toUpperCase()}

    [PREGUNTA DEL TÉCNICO]
    ${pregunta}

    [RESPUESTA DEL ASISTENTE]
    ${respuesta}

    [COMENTARIO DEL TÉCNICO]
    ${comentario || "Sin comentarios adicionales."}
    ==========================
        `.trim();

        await fs.writeFile(path.join(feedbackDir, fileName), contenido, 'utf8');
        console.log("📂 Feedback guardado en carpeta /feedback");
        return new Response(JSON.stringify({ enviado: true }), { status: 200 });
      }
    }

    const formData = await req.formData();
    const file = formData.get('file') as File | null;
    const pregunta_usuario = formData.get('pregunta_usuario') as string;
    const messagesRaw = formData.get('messages') as string;
    const messages = messagesRaw ? JSON.parse(messagesRaw) : [];

    let datos_placa = "";

    // Procesamiento del OCR local si existe un archivo
    if (file) {
      const bytes = await file.arrayBuffer();
      const buffer = Buffer.from(bytes);

      // Guardamos la imagen temporalmente para que el script de Python la lea
      const tempPath = path.join(process.cwd(), 'temp_ocr.jpg');
      await writeFile(tempPath, buffer);

      try {
        // Ejecutamos tesseract.py y capturamos la salida del print()
        datos_placa = execSync(`python ./app/api/chat/tesseract.py "${tempPath}"`).toString().trim();
        console.log("✅ OCR local exitoso");
      } catch (ocrError) {
        console.error("❌ Error ejecutando tesseract.py:", ocrError);
        datos_placa = "Error al leer la placa.";
      }
    }

    // Validación: verificamos que al menos venga la pregunta o el historial
    if (!pregunta_usuario && (!messages || messages.length === 0)) {
      return new Response(
        JSON.stringify({ error: "Faltan datos en la petición" }),
        { status: 400 }
      );
    }

    // Usamos 'pregunta_usuario' como la consulta principal
    const userMessage = pregunta_usuario;

    // 2) Detección de idioma y traducción para el RAG
    const detectedLang = detectLanguageSimple(userMessage);
    console.log('🌍 Idioma detectado:', detectedLang);

    let ragQuery = userMessage;
    if (detectedLang === 'es') {
      console.log('🔄 Traduciendo query para RAG...');
      ragQuery = await translateForRAG(userMessage, detectedLang);
      console.log('📝 Query traducido:', ragQuery);
    }

    // 3) Consulta al RAG (usando la consulta traducida)
    let model: Model = 'colpali'
    const url = `http://127.0.0.1:8000/?query=${encodeURIComponent(ragQuery)}&model=${model}`;
    
    // Configuración de paciencia: 60 segundos antes de rendirse
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 60000); 

    let retrievedDocs = "";
    let images: any = null;

    try {
      // Agregamos el signal para que el fetch no muera a los 10 segundos
      const ragRes = await fetch(url, { 
        method: "GET", 
        signal: controller.signal 
      });
      
      clearTimeout(timeoutId); // Limpiar el cronómetro si Python responde

    if (ragRes.ok) {
      const results: RAGDocument[] = await ragRes.json();

      if (model === 'colpali') {
          images = await processColpaliResults(results, 2);
      } else if (model === 'text') {
          retrievedDocs = await processTextResults(results);
      }
    } else {
      retrievedDocs = "Error al consultar la base de conocimiento.";
    }
    } catch (fetchError: any) {
      if (fetchError.name === 'AbortError') {
        console.error("❌ El servidor de Python tardó demasiado (Timeout)");
        retrievedDocs = "La base de conocimiento tardó demasiado en procesar.";
      } else {
        console.error("❌ Error de conexión con Python:", fetchError);
        retrievedDocs = "No se pudo conectar con el motor de búsqueda.";
      }
    }

    // 4) Armamos el prompt final para el modelo
    // Aquí es donde estructuramos la información separada
    let promptConContexto = userMessage;
    if (datos_placa) {
      promptConContexto = `
INFORMACIÓN TÉCNICA DETECTADA EN PLACA:
${datos_placa}

PREGUNTA DEL TÉCNICO:
${userMessage}
      `.trim();
    }

    const ragInstruction = RAG_INSTRUCTIONS[currentConfig.rag_mode as keyof typeof RAG_INSTRUCTIONS];
    const toneInstruction = TONE_INSTRUCTIONS[currentConfig.tone_mode as keyof typeof TONE_INSTRUCTIONS];

    // If the user language is English, translate the RAG and tone instructions to English
    let ragForPrompt = ragInstruction;
    let toneForPrompt = toneInstruction;
    if (detectedLang === 'en') {
      try {
        ragForPrompt = await translateForRAG(ragInstruction, 'es');
      } catch (e) {
        console.error('Error translating ragInstruction to en, using original:', e);
        ragForPrompt = ragInstruction;
      }
      try {
        toneForPrompt = await translateForRAG(toneInstruction, 'es');
      } catch (e) {
        console.error('Error translating toneInstruction to en, using original:', e);
        toneForPrompt = toneInstruction;
      }
    }

    const systemPromptContent = getSystemPrompt(detectedLang, retrievedDocs, model, ragForPrompt, toneForPrompt);
    const systemPrompt = {
      role: "system",
      content: systemPromptContent
    };

      // DEBUG: loguear el prompt que se envía al LLM para verificar RAG/TONE
      try {
        console.log('--- SYSTEM PROMPT START ---');
        console.log(systemPromptContent.slice(0, 4000));
        console.log('--- SYSTEM PROMPT END ---');
      } catch (e) {
        console.error('Error logging systemPromptContent', e);
      }

    // 5) Enviamos a Groq
    const userContent: object[] = [{ type: "text", text: promptConContexto }];
    if (model === 'colpali' && images && images.length > 0) {
      userContent.push(...images);
    }

    const body = {
      model: "meta-llama/llama-4-scout-17b-16e-instruct",
      messages: [
        systemPrompt,
        ...messages,
        { role: "user", content: userContent }
      ],
      max_tokens: 1500,
      temperature: 0.6,
      stream: true
    };

    const groqRes = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${process.env.GROQ_API_KEY}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(body)
    });

    if (!groqRes.ok) {
      const errorText = await groqRes.text();
      console.error('❌ Error en Groq:', errorText);
      return new Response(errorText, { status: 500 });
    }

    // 6) Manejo del Stream
    const reader = groqRes.body!.getReader();
    const stream = new ReadableStream({
      async start(controller) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          controller.enqueue(value);
        }
        controller.close();
      }
    });

    return new Response(stream, {
      headers: { "Content-Type": "text/event-stream" }
    });

  } catch (err) {
    console.error('Error en POST:', err);
    return new Response(
      JSON.stringify({ error: "Server error", details: String(err) }),
      { status: 500 }
    );
  }
}