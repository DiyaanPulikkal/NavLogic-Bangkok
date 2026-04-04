import { useState, useRef, useEffect, useCallback, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  TrainFront,
  Landmark,
  Map,
  ArrowLeftRight,
  Clock,
  ClipboardList,
  Loader2,
  type LucideIcon,
} from "lucide-react";
import {
  postQuery,
  createConversation,
  getConversation,
  type QueryResponse,
} from "../api/client";
import { useTheme } from "../context/ThemeContext";
import RouteSteps from "../components/RouteSteps";
import ScheduleSteps from "../components/ScheduleSteps";
import DayPlanSteps from "../components/DayPlanSteps";
import NightlifeSteps from "../components/NightlifeSteps";
import type { RouteData, RouteStep, ScheduleData, DayPlanData, NightlifeData } from "../types";

interface Message {
  role: "user" | "assistant";
  content: string;
  response?: QueryResponse;
}

const suggestions: { icon: LucideIcon; text: string; category: string }[] = [
  { icon: TrainFront, text: "Siam to Chatuchak", category: "route" },
  { icon: Landmark, text: "What's near Grand Palace?", category: "explore" },
  { icon: Map, text: "What line is Mo Chit on?", category: "info" },
  { icon: ArrowLeftRight, text: "Asok to Siam", category: "route" },
  { icon: Clock, text: "I need to get from Mo Chit to Asok by 8am", category: "schedule" },
  { icon: ClipboardList, text: "Plan my day: Mo Chit to Siam by 8am, then Asok by 10am — what to visit?", category: "plan" },
];

interface HomePageProps {
  conversationId: number | null;
  onConversationCreated: (id: number) => void;
}

