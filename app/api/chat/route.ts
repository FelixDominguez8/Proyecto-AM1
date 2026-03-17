import { NextRequest } from "next/server";
const { translate } = require('@vitalets/google-translate-api');
import { execSync } from 'child_process';
import { writeFile } from 'fs/promises';
import path from 'path';

export const runtime = "nodejs";


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

function getSystemPrompt(lang: string, retrievedDocs: string): string {
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
- RAG Priority: Use RAG steps exclusively. If 10 steps exist, output 10.
- Fallback: If RAG is missing/irrelevant, provide general safe technical guidance.
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
- Prioridad RAG: Usa pasos del RAG exclusivamente. Si hay 10 pasos, entrega los 10.
- Contingencia: Si el RAG falta o es irrelevante, brinda guía técnica general segura.
- Formato: Secciones divididas por ---. Títulos con ## y en **negrita**. Números en **negrita**.

--- CONTEXTO E INFO DEL DISPOSITIVO ---
Contexto: ${retrievedDocs}

Nota: Usa la "Información del dispositivo" (OCR) para identificar modelos. Si el texto es confuso, prioriza coincidencias que se alineen con los documentos técnicos.`;
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

export async function POST(req: NextRequest) {
  try {
    /// 1) Extraemos los campos usando formData para soportar la imagen y el historial
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
        datos_placa = execSync(`python tesseract.py "${tempPath}"`).toString().trim();
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
    const url = `http://127.0.0.1:8000/?query=${encodeURIComponent(ragQuery)}`;
    const ragRes = await fetch(url, { method: "GET" });

    interface RAGDocument {
      text: string;
      source: string;
      page: number;
      title?: string;
    }

    let retrievedDocs = "";

    if (ragRes.ok) {
      const results: RAGDocument[] = await ragRes.json();
      if (results.length > 0) {
        retrievedDocs = results
          .map((doc) => {
            return `
            --- ${doc.title || "Sin título"} ---
            [Página]: ${doc.page}
            [Source]: ${doc.source}
            [Texto]: ${doc.text}
            `.trim();
          })
          .join("\n\n");
        console.log(`✅ ${results.length} documentos recuperados`);
      } else {
        retrievedDocs = "No se encontraron documentos relevantes.";
      }
    } else {
      retrievedDocs = "Error al consultar la base de conocimiento.";
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

    const systemPromptContent = getSystemPrompt(detectedLang, retrievedDocs);
    const systemPrompt = {
      role: "system",
      content: systemPromptContent
    };

    // 5) Enviamos a Groq
    const body = {
      model: "meta-llama/llama-4-scout-17b-16e-instruct",
      // Incluimos el historial (messages) y el nuevo mensaje estructurado
      messages: [
        systemPrompt, 
        ...messages, 
        { role: "user", content: promptConContexto }
      ],
      max_tokens: 1500,
      temperature: 0.3,
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