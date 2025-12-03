"use client";

import React, { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ChatHistoryItem {
  id: string;
  title: string;
  messages: Message[];
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  // ⬅️ Nuevo: historial local
  const [history, setHistory] = useState<ChatHistoryItem[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);

  const bottomRef = useRef<HTMLDivElement | null>(null);
  const firstChatCreated = useRef(false);

  // ⬅️ Cargar historial desde localStorage al iniciar
  useEffect(() => {
    const saved = localStorage.getItem("chat_history");
    if (saved) {
      const parsed: ChatHistoryItem[] = JSON.parse(saved);
      setHistory(parsed);

      if (parsed.length > 0) {
        setActiveChatId(parsed[0].id);
        setMessages(parsed[0].messages);
      }
    }
  }, []);

  // ⬅️ Guardar historial en localStorage cuando cambia
  useEffect(() => {
    localStorage.setItem("chat_history", JSON.stringify(history));
  }, [history]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const saveCurrentChatToHistory = (updatedMessages: Message[]) => {
    // ⬅️ Crear primer chat SOLO UNA VEZ
    if (!activeChatId && !firstChatCreated.current) {
      const id = crypto.randomUUID();

      const firstMessage = updatedMessages[0]?.content;
      const title =
        firstMessage
          ? firstMessage.length > 50
            ? firstMessage.slice(0, 50) + "..."
            : firstMessage
          : "Nuevo chat";

      const newItem: ChatHistoryItem = {
        id,
        title,
        messages: updatedMessages,
      };

      setHistory((prev) => [newItem, ...prev]);
      setActiveChatId(id);

      // ⬅️ Marcar que ya se creó el primer chat
      firstChatCreated.current = true;

      return;
    }

    // ⬅️ Si aún no hay chatId (pero ya se intentó crear uno), NO hacer nada
    if (!activeChatId) return;

    // ⬅️ Actualizar el chat existente normalmente
    setHistory((prev) =>
      prev.map((chat) =>
        chat.id === activeChatId
          ? {
              ...chat,
              messages: updatedMessages,
              title:
                chat.messages.length === 0
                  ? updatedMessages[0]?.content.slice(0, 40) || "Nuevo chat"
                  : chat.title,
            }
          : chat
      )
    );
  };



  // ⬅️ Crear un chat nuevo
  const newChat = () => {
    const id = crypto.randomUUID();
    const newItem: ChatHistoryItem = {
      id,
      title: "Nuevo chat",
      messages: [],
    };

    setHistory((prev) => [newItem, ...prev]);
    setActiveChatId(id);
    setMessages([]);
  };

  // ⬅️ Seleccionar un chat del historial
  const selectChat = (id: string) => {
    setActiveChatId(id);
    const found = history.find((h) => h.id === id);
    if (found) setMessages(found.messages);
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = { role: "user", content: input };

    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    saveCurrentChatToHistory(newMessages);

    setInput("");
    setLoading(true);

    let botIndex = 0;
    setMessages((prev) => {
      botIndex = prev.length;

      const updated: Message[] = [
        ...prev,
        { role: "assistant" as const, content: "" }
      ];

      saveCurrentChatToHistory(updated);
      return updated;
    });


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
              saveCurrentChatToHistory(updated); // ⬅️ guardar en historial
              return updated;
            });
          }
        } catch (err) {
          console.error("Error parsing chunk:", err, line);
        }
      }
    }

    setLoading(false);
  };

  return (
    <div
      className="flex h-screen w-full bg-gradient-to-br from-zinc-100 to-zinc-200 dark:from-black dark:to-zinc-900 text-black dark:text-zinc-100"
      style={{
        backgroundImage:
          "url('https://images.unsplash.com/photo-1696550579911-4ece0b1899ea?fm=jpg&q=60&w=3000')",
        backgroundRepeat: "no-repeat",
        backgroundPosition: "center",
        backgroundSize: "cover",
      }}
    >
      {/* -------------------- SIDEBAR -------------------- */}
      <aside
        className="
          w-64 
          h-full 
          border-r 
          border-white/20 
          dark:border-zinc-800/40
          bg-white/10 
          dark:bg-zinc-900/20 
          backdrop-blur-xl 
          shadow-xl
          flex flex-col
        "
      >
        <div className="px-5 py-4 border-b border-white/20 dark:border-zinc-700/40">
          <h2 className="text-lg font-semibold text-white">Historial</h2>
        </div>

        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-3">
          {history.map((chat) => (
            <button
              key={chat.id}
              onClick={() => selectChat(chat.id)}
              className={`
                w-full text-left px-4 py-3 rounded-xl
                bg-white/20 dark:bg-zinc-800/30
                hover:bg-white/30 dark:hover:bg-zinc-700/40
                backdrop-blur-md border
                border-white/20 dark:border-zinc-700/40
                text-sm text-zinc-800 dark:text-zinc-300 shadow-sm transition
                ${activeChatId === chat.id ? "ring-2 ring-blue-500" : ""}
              `}
            >
              {chat.title}
            </button>
          ))}
        </div>

        <div className="p-4 border-t border-white/20 dark:border-zinc-800/40">
          <button
            onClick={newChat}
            className="
              w-full py-3 rounded-xl
              text-sm font-medium
              bg-blue-600 hover:bg-blue-700 text-white
              shadow-md transition
            "
          >
            Nuevo chat
          </button>
        </div>
      </aside>

      {/* -------------------- MAIN CHAT -------------------- */}
      <div
        className="flex flex-col w-full h-screen 
  bg-white dark:bg-zinc-950 border-l border-zinc-300 dark:border-zinc-800 
  overflow-hidden"
        style={{
          backgroundImage:
            "url('https://images.unsplash.com/photo-1676676701269-65de47175adf?fm=jpg&q=60&w=3000')",
          backgroundRepeat: "no-repeat",
          backgroundPosition: "center",
          backgroundSize: "cover",
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-center h-16 border-b border-zinc-300 dark:border-zinc-800 bg-white/20 dark:bg-zinc-900/20 backdrop-blur-md shadow-inner">
          <h1 className="text-xl font-bold tracking-tight text-zinc-800 dark:text-zinc-400">
            <img src="/1.png" alt="Logo" className="h-45 w-auto" />
          </h1>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-30 py-6 space-y-4">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex transition-all duration-200 ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`${
                  msg.role === "user"
                    ? "max-w-xl px-5 py-3 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-md"
                    : "w-full px-6 py-5 rounded-xl bg-white/70 dark:bg-zinc-800/70 backdrop-blur-md border border-zinc-300 dark:border-zinc-700 shadow-lg"
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
            <div className="text-sm text-zinc-800 dark:text-zinc-400 italic animate-pulse">
              Escribiendo…
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="p-5 border-t border-zinc-300 dark:border-zinc-800 bg-white/20 dark:bg-zinc-950/20 backdrop-blur-md shadow-inner">
          <div className="relative flex items-center">
            <input
              className="w-full px-5 py-4 pr-26 rounded-2xl bg-zinc-100 dark:bg-zinc-900 border border-zinc-300 dark:border-zinc-700 text-[15px] focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition"
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
            Llama 4 Scout · vía Groq · Streaming activado
          </p>
        </div>
      </div>
    </div>
  );
}

