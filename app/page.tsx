"use client";

import React, { useState, useRef, useEffect, ChangeEvent } from "react";
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

  const [history, setHistory] = useState<ChatHistoryItem[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);

  const bottomRef = useRef<HTMLDivElement | null>(null);
  const firstChatCreated = useRef(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const [view, setView] = useState("chat"); // "chat" o "settings"
  const [ragMode, setRagMode] = useState("rag-extra");

  const [toneMode, setToneMode] = useState("normal");

  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [currentFeedback, setCurrentFeedback] = useState<{
    msgIndex: number | null;
    type: 'like' | 'dislike' | null;
    comment: string;
  }>({ 
    msgIndex: null, 
    type: null, 
    comment: "" 
  });

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      setSelectedFile(file);
      // Crear URL para la miniatura
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    }
  }

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

  useEffect(() => {
    localStorage.setItem("chat_history", JSON.stringify(history));
  }, [history]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const saveCurrentChatToHistory = (updatedMessages: Message[]) => {
    // primera vez
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

      firstChatCreated.current = true;

      return;
    }

    if (!activeChatId) return;

    // Actualizar
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

  const selectChat = (id: string) => {
    setActiveChatId(id);
    const found = history.find((h) => h.id === id);
    if (found) setMessages(found.messages);
  };

  const sendMessage = async () => {
    // 1) Validación inicial: enviamos si hay texto O si hay imagen
    if ((!input.trim() && !selectedFile) || loading) return;

    setLoading(true);

    // --- PASO 1: Actualizar la interfaz (lo que ve el usuario) ---
    const userMessage: Message = { role: "user", content: input };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    saveCurrentChatToHistory(newMessages);

    const currentInput = input; // Guardamos el input actual antes de limpiar
    const currentFile = selectedFile; // Guardamos el archivo antes de limpiar

    setInput("");
    setSelectedFile(null); // Limpiamos la imagen después de capturarla para el envío
    setPreviewUrl(null);

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

    // --- PASO 2: Enviar al backend usando FormData ---
    // Agrupamos todo en un solo sobre para que el backend use tesseract.py
    const formData = new FormData();
    if (currentFile) {
      formData.append("file", currentFile);
    }
    formData.append("pregunta_usuario", currentInput);
    formData.append("messages", JSON.stringify(messages));

    const response = await fetch("/api/chat", {
      method: "POST",
      // IMPORTANTE: No enviamos headers de Content-Type, el navegador gestiona el boundary del FormData
      body: formData,
    });

    if (!response.body) {
      setLoading(false);
      return;
    }

    // --- PASO 3: Lógica de streaming original (completa) ---
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
              saveCurrentChatToHistory(updated);
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
              onClick={() => {
                selectChat(chat.id);
                setView("chat");
              }}
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

        <div className="p-4 border-t border-white/20 dark:border-zinc-800/40 space-y-2">
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
          {/* BOTÓN DE CONFIGURACIÓN AGREGADO */}
          <button
            onClick={() => setView(view === "chat" ? "settings" : "chat")}
            className={`
              w-full py-3 rounded-xl
              text-sm font-medium
              border border-white/30
              transition backdrop-blur-md
              ${view === "settings" ? "bg-white/40 text-white" : "bg-white/10 text-white/70 hover:bg-white/20"}
            `}
          >
            Configuración
          </button>
        </div>
      </aside>

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
        <div className="flex items-center justify-center h-16 border-b border-zinc-300 dark:border-zinc-800 bg-white/20 dark:bg-zinc-900/20 backdrop-blur-md shadow-inner">
          <h1 className="text-xl font-bold tracking-tight text-zinc-800 dark:text-zinc-400">
            <img src="/1.png" alt="Logo" className="h-45 w-auto" />
          </h1>
        </div>

        {view === "chat" ? (
          <>
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
                        {msg.role === "assistant" && (
                    <div className="flex items-center gap-4 mt-4 pt-4 border-t border-zinc-300/30">
                      <button 
                        onClick={() => {
                          setCurrentFeedback({ msgIndex: i, type: 'like', comment: "" });
                          setShowFeedbackModal(true);
                        }}
                        className="text-zinc-500 hover:text-green-500 transition-colors flex items-center gap-1 text-xs font-medium"
                      >
                        👍 Útil
                      </button>
                      <button 
                        onClick={() => {
                          setCurrentFeedback({ msgIndex: i, type: 'dislike', comment: "" });
                          setShowFeedbackModal(true);
                        }}
                        className="text-zinc-500 hover:text-red-500 transition-colors flex items-center gap-1 text-xs font-medium"
                      >
                        👎 No me sirvió
                      </button>
                    </div>
                  )}
                      </div>
                    ) : (
                      msg.content
                    )}
                  </div>
                  
                </div>
              ))}

              {loading && (
                <div className="text-sm text-white italic animate-pulse">
                  Escribiendo…
                </div>
              )}

              <div ref={bottomRef} />
            </div>

            <div className="p-5 border-t border-zinc-300 dark:border-zinc-800 bg-white/20 dark:bg-zinc-950/20 backdrop-blur-md shadow-inner">
              <div className="relative flex flex-col w-full max-w-4xl mx-auto">
                {previewUrl && (
                  <div className="absolute -top-20 left-0 flex items-center gap-3 bg-white/80 dark:bg-zinc-900/80 backdrop-blur-md p-2 rounded-xl border border-zinc-300 dark:border-zinc-700 shadow-lg animate-in fade-in slide-in-from-bottom-2">
                    <img
                      src={previewUrl}
                      alt="Preview"
                      className="h-12 w-12 object-cover rounded-lg border border-zinc-400"
                    />
                    <div className="flex flex-col">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-zinc-500">
                        Placa detectada
                      </span>
                      <button
                        onClick={() => {
                          setSelectedFile(null);
                          setPreviewUrl(null);
                        }}
                        className="text-xs text-red-500 hover:underline"
                      >
                        Eliminar
                      </button>
                    </div>
                  </div>
                )}

                <div className="relative flex items-center w-full bg-zinc-100 dark:bg-zinc-900 border border-zinc-300 dark:border-zinc-700 rounded-2xl transition-all focus-within:ring-2 focus-within:ring-blue-400">
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileChange}
                    style={{ display: "none" }}
                    accept="image/*"
                  />

                  <button
                    onClick={handleButtonClick}
                    className={`ml-2 p-2 rounded-xl transition-all ${selectedFile ? "bg-blue-100 dark:bg-blue-900/30 ring-1 ring-blue-500" : "hover:bg-zinc-200 dark:hover:bg-zinc-800"} active:scale-90 group`}
                  >
                    <img
                      src="/Subir.png"
                      alt="Subir"
                      className={`h-8 w-8 transition-opacity ${selectedFile ? "opacity-100" : "opacity-60 group-hover:opacity-100"}`}
                    />
                  </button>

                  <input
                    className="w-full bg-transparent px-3 py-4 pr-28 text-[15px] focus:outline-none"
                    placeholder={
                      selectedFile
                        ? "Pregunta sobre esta placa..."
                        : "Escribe tu pregunta técnica..."
                    }
                    value={input}
                    disabled={loading}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                  />

                  <button
                    onClick={sendMessage}
                    disabled={loading}
                    className="absolute right-2 px-5 py-2.5 rounded-xl bg-blue-600 text-white hover:bg-blue-700 disabled:bg-blue-400 shadow-md transition-all active:scale-95"
                  >
                    {loading ? (
                      <div className="flex items-center gap-2">
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      </div>
                    ) : (
                      "Enviar"
                    )}
                  </button>
                </div>
              </div>

              <p className="text-center text-xs text-zinc-800 dark:text-zinc-400 mt-3">
                Llama 4 Scout · vía Groq · Streaming activado
              </p>
            </div>
          </>
        ) : (
          /* SECCIÓN DE CONFIGURACIÓN */
          <div className="flex-1 overflow-y-auto px-6 py-10 max-w-4xl mx-auto w-full animate-in fade-in slide-in-from-right-4 duration-300 scrollbar-hide">
            <style jsx>{`
              .scrollbar-hide::-webkit-scrollbar { display: none; }
              .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
            `}</style>
            
            <div className="w-full px-8 py-8 rounded-2xl bg-white/70 dark:bg-zinc-900/70 backdrop-blur-xl border border-white/20 dark:border-zinc-800/50 shadow-2xl space-y-8">
              <h2 className="text-3xl font-bold text-zinc-800 dark:text-zinc-100 border-b border-zinc-300 dark:border-zinc-800 pb-4">
                Configuración
              </h2>

              {/* SECCIÓN: TIPO DE RESPUESTA */}
              <section className="space-y-6">
                <h3 className="text-lg font-medium text-zinc-700 dark:text-zinc-300 flex items-center gap-2">
                  <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                  Tipo de Respuesta (RAG)
                </h3>
                
                <div className="grid grid-cols-1 gap-4">
                  {[
                    {
                      id: "only-rag",
                      label: "Solo RAG",
                      desc: "Basado únicamente en el RAG. No se permite ampliar fuera de los manuales proporcionados.",
                    },
                    {
                      id: "rag-extra",
                      label: "RAG + Extra",
                      desc: "Basado en RAG pero amplía sobre puntos importantes o necesarios para el técnico.",
                    },
                    {
                      id: "rag-ref",
                      label: "RAG como Referencia",
                      desc: "Usa el conocimiento del modelo como base, consultando el RAG solo si es adecuado.",
                    },
                  ].map((option) => (
                    <button
                      key={option.id}
                      onClick={() => setRagMode(option.id)}
                      className={`flex flex-col text-left p-5 rounded-2xl border transition-all duration-200 ${
                        ragMode === option.id
                          ? "bg-blue-600 border-blue-400 text-white shadow-lg shadow-blue-500/30 scale-[1.02]"
                          : "bg-white/40 dark:bg-zinc-800/40 border-white/20 dark:border-zinc-700/30 hover:bg-white/60 dark:hover:bg-zinc-700/60 text-zinc-800 dark:text-zinc-200"
                      }`}
                    >
                      <span className="font-bold text-base">{option.label}</span>
                      <span className={`text-sm mt-1 ${ragMode === option.id ? "text-blue-100" : "text-zinc-500 dark:text-zinc-400"}`}>
                        {option.desc}
                      </span>
                    </button>
                  ))}
                </div>
              </section>

              {/* SECCIÓN: TONO DE VOZ (NUEVA) */}
              <section className="space-y-6">
                <h3 className="text-lg font-medium text-zinc-700 dark:text-zinc-300 flex items-center gap-2">
                  <span className="w-2 h-2 bg-emerald-500 rounded-full"></span>
                  Tono de Voz
                </h3>
                
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {[
                    {
                      id: "casual",
                      label: "Casual",
                      desc: "Lenguaje relajado y fácil de entender.",
                    },
                    {
                      id: "normal",
                      label: "Normal",
                      desc: "El equilibrio estándar del modelo.",
                    },
                    {
                      id: "formal",
                      label: "Formal",
                      desc: "Lenguaje técnico, preciso y profesional.",
                    },
                  ].map((option) => (
                    <button
                      key={option.id}
                      onClick={() => setToneMode(option.id)}
                      className={`flex flex-col text-left p-5 rounded-2xl border transition-all duration-200 ${
                        toneMode === option.id
                          ? "bg-emerald-600 border-emerald-400 text-white shadow-lg shadow-emerald-500/30 scale-[1.02]"
                          : "bg-white/40 dark:bg-zinc-800/40 border-white/20 dark:border-zinc-700/30 hover:bg-white/60 dark:hover:bg-zinc-700/60 text-zinc-800 dark:text-zinc-200"
                      }`}
                    >
                      <span className="font-bold text-base">{option.label}</span>
                      <span className={`text-xs mt-1 ${toneMode === option.id ? "text-emerald-100" : "text-zinc-500 dark:text-zinc-400"}`}>
                        {option.desc}
                      </span>
                    </button>
                  ))}
                </div>
              </section>

              <div className="pt-6 border-t border-zinc-300 dark:border-zinc-800">
                <button
                  onClick={() => setView("chat")}
                  className="w-full sm:w-auto px-10 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-2xl font-bold transition-all active:scale-95 shadow-lg shadow-blue-600/20"
                >
                  Guardar y Volver al Chat
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {showFeedbackModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="w-full max-w-md p-6 rounded-2xl bg-white/90 dark:bg-zinc-900/90 backdrop-blur-xl border border-white/20 shadow-2xl space-y-4">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${currentFeedback.type === 'like' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}>
                {currentFeedback.type === 'like' ? '👍' : '👎'}
              </div>
              <h3 className="text-xl font-bold">Cuéntanos más</h3>
            </div>
            
            <p className="text-sm text-zinc-600 dark:text-zinc-400">
              ¿Por qué esta respuesta fue {currentFeedback.type === 'like' ? 'buena' : 'mala'}? Tu comentario ayudará a mejorar los manuales y el modelo.
            </p>

            <textarea
              className="w-full h-32 p-4 bg-zinc-100 dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-xl focus:ring-2 focus:ring-blue-500 focus:outline-none text-sm resize-none"
              placeholder="Ej: El manual decía X, pero la respuesta sugirió Y..."
              value={currentFeedback.comment}
              onChange={(e) => setCurrentFeedback({...currentFeedback, comment: e.target.value})}
            />

            <div className="flex gap-3 pt-2">
              <button
                onClick={() => { setShowFeedbackModal(false); setCurrentFeedback({msgIndex: null, type: null, comment: ""}); }}
                className="flex-1 px-4 py-2.5 rounded-xl border border-zinc-300 dark:border-zinc-700 font-medium hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
              >
                Omitir
              </button>
              <button
                onClick={() => {
                  // Validamos que el índice no sea null antes de proceder
                  if (currentFeedback.msgIndex !== null) {
                    const userQuestion = messages[currentFeedback.msgIndex - 1]?.content;
                    const aiResponse = messages[currentFeedback.msgIndex]?.content;

                    // Aquí es donde enviarías los datos para crear el TXT
                    console.log("Generando reporte para TXT:", {
                      pregunta: userQuestion,
                      respuesta: aiResponse,
                      puntuacion: currentFeedback.type,
                      comentario: currentFeedback.comment
                    });
                  }
                  
                  setShowFeedbackModal(false);
                  setCurrentFeedback({msgIndex: null, type: null, comment: ""});
                }}
                className="flex-1 px-4 py-2.5 rounded-xl bg-blue-600 text-white font-medium hover:bg-blue-700 transition-shadow shadow-lg shadow-blue-600/20"
              >
                Enviar Feedback
              </button>
            </div>
          </div>
        </div>
      )}
      
    </div>
  );
}

