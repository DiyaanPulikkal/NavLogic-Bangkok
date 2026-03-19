import { motion, AnimatePresence } from "framer-motion";
import { useNavigate, useLocation } from "react-router-dom";
import { TrainFront } from "lucide-react";
import { useTheme } from "../context/ThemeContext";
import { useAuth } from "../context/AuthContext";
import {
  listConversations,
  deleteConversation,
  type ConversationInfo,
} from "../api/client";
import { useState, useEffect, useCallback } from "react";

interface Props {
  open: boolean;
  onToggle: () => void;
  conversations: ConversationInfo[];
  activeConversationId: number | null;
  onSelectConversation: (id: number | null) => void;
  onConversationsChange: () => void;
}

export default function Sidebar({
  open,
  onToggle,
  conversations,
  activeConversationId,
  onSelectConversation,
  onConversationsChange,
}: Props) {
  const navigate = useNavigate();
  const location = useLocation();
  const { theme, colors, toggle } = useTheme();
  const { logout, isAuthenticated } = useAuth();

  async function handleDelete(id: number, e: React.MouseEvent) {
    e.stopPropagation();
    await deleteConversation(id);
    if (activeConversationId === id) {
      onSelectConversation(null);
    }
    onConversationsChange();
  }

  return (
    <>
      <AnimatePresence>
        {open && (
          <motion.aside
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 260, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.2, ease: "easeInOut" }}
            className={`h-screen ${colors.sidebarBg} border-r ${colors.sidebarBorder} flex flex-col overflow-hidden flex-shrink-0`}
          >
            <div className="flex items-center justify-between px-4 pt-4 pb-2">
              <span className={`font-semibold text-base whitespace-nowrap tracking-tight ${theme === "dark" ? "text-gray-100" : "text-gray-900"}`}>
                <TrainFront size={18} className="text-[#e87722] mr-1.5 inline-block" />Bangkok Transit
              </span>
              <button
                onClick={onToggle}
                className={`${colors.sidebarTextMuted} hover:${theme === "dark" ? "text-gray-300" : "text-gray-700"} transition-colors bg-transparent border-none cursor-pointer p-1`}
                title="Close sidebar"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="3" width="18" height="18" rx="3" />
                  <line x1="9" y1="3" x2="9" y2="21" />
                </svg>
              </button>
            </div>

            <nav className="flex-1 px-2 py-3 space-y-0.5 overflow-y-auto">
              <SidebarButton
                icon={
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="12" y1="5" x2="12" y2="19" />
                    <line x1="5" y1="12" x2="19" y2="12" />
                  </svg>
                }
                label="New chat"
                onClick={() => {
                  onSelectConversation(null);
                  if (location.pathname !== "/") navigate("/");
                }}
              />
              <SidebarButton
                icon={
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="11" cy="11" r="8" />
                    <line x1="21" y1="21" x2="16.65" y2="16.65" />
                  </svg>
                }
                label="Explore stations"
                onClick={() => navigate("/explore")}
                active={location.pathname === "/explore"}
              />

              {/* Conversation list */}
              {conversations.length > 0 && (
                <div className="mt-4 pt-3 border-t border-current/10">
                  <p className={`px-3 pb-2 text-xs font-medium ${colors.sidebarTextMuted} uppercase tracking-wide`}>
                    History
                  </p>
                  {conversations.map((conv) => (
                    <button
                      key={conv.id}
                      onClick={() => {
                        onSelectConversation(conv.id);
                        if (location.pathname !== "/") navigate("/");
                      }}
                      className={`w-full flex items-center justify-between gap-2 px-3 py-2 rounded-lg text-sm transition-colors
                                  bg-transparent border-none cursor-pointer text-left group
                                  ${activeConversationId === conv.id
                                    ? `${colors.sidebarActive} ${colors.text}`
                                    : `${colors.sidebarText} ${colors.sidebarHover}`}`}
                    >
                      <span className="truncate flex-1">{conv.title}</span>
                      <span
                        onClick={(e) => handleDelete(conv.id, e)}
                        className={`opacity-0 group-hover:opacity-100 ${colors.sidebarTextMuted} hover:text-red-400 transition-opacity cursor-pointer`}
                        title="Delete"
                      >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <line x1="18" y1="6" x2="6" y2="18" />
                          <line x1="6" y1="6" x2="18" y2="18" />
                        </svg>
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </nav>

            {/* Theme toggle + footer */}
            <div className={`px-3 py-3 border-t ${colors.sidebarBorder} space-y-2`}>
              <button
                onClick={toggle}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors
                            bg-transparent border-none cursor-pointer text-left ${colors.sidebarText} ${colors.sidebarHover}`}
              >
                {theme === "dark" ? (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="5" />
                    <line x1="12" y1="1" x2="12" y2="3" />
                    <line x1="12" y1="21" x2="12" y2="23" />
                    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
                    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
                    <line x1="1" y1="12" x2="3" y2="12" />
                    <line x1="21" y1="12" x2="23" y2="12" />
                    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
                    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
                  </svg>
                ) : (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
                  </svg>
                )}
                <span className="whitespace-nowrap">{theme === "dark" ? "Light mode" : "Dark mode"}</span>
              </button>
              {isAuthenticated && (
                <button
                  onClick={logout}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors
                              bg-transparent border-none cursor-pointer text-left ${colors.sidebarText} ${colors.sidebarHover}`}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                    <polyline points="16 17 21 12 16 7" />
                    <line x1="21" y1="12" x2="9" y2="12" />
                  </svg>
                  <span className="whitespace-nowrap">Sign out</span>
                </button>
              )}
              <p className={`text-xs px-3 ${colors.sidebarTextMuted}`}>Bangkok Public Transport</p>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {!open && (
        <button
          onClick={onToggle}
          className={`fixed top-3 left-3 z-50 transition-colors
                     ${theme === "dark" ? "text-gray-500 hover:text-gray-300 bg-[#1a1a1a]/80 border-[#2a2a2a]" : "text-gray-400 hover:text-gray-700 bg-white/80 border-gray-200"}
                     backdrop-blur border rounded-lg p-2 cursor-pointer`}
          title="Open sidebar"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="3" width="18" height="18" rx="3" />
            <line x1="9" y1="3" x2="9" y2="21" />
          </svg>
        </button>
      )}
    </>
  );
}

function SidebarButton({
  icon,
  label,
  onClick,
  active = false,
}: {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  active?: boolean;
}) {
  const { colors } = useTheme();

  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors
                  bg-transparent border-none cursor-pointer text-left
                  ${active ? `${colors.sidebarActive} ${colors.text}` : `${colors.sidebarText} ${colors.sidebarHover}`}`}
    >
      {icon}
      <span className="whitespace-nowrap">{label}</span>
    </button>
  );
}
