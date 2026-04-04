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
  bg: "bg-[#f8f7f4]",
  bgSecondary: "bg-white",
  bgTertiary: "bg-gray-100",
  border: "border-gray-200",
  borderHover: "border-gray-300",
  text: "text-gray-900",
  textSecondary: "text-gray-600",
  textMuted: "text-gray-400",
  inputBg: "bg-white",
  inputBorder: "border-gray-200",
  userBubble: "bg-[#e87722]",
  userBubbleText: "text-white",
  assistantBubble: "bg-white",
  assistantBubbleBorder: "border-gray-150",
  assistantBubbleText: "text-gray-800",
  sidebarBg: "bg-[#f0eeeb]",
  sidebarBorder: "border-gray-200",
  sidebarText: "text-gray-700",
  sidebarTextMuted: "text-gray-400",
  sidebarHover: "hover:bg-gray-200/60",
  sidebarActive: "bg-gray-200/80",
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
  bg: "bg-[#191919]",
  bgSecondary: "bg-[#242424]",
  bgTertiary: "bg-[#2e2e2e]",
  border: "border-[#333]",
  borderHover: "border-[#444]",
  text: "text-gray-100",
  textSecondary: "text-gray-400",
  textMuted: "text-gray-500",
  inputBg: "bg-[#242424]",
  inputBorder: "border-[#333]",
  userBubble: "bg-[#e87722]",
  userBubbleText: "text-white",
  assistantBubble: "bg-[#242424]",
  assistantBubbleBorder: "border-[#333]",
  assistantBubbleText: "text-gray-300",
  sidebarBg: "bg-[#141414]",
  sidebarBorder: "border-[#222]",
  sidebarText: "text-gray-400",
  sidebarTextMuted: "text-gray-600",
  sidebarHover: "hover:bg-[#1e1e1e]",
  sidebarActive: "bg-[#222]",
  cardBg: "bg-[#242424]",
  cardBorder: "border-[#333]",
  cardHover: "hover:border-[#444]",
  headerBg: "bg-[#141414]",
  headerBorder: "border-[#222]",
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

// eslint-disable-next-line react-refresh/only-export-components
export function useTheme() {
  return useContext(ThemeContext);
}