export default function HomePage({ conversationId, onConversationCreated }: HomePageProps) {
  const { theme, colors } = useTheme();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const hasMessages = messages.length > 0 || loading;

  // Load messages when conversationId changes
  useEffect(() => {
    if (!conversationId) {
      setMessages([]);
      return;
    }
    let cancelled = false;
    getConversation(conversationId)
      .then((conv) => {
        if (cancelled) return;
        setMessages(
          conv.messages.map((m) => ({
            role: m.role === "user" ? "user" as const : "assistant" as const,
            content: m.content,
            response: m.response_data ?? undefined,
          }))
        );
      })
      .catch(() => {
        if (!cancelled) setMessages([]);
      });
    return () => { cancelled = true; };
  }, [conversationId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = useCallback(async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: trimmed }]);
    setLoading(true);

    try {
      let activeConvId = conversationId;

      // Auto-create conversation on first message
      if (!activeConvId) {
        const conv = await createConversation(trimmed.slice(0, 60));
        activeConvId = conv.id;
        onConversationCreated(conv.id);
      }

      const res = await postQuery(trimmed, activeConvId);
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
  }, [conversationId, loading, onConversationCreated]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    sendMessage(input);
  }

  return (
    <div className={`h-screen flex flex-col ${colors.bg} overflow-hidden`}>
      {/* Empty state — welcome */}
      {!hasMessages && (
        <div className="flex-1 flex flex-col items-center justify-center px-4">
          <motion.div
            className="text-center mb-10"
            initial={{ opacity: 0, y: -12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: [0.23, 1, 0.32, 1] }}
          >
            <div className="mb-4">
              <span className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-[#e87722]/10">
                <TrainFront size={28} className="text-[#e87722]" />
              </span>
            </div>
            <h1 className={`text-2xl font-semibold ${colors.text} tracking-tight`}>
              NavLogic - Bangkok
            </h1>
            <p className={`text-sm ${colors.textMuted} mt-1.5`}>
              Routes, schedules, and day plans across BTS, MRT & more
            </p>
          </motion.div>

          <motion.form
            onSubmit={handleSubmit}
            className="w-full max-w-xl"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.08, ease: [0.23, 1, 0.32, 1] }}
          >
            <div className={`${colors.inputBg} rounded-2xl border ${colors.inputBorder} overflow-hidden transition-shadow
                            ${theme === "light" ? "shadow-sm hover:shadow-md" : "hover:border-[#444]"}
                            focus-within:ring-2 focus-within:ring-[#e87722]/30 focus-within:border-[#e87722]/50`}>
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Where do you want to go?"
                className={`w-full px-5 py-4 bg-transparent ${colors.text} text-base placeholder:${colors.textMuted}
                           focus:outline-none border-none`}
                style={{ caretColor: "#e87722" }}
              />
              <div className="flex items-center justify-end px-4 pb-3">
                <button
                  type="submit"
                  disabled={loading || !input.trim()}
                  className={`p-2 rounded-xl transition-all border-none cursor-pointer
                             ${input.trim()
                               ? "bg-[#e87722] text-white hover:bg-[#d06a1a] scale-100"
                               : `bg-transparent ${colors.textMuted} disabled:opacity-30`
                             }`}
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="22" y1="2" x2="11" y2="13" />
                    <polygon points="22 2 15 22 11 13 2 9 22 2" />
                  </svg>
                </button>
              </div>
            </div>
          </motion.form>

          <motion.div
            className="flex flex-wrap justify-center gap-2 mt-5 max-w-xl"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            {suggestions.map((s, i) => (
              <motion.button
                key={s.text}
                onClick={() => sendMessage(s.text)}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.25 + i * 0.04, duration: 0.35 }}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-xl border
                           ${colors.inputBg} ${colors.inputBorder} ${colors.textSecondary}
                           text-[13px] leading-tight
                           hover:border-[#e87722]/40 hover:text-[#e87722]
                           active:scale-[0.97]
                           transition-all duration-150 cursor-pointer`}
              >
                <s.icon size={16} className="flex-shrink-0 opacity-70" />
                <span>{s.text}</span>
              </motion.button>
            ))}
          </motion.div>
        </div>
      )}

      {/* Chat mode */}
      {hasMessages && (
        <>
          <div className="flex-1 overflow-y-auto">
            <div className="max-w-2xl mx-auto px-4 py-6 space-y-4">
              <AnimatePresence>
                {messages.map((msg, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, ease: [0.23, 1, 0.32, 1] }}
                    className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                        msg.role === "user"
                          ? `${colors.userBubble} ${colors.userBubbleText}`
                          : `${colors.assistantBubble} border ${colors.assistantBubbleBorder} ${colors.assistantBubbleText}`
                      }`}
                    >
                      {msg.role === "assistant" && msg.response?.type === "route" ? (
                        <RouteResult data={msg.response.data as unknown as RouteData} />
                      ) : msg.role === "assistant" && msg.response?.type === "schedule" ? (
                        <ScheduleResult data={msg.response.data as unknown as ScheduleData} />
                      ) : msg.role === "assistant" && msg.response?.type === "day_plan" ? (
                        <DayPlanResult data={msg.response.data as unknown as DayPlanData} />
                      ) : msg.role === "assistant" && msg.response?.type === "nightlife" ? (
                        <NightlifeResult data={msg.response.data as unknown as NightlifeData} />
                      ) : msg.role === "assistant" ? (
                        <div className="prose-chat text-sm leading-relaxed">
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                        </div>
                      ) : (
                        <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                      )}
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>

              {loading && <LoadingIndicator />}

              <div ref={bottomRef} />
            </div>
          </div>

          {/* Chat input */}
          <div className={`px-4 pb-4 pt-2 ${theme === "dark" ? "bg-gradient-to-t from-[#191919] via-[#191919] to-transparent" : "bg-gradient-to-t from-[#f8f7f4] via-[#f8f7f4] to-transparent"}`}>
            <form onSubmit={handleSubmit} className="max-w-2xl mx-auto">
              <div className={`${colors.inputBg} rounded-2xl border ${colors.inputBorder} overflow-hidden transition-shadow
                              ${theme === "light" ? "shadow-sm" : ""}
                              focus-within:ring-2 focus-within:ring-[#e87722]/30 focus-within:border-[#e87722]/50`}>
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask about Bangkok transit..."
                  className={`w-full px-5 py-4 bg-transparent ${colors.text} text-base placeholder:${colors.textMuted}
                             focus:outline-none border-none`}
                  style={{ caretColor: "#e87722" }}
                  disabled={loading}
                />
                <div className="flex items-center justify-end px-4 pb-3">
                  <button
                    type="submit"
                    disabled={loading || !input.trim()}
                    className={`p-2 rounded-xl transition-all duration-150 border-none cursor-pointer
                               ${input.trim()
                                 ? "bg-[#e87722] text-white hover:bg-[#d06a1a]"
                                 : `bg-transparent ${colors.textMuted} disabled:opacity-30`
                               }`}
                  >
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="22" y1="2" x2="11" y2="13" />
                      <polygon points="22 2 15 22 11 13 2 9 22 2" />
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

const loadingPhrases = [
  "Checking the map...",
  "Finding the best route...",
  "Consulting the timetable...",
  "Navigating Bangkok traffic...",
  "Calculating transfers...",
  "Asking the station master...",
  "Scanning transit lines...",
  "Optimizing your journey...",
  "Crunching the schedule...",
  "Almost there...",
];

function LoadingIndicator() {
  const { colors } = useTheme();
  const phrase = useMemo(
    () => loadingPhrases[Math.floor(Math.random() * loadingPhrases.length)],
    []
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="flex justify-start"
    >
      <div className={`flex items-center gap-2.5 px-4 py-2.5 rounded-2xl ${colors.assistantBubble} border ${colors.assistantBubbleBorder}`}>
        <Loader2 size={16} className={`animate-spin ${colors.textMuted}`} />
        <span className={`text-sm ${colors.textMuted}`}>{phrase}</span>
      </div>
    </motion.div>
  );
}

function RouteResult({ data }: { data: RouteData }) {
  const { colors } = useTheme();
  return (
    <div>
      <div className={`flex items-baseline gap-2 mb-1`}>
        <p className={`text-sm font-semibold ${colors.text}`}>
          {data.from} → {data.to}
        </p>
        <span className={`text-xs ${colors.textMuted}`}>~{data.total_time} min</span>
      </div>
      <RouteSteps steps={data.steps as RouteStep[]} />
    </div>
  );
}

function ScheduleResult({ data }: { data: ScheduleData }) {
  const { colors } = useTheme();
  return (
    <div>
      {data.answer && (
        <div className={`prose-chat text-sm ${colors.text} mb-3 leading-relaxed`}>
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{data.answer}</ReactMarkdown>
        </div>
      )}
      {data.itineraries && data.itineraries.length > 0 && (
        <ScheduleSteps
          itineraries={data.itineraries}
          origin={data.origin}
          destination={data.destination}
          deadline={data.deadline}
        />
      )}
    </div>
  );
}

function DayPlanResult({ data }: { data: DayPlanData }) {
  const { colors } = useTheme();
  return (
    <div>
      {data.answer && (
        <div className={`prose-chat text-sm ${colors.text} mb-3 leading-relaxed`}>
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{data.answer}</ReactMarkdown>
        </div>
      )}
      {data.legs && data.legs.length > 0 && (
        <DayPlanSteps legs={data.legs} origin={data.origin} />
      )}
    </div>
  );
}

function NightlifeResult({ data }: { data: NightlifeData }) {
  const { colors } = useTheme();
  return (
    <div>
      {data.answer && (
        <div className={`prose-chat text-sm ${colors.text} mb-3 leading-relaxed`}>
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{data.answer}</ReactMarkdown>
        </div>
      )}
      <NightlifeSteps data={data} />
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
  if (res.type === "schedule") {
    return (res.data as { answer?: string }).answer ?? "";
  }
  if (res.type === "day_plan") {
    return (res.data as { answer?: string }).answer ?? "";
  }
  if (res.type === "nightlife") {
    return (res.data as { answer?: string }).answer ?? "";
  }
  return "";
}
