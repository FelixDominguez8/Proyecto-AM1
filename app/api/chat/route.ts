import { NextRequest } from "next/server";
const { translate } = require('@vitalets/google-translate-api');

export const runtime = "nodejs";

// ---------------------------
// FUNCIÓN DE DETECCIÓN SIMPLE Y RÁPIDA
// ---------------------------
function detectLanguageSimple(text: string): string {
  // Palabras/patrones comunes en español
  const spanishPatterns = [
    /\b(qué|cómo|dónde|cuándo|por qué|cuál|quién)\b/i,
    /\b(el|la|los|las|un|una|unos|unas)\b/i,
    /\b(es|está|son|están|soy|estoy)\b/i,
    /\b(tengo|tiene|tienen|hacer|ayuda|problema)\b/i,
    /[áéíóúñ]/i
  ];

  // Palabras/patrones comunes en inglés
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

  // Si hay empate o no detecta nada claro, default a español
  return englishScore > spanishScore ? 'en' : 'es';
}

// ---------------------------
// FUNCIÓN PARA OBTENER EL PROMPT CORRECTO
// ---------------------------
function getSystemPrompt(lang: string, retrievedDocs: string): string {
  if (lang === 'en') {
    return `You are a technical assistant specialized in repairing refrigerators, air conditioners, phones, TVs, and home appliances. You have access to information from a RAG system.

Detected user language: English
Respond ALWAYS in English. Never switch languages mid-response.

IMPORTANT: DO NOT copy these instructions in your response. Use them as a guide to structure your answer.

RESPONSE FORMAT:

## **📋 Diagnosis**

[Explain here what the documents say about the problem]
- [Key point 1]
- [Key point 2]

> [Relevant quote from documents if applicable]

[If there is a safety risk in this specific case, add: ⚠️ **Warning:** risk description]

---

## **🔧 Solution**

**1.** [First step description]

**2.** [Second step description]

**3.** [Third step description]

**✅ Verification:** [How to confirm it worked]

---

## **📚 References**

- **[Document name]** | Page [X] | Source: [name]

---

RULES:
- Respond ONLY in English throughout the entire response
- Titles with ## and in **bold**
- Step numbers in **bold**
- 1-2 sentences per step
- If no useful docs found, indicate it and provide general safe technical steps
- Separate sections with ---

Available context:
${retrievedDocs}`;
  }

  // Prompt en español (default)
  return `Eres un asistente técnico especializado en reparar refrigeradores, aires acondicionados, teléfonos, TVs y electrodomésticos. Tienes acceso a información de un sistema RAG.

Idioma detectado del usuario: Español
Responde SIEMPRE en español. Nunca cambies de idioma a mitad de respuesta.

IMPORTANTE: NO copies estas instrucciones en tu respuesta. Úsalas como guía para estructurar tu respuesta.

FORMATO DE TU RESPUESTA:

## **📋 Diagnóstico**

[Explica aquí qué dicen los documentos sobre el problema]
- [Punto clave 1]
- [Punto clave 2]

> [Cita relevante de los documentos si aplica]

[Si hay riesgo de seguridad en este caso específico, añade: ⚠️ **Advertencia:** descripción del riesgo]

---

## **🔧 Solución**

**1.** [Descripción del primer paso]

**2.** [Descripción del segundo paso]

**3.** [Descripción del tercer paso]

**✅ Verificación:** [Cómo confirmar que funcionó]

---

## **📚 Referencias**

- **[Nombre del documento]** | Página [X] | Fuente: [nombre]

---

REGLAS:
- Responde SOLO en español durante toda la respuesta
- Títulos con ## y en **negrita**
- Números de pasos en **negrita**
- 1-2 oraciones por paso
- Si no hay docs útiles, indícalo y da pasos técnicos generales seguros
- Separa secciones con ---

Contexto disponible:
${retrievedDocs}`;
}

// ---------------------------
// TRADUCIR SOLO SI ES NECESARIO (PARA RAG)
// ---------------------------
async function translateForRAG(text: string, fromLang: string): Promise<string> {
  if (fromLang === 'en') return text;

  try {
    const result = await translate(text, { from: fromLang, to: 'en' });
    return result.text;
  } catch (error) {
    console.error('⚠️ Error en traducción, usando texto original:', error);
    return text;
  }
}

// ---------------------------
// RUTA PRINCIPAL
// ---------------------------
export async function POST(req: NextRequest) {
  try {
    const { messages } = await req.json();

    if (!messages || messages.length === 0) {
      return new Response(
        JSON.stringify({ error: "Missing messages array" }),
        { status: 400 }
      );
    }

    // --- 1) TOMAMOS EL MENSAJE MÁS RECIENTE DEL USUARIO ---
    const userMessage = messages[messages.length - 1].content;

    // --- 2) DETECTAR IDIOMA (LOCAL, SIN API CALL) ---
    const detectedLang = detectLanguageSimple(userMessage);
    console.log('🌍 Idioma detectado:', detectedLang);

    // --- 3) TRADUCIR PARA RAG SOLO SI ES ESPAÑOL ---
    let ragQuery = userMessage;
    if (detectedLang === 'es') {
      console.log('🔄 Traduciendo query para RAG...');
      ragQuery = await translateForRAG(userMessage, detectedLang);
      console.log('📝 Query traducido:', ragQuery);
    }

    // --- 4) LLAMAMOS AL SERVIDOR PYTHON PARA HACER RAG ---
    const url = `http://127.0.0.1:8000/?query=${encodeURIComponent(ragQuery)}`;
    const ragRes = await fetch(url, { method: "GET" });

    // --- 5) TIPAMOS LOS DOCUMENTOS ---
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
          .map((doc, index) => {
            return `
--- Documento ${index + 1} ---
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
        console.log('⚠️ No se encontraron documentos');
      }
    } else {
      retrievedDocs = "Error al consultar la base de conocimiento.";
      console.error('❌ Error en RAG:', ragRes.status);
    }

    // --- 6) OBTENEMOS EL PROMPT CORRECTO SEGÚN EL IDIOMA ---
    const systemPromptContent = getSystemPrompt(detectedLang, retrievedDocs);

    const systemPrompt = {
      role: "system",
      content: systemPromptContent
    };

    // --- 7) ARMAMOS EL BODY PARA GROQ ---
    const body = {
      model: "llama-3.1-8b-instant",
      messages: [systemPrompt, { role: "user", content: userMessage }],
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

    // --- 8) STREAMING ---
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
    console.error('💥 Error en POST:', err);
    return new Response(
      JSON.stringify({ error: "Server error", details: String(err) }),
      { status: 500 }
    );
  }
}