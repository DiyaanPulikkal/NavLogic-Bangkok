import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import SearchPage from "./pages/SearchPage";
import RoutePage from "./pages/RoutePage";
import ExplorePage from "./pages/ExplorePage";
import QueryPage from "./pages/QueryPage";

export default function App() {
  return (
    <BrowserRouter>
      <AnimatePresence mode="wait">
        <Routes>
          <Route path="/" element={<SearchPage />} />
          <Route path="/route" element={<RoutePage />} />
          <Route path="/explore" element={<ExplorePage />} />
          <Route path="/query" element={<QueryPage />} />
        </Routes>
      </AnimatePresence>
    </BrowserRouter>
  );
}
