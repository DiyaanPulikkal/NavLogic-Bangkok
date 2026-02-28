import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import { ThemeProvider, useTheme } from "./context/ThemeContext";
import Sidebar from "./components/Sidebar";
import HomePage from "./pages/HomePage";
import RoutePage from "./pages/RoutePage";
import ExplorePage from "./pages/ExplorePage";

function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { colors } = useTheme();

  return (
    <div className={`flex h-screen overflow-hidden ${colors.bg}`}>
      <Sidebar open={sidebarOpen} onToggle={() => setSidebarOpen((v) => !v)} />
      <main className="flex-1 min-w-0 overflow-hidden">
        <AnimatePresence mode="wait">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/route" element={<RoutePage />} />
            <Route path="/explore" element={<ExplorePage />} />
          </Routes>
        </AnimatePresence>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <AppLayout />
      </ThemeProvider>
    </BrowserRouter>
  );
}
