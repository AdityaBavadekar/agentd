import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  AlertCircle,
  CheckCircle2,
  Clock,
  ArrowLeft,
  Eye,
  Send,
  Loader2,
  XCircle,
  MessageCircle,
  ChevronDown,
  ChevronUp
} from "lucide-react";
import { getSessionStatus, postSessionAnswer } from "../utils";
import type { PipelineSessionStatus } from "../types";
import MarkdownBlock from "../components/markdown";

function ShowHideComponent({ previousUpdates }: { previousUpdates: [] }) {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
      <button
        onClick={() => setIsVisible(!isVisible)}
        className="flex items-center justify-between w-full text-left text-gray-200 hover:text-white transition-colors"
      >
        <span className="font-medium">Show previous updates</span>
        {isVisible ? (
          <ChevronUp className="h-4 w-4 ml-2" />
        ) : (
          <ChevronDown className="h-4 w-4 ml-2" />
        )}
      </button>

      {isVisible && (
        <div className="mt-4 space-y-3 border-t border-gray-700 pt-4">
          {previousUpdates.map((update, index) => (
            <div key={index} className="bg-gray-700 rounded-lg p-3">
              <p className="text-gray-300 text-sm">
                <MarkdownBlock text={update} />
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function StatusPage() {
  const { requestId } = useParams();
  const [status, setStatus] = useState<PipelineSessionStatus | null>(null);
  const [pageStatus, setPageStatus] = useState<"loading" | "error" | "success">("loading");
  const [error, setError] = useState<string | null>(null);
  const [userAnswer, setUserAnswer] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const interval = setInterval(async () => {
      const res = await fetch(getSessionStatus(requestId || ""));
      const data = await res.json();
      if (res.ok) {
        setPageStatus("success");
        setStatus(data);
        if (data.pipeline_status === "completed") {
          clearInterval(interval);
        }
      } else {
        clearInterval(interval);
        setPageStatus("error");
        setError(data.message || "Failed to fetch reuqest status");
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [requestId, navigate]);

  const handleSubmitAnswer = async () => {
    if (!userAnswer.trim()) {
      alert("Please enter a solution.");
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await fetch(postSessionAnswer(requestId || ""), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answer: userAnswer }),
      });
      const data = await res.json();
      if (!res.ok) {
        alert(data.message || "Failed to submit choice");
      } else {
        setUserAnswer("");
      }
    } catch (err) {
      alert("Failed to submit answer. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (pageStatus === "error") {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-gray-800 rounded-lg shadow-xl p-6 border border-gray-700">
          <div className="flex items-center mb-4">
            <XCircle className="h-8 w-8 text-red-400 mr-3" />
            <h1 className="text-2xl font-bold text-white">Error</h1>
          </div>
          <p className="text-gray-300 mb-6">{error}</p>
          <button
            onClick={() => navigate("/")}
            className="w-full bg-gray-700 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center border border-gray-600"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Go Back
          </button>
        </div>
      </div>
    );
  }

  if (pageStatus === "loading" || !status) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
        <div className="text-center">
          <Loader2 className="h-12 w-12 text-blue-400 animate-spin mx-auto mb-4" />
          <p className="text-lg text-gray-300">Loading reuqest status...</p>
        </div>
      </div>
    );
  }

  if (status.pipeline_status === "failed") {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
        <div className="max-w-2xl w-full bg-gray-800 rounded-lg shadow-xl p-6 border border-gray-700">
          <div className="flex items-center mb-6">
            <AlertCircle className="h-8 w-8 text-red-400 mr-3" />
            <h1 className="text-2xl font-bold text-white">Reuqest Failed</h1>
          </div>

          <div className="space-y-4 mb-6">
            <div className="bg-red-900/50 border border-red-700 rounded-lg p-4">
              <p className="text-red-200 font-medium">Error: {status.error}</p>
            </div>

            {status.update && (
              <div className="bg-gray-700 border border-gray-600 rounded-lg p-4">
                <p className="text-gray-200">
                  <MarkdownBlock text={status.update} />
                </p>
              </div>
            )}

            <p className="text-sm text-gray-400">
              Last Update: {new Date(status.updated_at).toLocaleString()}
            </p>
          </div>

          <button
            onClick={() => navigate("/")}
            className="w-full bg-gray-700 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center border border-gray-600"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Go Back
          </button>
        </div>
      </div>
    );
  }

  if (status.pipeline_status === "completed") {
    return (
      <div className="min-h-screen bg-gray-900 py-8 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-gray-800 rounded-lg shadow-xl p-6 mb-6 border border-gray-700">
            <div className="flex items-center mb-6">
              <CheckCircle2 className="h-8 w-8 text-green-400 mr-3" />
              <h1 className="text-2xl font-bold text-white">Reuqest Completed</h1>
            </div>

            <div className="bg-green-900/50 border border-green-700 rounded-lg p-4 mb-6">
              <h3 className="text-lg font-semibold text-green-200 mb-2">
                Congratulations! Your reuqest has completed successfully.
              </h3>
              <p className="text-green-300">Here are the results:</p>
            </div>

            <div className="bg-gray-700 border border-gray-600 rounded-lg p-4 mb-6">
              {status.agent_updates.map((update, index) => (
                <div key={index} className="mb-4">
                  <h4 className="text-sm font-medium text-gray-200 mb-1">
                    Agent {index + 1} Update:
                  </h4>
                  <MarkdownBlock text={update} />
                </div>
              ))
              }
            </div>

            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={() => navigate(`/result/${requestId}`)}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center border border-blue-500"
              >
                <Eye className="h-4 w-4 mr-2" />
                View Detailed Results
              </button>
              <button
                onClick={() => navigate("/")}
                className="flex-1 bg-gray-700 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center border border-gray-600"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Go Back
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 py-8 px-4 w-full">
      <div className="max-w-4xl mx-auto">
        <div className="bg-gray-800 rounded-lg shadow-xl p-6 border border-gray-700">
          <div className="flex items-center mb-6">
            <Clock className="h-8 w-8 text-blue-400 mr-3" />
            <h1 className="text-2xl font-bold text-white">Reuqest Status</h1>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-blue-900/50 border border-blue-700 rounded-lg p-4">
              <p className="text-sm font-medium text-blue-200">Status</p>
              <p className="text-lg font-semibold text-blue-100 capitalize">
                {status.pipeline_status.replace(/_/g, ' ')}
              </p>
            </div>

            <div className="bg-green-900/50 border border-green-700 rounded-lg p-4">
              <p className="text-sm font-medium text-green-200">Progress</p>
              <div className="flex items-center mt-1">
                <div className="flex-1 bg-green-800 rounded-full h-2 mr-2">
                  <div
                    className="bg-green-400 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${status.progress}%` }}
                  ></div>
                </div>
                <span className="text-lg font-semibold text-green-100">
                  {status.progress}%
                </span>
              </div>
            </div>

            <div className="bg-gray-700 border border-gray-600 rounded-lg p-4">
              <p className="text-sm font-medium text-gray-200">Last Update</p>
              <p className="text-sm text-gray-400">
                {new Date(status.updated_at).toLocaleString()}
              </p>
            </div>
          </div>

          {status.agent_updates.length > 0 && (
            <div className="mb-4">
              <ShowHideComponent previousUpdates={status.agent_updates} />
            </div>
          )}


          {status.update && (
            <div className="bg-gray-700 border border-gray-600 rounded-lg p-4 mb-6">
              <h3 className="font-medium text-white mb-2">Current Update:</h3>
              <p className="text-gray-300">
                <MarkdownBlock text={status.update} />
              </p>
            </div>
          )}

          {status.pipeline_status === "waiting_for_input" && (
            <div className="bg-yellow-900/50 border border-yellow-700 rounded-lg p-6">
              <div className="flex items-center mb-4">
                <MessageCircle className="h-6 w-6 text-yellow-400 mr-2" />
                <h2 className="text-lg font-semibold text-yellow-100">
                  Agent is waiting for your input (Plrease refer to last update in previous updates for context)
                </h2>
              </div>

              <div className="mb-4">
                <p className="text-yellow-200 mb-2">The agent is asking:</p>
                <div className="bg-gray-800 border border-yellow-700 rounded p-3">
                  <p className="text-gray-100">{status.update}</p>
                </div>
              </div>

              <div className="space-y-3">
                <label className="block text-sm font-medium text-yellow-100">
                  Your answer:
                </label>
                <textarea
                  value={userAnswer}
                  onChange={(e) => setUserAnswer(e.target.value)}
                  placeholder="Type your answer here..."
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-600 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 placeholder-gray-400"
                  rows={3}
                />
                <button
                  onClick={handleSubmitAnswer}
                  disabled={isSubmitting || !userAnswer.trim()}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center border border-blue-500 disabled:border-gray-500"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Submitting...
                    </>
                  ) : (
                    <>
                      <Send className="h-4 w-4 mr-2" />
                      Submit Answer
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}