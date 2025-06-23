import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Play, Sparkles, Loader2, ArrowRight } from "lucide-react";
import { API_ENDPOINTS, getApiUrl } from "../utils";

export default function HomePage() {
  const [topic, setTopic] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    if (!topic.trim()) return alert("Please enter a valid topic");
    
    setIsSubmitting(true);
    try {
      const res = await fetch(getApiUrl(API_ENDPOINTS.API_RUN), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic }),
      });
      const data = await res.json();
      if (res.ok) {
        navigate(`/status/${data.request_id}`);
      } else {
        alert(data.message || "Error starting pipeline");
      }
    } catch (error) {
      alert("Network error. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-6">
            <div className="bg-blue-600 p-3 rounded-full mr-4">
              <Sparkles className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-white">
              agent<span className="text-blue-400">d</span>
            </h1>
          </div>
          
          <p className="text-xl text-gray-300 mb-2">
            AI-Powered Analysis Engine
          </p>
          <p className="text-gray-400 max-w-lg mx-auto">
            Enter any topic or idea and let our intelligent agents analyze, 
            research, and provide comprehensive insights for you.
          </p>
        </div>

        <div className="bg-gray-800 rounded-xl shadow-2xl p-8 border border-gray-700">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label 
                htmlFor="topic" 
                className="block text-sm font-medium text-gray-200 mb-3"
              >
                What would you like to analyze?
              </label>
              <div className="relative">
                <input
                  id="topic"
                  type="text"
                  placeholder="e.g., Market trends in renewable energy, Analysis of remote work productivity..."
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 placeholder-gray-400 text-lg"
                  disabled={isSubmitting}
                />
                <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                  <Play className="h-5 w-5 text-gray-400" />
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting || !topic.trim()}
              className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-gray-600 disabled:to-gray-700 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200 flex items-center justify-center text-lg shadow-lg hover:shadow-xl transform hover:scale-[1.02] disabled:transform-none"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                  Starting Analysis...
                </>
              ) : (
                <>
                  Start Analysis
                  <ArrowRight className="h-5 w-5 ml-2" />
                </>
              )}
            </button>
          </form>
        </div>

        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6 text-center">
            <div className="bg-green-600/20 p-2 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
              <Sparkles className="h-6 w-6 text-green-400" />
            </div>
            <h3 className="text-white font-semibold mb-2">Intelligent Analysis</h3>
            <p className="text-gray-400 text-sm">
              Advanced AI agents work together to provide deep insights
            </p>
          </div>

          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6 text-center">
            <div className="bg-purple-600/20 p-2 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
              <Play className="h-6 w-6 text-purple-400" />
            </div>
            <h3 className="text-white font-semibold mb-2">Real-time Processing</h3>
            <p className="text-gray-400 text-sm">
              Watch your analysis progress in real-time with live updates
            </p>
          </div>

          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6 text-center">
            <div className="bg-blue-600/20 p-2 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
              <ArrowRight className="h-6 w-6 text-blue-400" />
            </div>
            <h3 className="text-white font-semibold mb-2">Comprehensive Results</h3>
            <p className="text-gray-400 text-sm">
              Get detailed reports with actionable insights and recommendations
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}