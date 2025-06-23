import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/home";
import AboutPage from "./pages/about";
import StatusPage from "./pages/status-page";
import ResultPage from "./pages/result-page";
import NotFoundPage from "./pages/not-found";

export default function App() {
  return (
    <div className="bg-gray-800 min-w-screen">
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/status/:requestId" element={<StatusPage />} />
        <Route path="/result/:requestId" element={<ResultPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Router>
    </div>
  );
}
