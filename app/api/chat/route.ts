import { NextRequest } from "next/server";

export const runtime = "edge";

export async function POST(req: NextRequest) {
  try {
    const { messages } = await req.json();

    if (!messages) {
      return new Response(
        JSON.stringify({ error: "Missing messages array" }),
        { status: 400 }
      );
    }

    const systemPrompt = {
      role: "system",
      content: `
    Eres un asistente técnico especializado en reparar refrigeradores, teléfonos, TVs y otros electrodomésticos.

    Responde siempre en español, usando **Markdown** para el formato. Debes:

    - Usar títulos (## Título) cuando sea necesario
    - Usar numeración o bullets para pasos
    - Separar secciones con líneas vacías (doble salto de línea)
    - Usar negritas o cursivas cuando convenga
    - Ser claro y conciso, no extenderte innecesariamente

    Ejemplo de respuesta:

    ## Cómo revisar un refrigerador

    1. Paso 1: Verifica que esté conectado a la corriente.
    2. Paso 2: Revisa si el termostato está funcionando.
    3. Paso 3: Comprueba que el motor no haga ruidos extraños.

    **Consejos adicionales:**

    - Siempre desenchufa antes de manipular componentes internos.
    - Documenta cualquier falla para seguimiento.

    Responde siempre con este estilo, usando Markdown para todos los títulos, listas y párrafos.
    `
    };


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

    const reader = groqRes.body!.getReader();

    const stream = new ReadableStream({
      async start(controller) {
        const decoder = new TextDecoder();

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          controller.enqueue(value);
        }

        controller.close();
      }
    });

    return new Response(stream, {
      headers: {
        "Content-Type": "text/event-stream"
      }
    });

  } catch (err) {
    console.error(err);
    return new Response(
      JSON.stringify({ error: "Server error", details: err }),
      { status: 500 }
    );
  }
}
