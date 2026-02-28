import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { postQuery, type QueryResponse } from "../api/client";
import { useTheme } from "../context/ThemeContext";
import RouteSteps from "../components/RouteSteps";
import type { RouteData, RouteStep } from "../types";

interface Message {
  role: "user" | "assistant";
  content: string;
  response?: QueryResponse;
}

const suggestions = [
  { icon: "🚆", text: "Siam to Chatuchak" },
  { icon: "🏛", text: "What's near Grand Palace?" },
  { icon: "🗺", text: "What line is Mo Chit on?" },
  { icon: "🔄", text: "Asok to Siam" },
];

export default function HomePage() {
  const { theme, colors } = useTheme();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const hasMessages = messages.length > 0 || loading;

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function sendMessage(text: string) {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: trimmed }]);
    setLoading(true);

    try {
      const res = await postQuery(trimmed);
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

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    sendMessage(input);
  }

  return (
    <div className={`h-screen flex flex-col ${colors.bg} overflow-hidden`}>
      {/* Empty state */}
      {!hasMessages && (
        <div className="flex-1 flex flex-col items-center justify-center px-4">
          <motion.div
            className="text-center mb-8"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            <h1 className={`text-3xl font-semibold ${colors.text} mb-1`}>
              <span className="text-orange-400 mr-2">✳</span>
              Welcome to Bangkok Transit
            </h1>
          </motion.div>

          <motion.form
            onSubmit={handleSubmit}
            className="w-full max-w-2xl"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
          >
            <div className={`${colors.inputBg} rounded-2xl border ${colors.inputBorder} overflow-hidden ${theme === "light" ? "shadow-lg" : ""}`}>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="How can I help you today?"
                className={`w-full px-5 py-4 bg-transparent ${colors.text} text-base ${colors.textMuted} placeholder-current
                           focus:outline-none border-none`}
                style={{ caretColor: theme === "dark" ? "white" : "black" }}
              />
              <div className="flex items-center justify-end px-4 pb-3">
                <button
                  type="submit"
                  disabled={loading || !input.trim()}
                  className={`p-2 rounded-lg bg-transparent ${colors.bgTertiary.replace("bg-", "hover:bg-")} disabled:opacity-30
                             ${colors.textMuted} transition-colors border-none cursor-pointer`}
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94l18.04-8.01a.75.75 0 000-1.36L3.478 2.405z" />
                  </svg>
                </button>
              </div>
            </div>
          </motion.form>

          <motion.div
            className="flex flex-wrap justify-center gap-2 mt-4 max-w-2xl"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.4, delay: 0.25 }}
          >
            {suggestions.map((s) => (
              <button
                key={s.text}
                onClick={() => sendMessage(s.text)}
                className={`flex items-center gap-2 px-4 py-2 rounded-full border
                           ${colors.inputBg} ${colors.inputBorder} ${colors.textSecondary}
                           text-sm ${colors.bgTertiary.replace("bg-", "hover:bg-")} hover:${theme === "dark" ? "text-white" : "text-gray-900"}
                           transition-colors cursor-pointer`}
              >
                <span>{s.icon}</span>
                <span>{s.text}</span>
              </button>
            ))}
          </motion.div>
        </div>
      )}

      {/* Chat mode */}
      {hasMessages && (
        <>
          <div className="flex-1 overflow-y-auto">
            <div className="max-w-2xl mx-auto px-4 py-6 space-y-5">
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
                          ? `${colors.userBubble} ${colors.userBubbleText}`
                          : `${colors.assistantBubble} border ${colors.assistantBubbleBorder} ${colors.assistantBubbleText} ${theme === "light" ? "shadow-sm" : ""}`
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
                  <div className={`${colors.assistantBubble} border ${colors.assistantBubbleBorder} rounded-2xl px-4 py-3`}>
                    <motion.div
                      className="flex gap-1.5"
                      initial={{ opacity: 0.5 }}
                      animate={{ opacity: 1 }}
                      transition={{ repeat: Infinity, repeatType: "reverse", duration: 0.6 }}
                    >
                      <span className={`w-2 h-2 ${theme === "dark" ? "bg-gray-500" : "bg-gray-300"} rounded-full`} />
                      <span className={`w-2 h-2 ${theme === "dark" ? "bg-gray-500" : "bg-gray-300"} rounded-full`} />
                      <span className={`w-2 h-2 ${theme === "dark" ? "bg-gray-500" : "bg-gray-300"} rounded-full`} />
                    </motion.div>
                  </div>
                </motion.div>
              )}

              <div ref={bottomRef} />
            </div>
          </div>

          <div className="px-4 pb-4 pt-2">
            <form onSubmit={handleSubmit} className="max-w-2xl mx-auto">
              <div className={`${colors.inputBg} rounded-2xl border ${colors.inputBorder} overflow-hidden ${theme === "light" ? "shadow-lg" : ""}`}>
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask about Bangkok transit..."
                  className={`w-full px-5 py-4 bg-transparent ${colors.text} text-base ${colors.textMuted} placeholder-current
                             focus:outline-none border-none`}
                  style={{ caretColor: theme === "dark" ? "white" : "black" }}
                  disabled={loading}
                />
                <div className="flex items-center justify-end px-4 pb-3">
                  <button
                    type="submit"
                    disabled={loading || !input.trim()}
                    className={`p-2 rounded-lg bg-transparent ${colors.bgTertiary.replace("bg-", "hover:bg-")} disabled:opacity-30
                               ${colors.textMuted} transition-colors border-none cursor-pointer`}
                  >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94l18.04-8.01a.75.75 0 000-1.36L3.478 2.405z" />
                    </svg>
                  </button>
                </div>
              </div>
            </form>
          </div>
        </>
      )}
    </div>
  );
}

function RouteResult({ data }: { data: RouteData }) {
  const { colors } = useTheme();
  return (
    <div>
      <p className={`text-sm font-medium ${colors.text} mb-1`}>
        {data.from} → {data.to}
      </p>
      <p className={`text-xs ${colors.textMuted} mb-3`}>~{data.total_time} min</p>
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
  return "";
}
