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
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    setLoading(true);

    const botMessage: Message = { role: "assistant", content: "" };
    setMessages((prev) => [...prev, botMessage]);
    const botIndex = messages.length;

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
    <div className="flex h-screen w-full bg-zinc-100 dark:bg-black text-black dark:text-zinc-100">
      <div className="flex flex-col mx-auto w-full max-w-3xl h-full border-l border-r border-zinc-300 dark:border-zinc-800 bg-white dark:bg-zinc-950">

        <div className="flex items-center justify-center h-14 border-b border-zinc-300 dark:border-zinc-800 bg-white/70 dark:bg-zinc-900/70 backdrop-blur">
          <h1 className="text-lg font-semibold tracking-tight">Mi Chatbot Técnico</h1>
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-6 space-y-6">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-xl px-4 py-3 rounded-2xl shadow-sm text-[15px] leading-relaxed ${
                  msg.role === "user"
                    ? "bg-blue-600 text-white rounded-br-md"
                    : "bg-zinc-200 dark:bg-zinc-800 text-black dark:text-zinc-200 rounded-bl-md"
                }`}
              >
                {msg.role === "assistant" ? (
                  <div className="prose dark:prose-invert whitespace-pre-wrap">
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
            <div className="text-sm text-zinc-500 dark:text-zinc-400">Escribiendo…</div>
          )}

          <div ref={bottomRef} />
        </div>

        <div className="p-5 border-t border-zinc-300 dark:border-zinc-800 bg-white dark:bg-zinc-950">
          <div className="relative flex items-center">

            <input
              className="w-full px-5 py-4 pr-16 rounded-2xl bg-zinc-100 dark:bg-zinc-900 border border-zinc-300 dark:border-zinc-700 text-[15px] focus:outline-none focus:border-blue-500 dark:focus:border-blue-400"
              placeholder="Escribe tu pregunta técnica..."
              value={input}
              disabled={loading}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            />

            <button
              onClick={sendMessage}
              disabled={loading}
              className="absolute right-3 px-4 py-2 rounded-xl bg-blue-600 text-white hover:bg-blue-700 disabled:bg-blue-400 transition text-sm"
            >
              Enviar
            </button>
          </div>

          <p className="text-center text-xs text-zinc-500 dark:text-zinc-400 mt-3">
            Llama 3.1 · vía Groq · Streaming activado
          </p>
        </div>
      </div>
    </div>
  );
}
