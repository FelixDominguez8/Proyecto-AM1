import { NextRequest } from "next/server";

export const runtime = "edge";

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

    // --- 2) LLAMAMOS AL SERVIDOR PYTHON PARA HACER RAG ---
    const url = `http://127.0.0.1:8000/?query=${encodeURIComponent(userMessage)}`;
    const ragRes = await fetch(url, { method: "GET" });

    // --- 3) TIPAMOS LOS DOCUMENTOS ---
    interface RAGDocument {
      text: string;
      source: string;
      page: number;
      title?: string;
    }

    let retrievedDocs = "";

    if (ragRes.ok) {
      const results: RAGDocument[] = await ragRes.json();

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

    } else {
      retrievedDocs = "No se recolectaron los documentos";
    }

    // --- 4) IMPRIMIMOS EN CONSOLA ---
    console.log("Retrieved Docs:\n", retrievedDocs);

    // --- 5) ARMAMOS EL SYSTEM PROMPT + CONTEXTO RECUPERADO ---
    const systemPrompt = {
      role: "system",
      content: `
Eres un asistente técnico especializado en reparar refrigeradores, aires acondicionados,
teléfonos, TVs y electrodomésticos. Tienes acceso a información proveniente de un sistema RAG.

INSTRUCCIONES IMPORTANTES:

1. Usa formato **Markdown**:
   - Títulos con "##"
   - Subtítulos con "###"
   - Bullet points y numeración cuando sea útil
   - Doble salto de línea entre secciones
2. Divide SIEMPRE tu respuesta en estas secciones:

## Significado (según documentos)
- Explica **exactamente** lo que digan los documentos encontrados.
- Si los documentos solo ofrecen una descripción parcial, indícalo.
- NO inventes información que los documentos no contienen.

## Qué hacer (usando información del usuario + experiencia técnica)
- Si los documentos traen pasos específicos, úsalos.
- Si no hay pasos en los documentos, entonces usa tu conocimiento técnico general.

## Referencias
Por cada fragmento utilizado del RAG, incluye:
- **Título**
- **Página**
- **Source**
- (Opcional) Una frase breve explicando por qué fue relevante

3. Si NO se encontró información útil en los documentos:
   - Indícalo claramente
   - Pero igual da pasos técnicos generales seguros y útiles

5. Sé muy claro, organizado y conciso.

Tu prioridad: producir respuestas técnicas confiables, bien estructuradas y fáciles de leer.

Este es el contexto a utilizar: 
${retrievedDocs}
      `
    };

    // --- 7) ARMAMOS EL BODY PARA GROQ ---
    const body = {
      model: "llama-3.1-8b-instant",
      messages: [systemPrompt, ...messages],
      max_tokens: 512,
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
    console.error(err);
    return new Response(
      JSON.stringify({ error: "Server error", details: err }),
      { status: 500 }
    );
  }
}
