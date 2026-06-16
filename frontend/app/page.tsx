"use client";

import { useState } from "react";

interface Source {
  company: string;
  ticker: string;
  year: string;
  doc_type: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  sub_questions?: string[];
}

const SAMPLE_QUESTIONS = [
  "Compare Apple and Microsoft revenue in 2022",
  "What risks did Meta cite in their 2023 10-K filing?",
  "What drove Amazon revenue growth from 2021 to 2023?",
  "Compare R&D spending across all Big Tech companies in 2022",
];

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async (question: string) => {
    if (!question.trim() || loading) return;

    const userMsg: Message = { role: "user", content: question };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      const data = await res.json();

      const assistantMsg: Message = {
        role: "assistant",
        content: data.answer,
        sources: data.sources,
        sub_questions: data.sub_questions,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Error connecting to FinSight API. Make sure the backend is running on port 8000.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-4 flex items-center gap-3">
        <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center font-bold text-black text-sm">
          F
        </div>
        <div>
          <h1 className="text-lg font-semibold">FinSight</h1>
          <p className="text-xs text-gray-400">
            Agentic RAG · Big Tech SEC Filings · 2021–2023
          </p>
        </div>
        <div className="ml-auto flex gap-2">
          {["AAPL", "MSFT", "GOOGL", "META", "AMZN"].map((t) => (
            <span
              key={t}
              className="text-xs bg-gray-800 text-emerald-400 px-2 py-1 rounded font-mono"
            >
              {t}
            </span>
          ))}
        </div>
      </header>

      {/* Chat area */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6 max-w-4xl mx-auto w-full">
        {messages.length === 0 && (
          <div className="text-center mt-16 space-y-6">
            <h2 className="text-2xl font-semibold text-gray-200">
              Ask anything about Big Tech financials
            </h2>
            <p className="text-gray-400 text-sm">
              Powered by agentic multi-hop RAG over SEC 10-K filings
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-8">
              {SAMPLE_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => sendMessage(q)}
                  className="text-left p-4 bg-gray-900 border border-gray-700 rounded-xl hover:border-emerald-500 hover:bg-gray-800 transition text-sm text-gray-300"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-3xl w-full ${
                msg.role === "user" ? "flex justify-end" : ""
              }`}
            >
              {msg.role === "user" ? (
                <div className="bg-emerald-600 text-white px-4 py-3 rounded-2xl rounded-tr-sm max-w-xl text-sm">
                  {msg.content}
                </div>
              ) : (
                <div className="space-y-3">
                  {msg.sub_questions && msg.sub_questions.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {msg.sub_questions.map((q, j) => (
                        <span
                          key={j}
                          className="text-xs bg-gray-800 text-gray-400 px-2 py-1 rounded-full border border-gray-700"
                        >
                          {q.length > 60 ? q.slice(0, 60) + "..." : q}
                        </span>
                      ))}
                    </div>
                  )}

                  <div className="bg-gray-900 border border-gray-800 rounded-2xl rounded-tl-sm px-5 py-4 text-sm text-gray-200 leading-relaxed whitespace-pre-wrap">
                    {msg.content}
                  </div>

                  {msg.sources && msg.sources.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {msg.sources.map((s, j) => (
                        <span
                          key={j}
                          className="text-xs bg-gray-900 border border-emerald-800 text-emerald-400 px-3 py-1 rounded-full"
                        >
                          {s.company} · {s.year} · {s.doc_type}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-900 border border-gray-800 rounded-2xl px-5 py-4 text-sm text-gray-400">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce delay-200" />
                <span className="ml-2">Researching SEC filings...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-gray-800 px-4 py-4">
        <div className="max-w-4xl mx-auto flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage(input)}
            placeholder="Ask about Apple, Microsoft, Google, Meta, or Amazon..."
            className="flex-1 bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500 transition"
          />
          <button
            onClick={() => sendMessage(input)}
            disabled={loading || !input.trim()}
            className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 disabled:cursor-not-allowed text-white px-5 py-3 rounded-xl text-sm font-medium transition"
          >
            {loading ? "..." : "Ask"}
          </button>
        </div>
        <p className="text-center text-xs text-gray-600 mt-2">
          Answers grounded in SEC 10-K filings · Not financial advice
        </p>
      </div>
    </div>
  );
}
