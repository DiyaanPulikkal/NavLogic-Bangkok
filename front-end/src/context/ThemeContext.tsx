import { createContext, useContext, useState, useEffect } from "react";

type Theme = "light" | "dark";

interface ThemeColors {
  bg: string;
  bgSecondary: string;
  bgTertiary: string;
  border: string;
  borderHover: string;
  text: string;
  textSecondary: string;
  textMuted: string;
  inputBg: string;
  inputBorder: string;
  userBubble: string;
  userBubbleText: string;
  assistantBubble: string;
  assistantBubbleBorder: string;
  assistantBubbleText: string;
  sidebarBg: string;
  sidebarBorder: string;
  sidebarText: string;
  sidebarTextMuted: string;
  sidebarHover: string;
  sidebarActive: string;
  cardBg: string;
  cardBorder: string;
  cardHover: string;
  headerBg: string;
  headerBorder: string;
  transferBg: string;
  transferBorder: string;
  transferText: string;
}

const lightColors: ThemeColors = {
  bg: "bg-gray-50",
  bgSecondary: "bg-white",
  bgTertiary: "bg-gray-100",
  border: "border-gray-200",
  borderHover: "border-gray-300",
  text: "text-gray-900",
  textSecondary: "text-gray-600",
  textMuted: "text-gray-400",
  inputBg: "bg-white",
  inputBorder: "border-gray-200",
  userBubble: "bg-blue-600",
  userBubbleText: "text-white",
  assistantBubble: "bg-white",
  assistantBubbleBorder: "border-gray-100",
  assistantBubbleText: "text-gray-800",
  sidebarBg: "bg-gray-100",
  sidebarBorder: "border-gray-200",
  sidebarText: "text-gray-700",
  sidebarTextMuted: "text-gray-400",
  sidebarHover: "hover:bg-gray-200",
  sidebarActive: "bg-gray-200",
  cardBg: "bg-white",
  cardBorder: "border-gray-100",
  cardHover: "hover:border-gray-300",
  headerBg: "bg-white",
  headerBorder: "border-gray-100",
  transferBg: "bg-amber-50",
  transferBorder: "border-amber-200",
  transferText: "text-amber-800",
};

const darkColors: ThemeColors = {
  bg: "bg-[#212121]",
  bgSecondary: "bg-[#2f2f2f]",
  bgTertiary: "bg-[#3a3a3a]",
  border: "border-[#3a3a3a]",
  borderHover: "border-[#4a4a4a]",
  text: "text-white",
  textSecondary: "text-gray-300",
  textMuted: "text-gray-500",
  inputBg: "bg-[#2f2f2f]",
  inputBorder: "border-[#3a3a3a]",
  userBubble: "bg-[#3a3a3a]",
  userBubbleText: "text-white",
  assistantBubble: "bg-[#2f2f2f]",
  assistantBubbleBorder: "border-[#3a3a3a]",
  assistantBubbleText: "text-gray-200",
  sidebarBg: "bg-[#1a1a1a]",
  sidebarBorder: "border-[#2a2a2a]",
  sidebarText: "text-gray-400",
  sidebarTextMuted: "text-gray-600",
  sidebarHover: "hover:bg-[#252525]",
  sidebarActive: "bg-[#2a2a2a]",
  cardBg: "bg-[#2f2f2f]",
  cardBorder: "border-[#3a3a3a]",
  cardHover: "hover:border-[#4a4a4a]",
  headerBg: "bg-[#1a1a1a]",
  headerBorder: "border-[#2a2a2a]",
  transferBg: "bg-amber-900/30",
  transferBorder: "border-amber-700/40",
  transferText: "text-amber-300",
};

interface ThemeContextValue {
  theme: Theme;
  colors: ThemeColors;
  toggle: () => void;
}

const ThemeContext = createContext<ThemeContextValue>({
  theme: "dark",
  colors: darkColors,
  toggle: () => {},
});

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => {
    const saved = localStorage.getItem("theme") as Theme | null;
    return saved ?? "dark";
  });

  useEffect(() => {
    localStorage.setItem("theme", theme);
  }, [theme]);

  const colors = theme === "dark" ? darkColors : lightColors;

  return (
    <ThemeContext.Provider value={{ theme, colors, toggle: () => setTheme((t) => (t === "dark" ? "light" : "dark")) }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  return useContext(ThemeContext);
}
