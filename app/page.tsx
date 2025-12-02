"use client";

import React, { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = { role: "user", content: input };

    // 1️⃣ Agregar mensaje del usuario
    setMessages((prev) => [...prev, userMessage]);

    setInput("");
    setLoading(true);

    // 2️⃣ Crear placeholder del bot
    let botIndex = 0;
    setMessages((prev) => {
      botIndex = prev.length; // el bot será el siguiente índice
      return [...prev, { role: "assistant", content: "" }];
    });

    // 3️⃣ Llamada al API
    const response = await fetch("/api/chat", {
      method: "POST",
      body: JSON.stringify({ messages: [...messages, userMessage] }),
      headers: { "Content-Type": "application/json" },
    });

    if (!response.body) {
      setLoading(false);
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;

        const dataStr = line.replace(/^data: /, "").trim();
        if (dataStr === "[DONE]") break;

        try {
          const parsed = JSON.parse(dataStr);
          const delta = parsed.choices[0].delta?.content;
          if (delta) {
            setMessages((prev) => {
              const updated = [...prev];
              updated[botIndex] = {
                role: "assistant",
                content: (updated[botIndex].content || "") + delta,
              };
              return updated;
            });
          }
        } catch (err) {
          console.error("Error parseando chunk:", err, line);
        }
      }
    }

    setLoading(false);
  };


  return (
    <div className="flex h-screen w-full bg-gradient-to-br from-zinc-100 to-zinc-200 dark:from-black dark:to-zinc-900 text-black dark:text-zinc-100"
    style={{
      backgroundImage: "url('https://images.unsplash.com/photo-1696550579911-4ece0b1899ea?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D')",
      backgroundRepeat: "no-repeat",
      backgroundPosition: "center",
      backgroundSize: "cover",
    }}
    >
      <div className="flex flex-col mx-auto w-full max-w-3xl h-[95vh] mt-[2.5vh] mb-[2.5vh] border-l border-r border-zinc-300 dark:border-zinc-800 bg-white dark:bg-zinc-950 shadow-xl rounded-xl overflow-hidden"
      style={{
        backgroundImage: "url('https://images.unsplash.com/photo-1676676701269-65de47175adf?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D')",
        backgroundRepeat: "no-repeat",
        backgroundPosition: "center",
        backgroundSize: "cover",
      }}
      >

        <div className="flex items-center justify-center h-16 border-b border-zinc-300 dark:border-zinc-800 bg-white/20 dark:bg-zinc-900/20 backdrop-blur-md shadow-inner">
          <h1 className="text-xl font-bold tracking-tight text-zinc-800 dark:text-zinc-400">
            Chat Técnico Inteligente
          </h1>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex transition-all duration-200 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-xl px-5 py-3 rounded-2xl shadow-md text-[15px] leading-relaxed break-words ${
                  msg.role === "user"
                    ? "bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-br-md hover:from-blue-600 hover:to-blue-700 transition"
                    : "bg-gradient-to-tr from-zinc-200 to-zinc-300 dark:from-zinc-800 dark:to-zinc-700 text-black dark:text-zinc-200 rounded-bl-md hover:from-zinc-300 hover:to-zinc-400 dark:hover:from-zinc-700 dark:hover:to-zinc-600 transition"
                }`}
              >
                {msg.role === "assistant" ? (
                  <div className="prose dark:prose-invert whitespace-pre-wrap font-sans">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                ) : (
                  msg.content
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="text-sm text-zinc-800 dark:text-zinc-400 italic animate-pulse">Escribiendo…</div>
          )}

          <div ref={bottomRef} />
        </div>

        <div className="p-5 border-t border-zinc-300 dark:border-zinc-800 bg-white/20 dark:bg-zinc-950/20 backdrop-blur-md shadow-inner">
          <div className="relative flex items-center">
            <input
              className="w-full px-5 py-4 pr-20 rounded-2xl bg-zinc-100 dark:bg-zinc-900 border border-zinc-300 dark:border-zinc-700 text-[15px] focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition"
              placeholder="Escribe tu pregunta técnica..."
              value={input}
              disabled={loading}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            />

            <button
              onClick={sendMessage}
              disabled={loading}
              className="absolute right-3 px-5 py-3 rounded-full bg-blue-600 text-white hover:bg-blue-700 disabled:bg-blue-400 shadow-md transition-all"
            >
              Enviar
            </button>
          </div>

          <p className="text-center text-xs text-zinc-800 dark:text-zinc-400 mt-3">
            Llama 3.1 · vía Groq · Streaming activado
          </p>
        </div>
      </div>
    </div>
  );
}
