import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { postQuery, type QueryResponse } from "../api/client";
import { useNavigate } from "react-router-dom";
import RouteSteps from "../components/RouteSteps";
import type { RouteData, RouteStep } from "../types";

interface Message {
  role: "user" | "assistant";
  content: string;
  response?: QueryResponse;
}

export default function QueryPage() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send(e: React.FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setLoading(true);

    try {
      const res = await postQuery(text);
      const assistantMsg: Message = {
        role: "assistant",
        content: formatResponse(res),
        response: res,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Something went wrong. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-100 sticky top-0 z-40">
        <div className="max-w-2xl mx-auto px-4 py-3 flex items-center gap-3">
          <button
            onClick={() => navigate("/")}
            className="text-gray-400 hover:text-gray-700 transition-colors text-xl bg-transparent border-none cursor-pointer"
          >
            ←
          </button>
          <h1 className="text-lg font-bold text-gray-900">Ask anything</h1>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-2xl mx-auto px-4 py-6 space-y-4">
          {messages.length === 0 && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center py-16"
            >
              <p className="text-gray-400 text-lg mb-2">Ask about Bangkok transit</p>
              <div className="flex flex-wrap justify-center gap-2">
                {[
                  "How do I get from Siam to Chatuchak?",
                  "What line is Mo Chit on?",
                  "Are Asok and Nana on the same line?",
                  "What's near Grand Palace?",
                ].map((q) => (
                  <button
                    key={q}
                    onClick={() => { setInput(q); }}
                    className="text-sm px-3 py-1.5 rounded-full bg-white border border-gray-200 text-gray-600
                               hover:bg-blue-50 hover:border-blue-200 transition-colors cursor-pointer"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </motion.div>
          )}

          <AnimatePresence>
            {messages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                    msg.role === "user"
                      ? "bg-blue-600 text-white"
                      : "bg-white border border-gray-100 shadow-sm"
                  }`}
                >
                  {msg.role === "assistant" && msg.response?.type === "route" ? (
                    <RouteResult data={msg.response.data as unknown as RouteData} />
                  ) : (
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {loading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start"
            >
              <div className="bg-white border border-gray-100 shadow-sm rounded-2xl px-4 py-3">
                <motion.div
                  className="flex gap-1"
                  initial={{ opacity: 0.5 }}
                  animate={{ opacity: 1 }}
                  transition={{ repeat: Infinity, repeatType: "reverse", duration: 0.6 }}
                >
                  <span className="w-2 h-2 bg-gray-300 rounded-full" />
                  <span className="w-2 h-2 bg-gray-300 rounded-full" />
                  <span className="w-2 h-2 bg-gray-300 rounded-full" />
                </motion.div>
              </div>
            </motion.div>
          )}

          <div ref={bottomRef} />
        </div>
      </div>

      {/* Input */}
      <div className="bg-white border-t border-gray-100 sticky bottom-0">
        <form onSubmit={send} className="max-w-2xl mx-auto px-4 py-3 flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about routes, stations, attractions..."
            className="flex-1 px-4 py-2.5 rounded-xl border border-gray-200 bg-gray-50 text-sm
                       focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white
                       font-medium rounded-xl text-sm transition-colors border-none cursor-pointer"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

function RouteResult({ data }: { data: RouteData }) {
  return (
    <div>
      <p className="text-sm font-medium text-gray-900 mb-1">
        {data.from} → {data.to}
      </p>
      <p className="text-xs text-gray-400 mb-3">~{data.total_time} min</p>
      <RouteSteps steps={data.steps as RouteStep[]} />
    </div>
  );
}

function formatResponse(res: QueryResponse): string {
  if (res.type === "error") {
    return (res.data as { message: string }).message;
  }
  if (res.type === "answer") {
    return (res.data as { answer: string }).answer;
  }
  // Route type is handled visually
  return "";
}
