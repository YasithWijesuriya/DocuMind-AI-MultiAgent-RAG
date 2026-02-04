import React, { useState, useRef, useEffect } from "react";
import FileUploadZone from "./FileUploadZone";
import ResponsePanel from "./ResponsePanel";
import LoadingSpinner from "./LoadingSpinner";
import { 
  FiSend, 
  FiX, 
  FiFileText, 
  FiList,
  FiKey,
  FiInfo,
  FiZap,
  FiBarChart2,
  FiCheck
} from "react-icons/fi";

const SAMPLE_QUESTIONS = [
  {
    id: 1,
    text: "What this document about?",
    icon: FiFileText,
    category: "Overview"
  },
  {
    id: 2,
    text: "What are the main topics covered?",
    icon: FiList,
    category: "Content"
  },
  {
    id: 3,
    text: "What is the key information?",
    icon: FiKey,
    category: "Key Points"
  },
  {
    id: 4,
    text: "Can you explain the important details?",
    icon: FiInfo,
    category: "Details"
  },
  {
    id: 5,
    text: "What should I know from this document?",
    icon: FiZap,
    category: "Essential"
  },
  {
    id: 6,
    text: "Provide a detailed analysis of this document",
    icon: FiBarChart2,
    category: "Analysis"
  }
];

export default function AskForm() {
  const [files, setFiles] = useState([]);
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const [copied, setCopied] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [showSampleQuestions, setShowSampleQuestions] = useState(true);
  const responseEndRef = useRef(null);

  // Auto-scroll to bottom when response updates
  useEffect(() => {
    responseEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [streamingText, response]);

  const handleFileChange = (e) => {
    const newFiles = Array.from(e.target.files || []);
    setFiles((prevFiles) => {
      const combined = [...prevFiles, ...newFiles];
      return combined.slice(-5); // Limit to 5 files
    });
  };

  const removeFile = (index) => {
    setFiles((prevFiles) => prevFiles.filter((_, i) => i !== index));
  };

  const handleSampleQuestionClick = (questionText) => {
    setQuestion(questionText);
    setSelectedQuestion(questionText);
    setShowSampleQuestions(false);
    // Auto-submit after selecting
    setTimeout(() => {
      handleSubmit(null, questionText);
    }, 100);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { 
      e.preventDefault(); 
      handleSubmit(e); 
    }
  };

  const handleSubmit = async (e, questionText = null) => {
    if (e) e.preventDefault();

    const finalQuestion = questionText || question;

    if (!finalQuestion.trim()) {
      alert("Please enter a question");
      return;
    }

    if (files.length === 0) {
      alert("Please upload at least one PDF file");
      return;
    }

    setLoading(true);
    setResponse("");
    setStreamingText("");
    setSelectedQuestion(finalQuestion);
    setShowSampleQuestions(false);

    const formData = new FormData();
    formData.append("question", finalQuestion);

    files.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response = await fetch("https://web-production-d725e.up.railway.app/ask", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Network response was not ok");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullResponse = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.trim()) {
            try {
              const json = JSON.parse(line);

              if (json.type === "text") {
                fullResponse += json.content;
                setStreamingText(fullResponse);
              } else if (json.type === "complete") {
                fullResponse = json.content;
                setResponse(fullResponse);
                setStreamingText("");
              } else if (json.type === "error") {
                console.error("Error:", json.content);
                setResponse(`Error: ${json.content}`);
              }
            } catch (e) {
              // Ignore JSON parse errors for incomplete lines
            }
          }
        }
      }
    } catch (error) {
      console.error("Error:", error);
      setResponse(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    const text = response || streamingText;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const fileNames =
    files.length > 0
      ? files.map((f) => f.name).join(", ")
      : "No files selected";

  return (
    <div className="max-w-7xl mx-auto">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 flex flex-col gap-4">
          <div className="flex flex-col gap-3">
            
              <FileUploadZone
                onFileChange={handleFileChange}
                disabled={loading}
                fileCount={files.length}
                fileNames={fileNames}
              />

            {files.length > 0 && (
              <div className="p-4 bg-gradient-to-r from-emerald-900/40 to-teal-900/40 rounded-2xl border border-emerald-600/50 backdrop-blur-sm">
                <div className="flex items-start gap-3">
                  <div className="text-emerald-400 flex-shrink-0 mt-0.5">
                    <FiCheck size={20} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-emerald-100">
                      {files.length} File{files.length !== 1 ? "s" : ""} Selected
                    </p>
                    <div className="mt-2 space-y-1">
                      {files.map((file, index) => (
                        <div
                          key={index}
                          className="flex items-center justify-between p-2 bg-gray-700/50 rounded-lg hover:bg-gray-600/50 transition-colors group"
                        >
                          <span className="text-xs text-emerald-200 truncate flex-1 font-mono">
                            {file.name}
                          </span>
                          <button
                            onClick={() => removeFile(index)}
                            disabled={loading}
                            className="ml-2 text-gray-400 hover:text-red-400 disabled:opacity-50 transition-colors opacity-0 group-hover:opacity-100"
                            title="Remove file"
                          >
                            <FiX size={14} />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          <form onSubmit={handleSubmit} className="flex flex-col gap-3">
            <label className="text-sm font-bold text-gray-100 flex items-center gap-2">
              <FiFileText className="w-4 h-4" />
              Your Question
            </label>
            <div className="relative">
              <textarea
                value={question}
                onChange={(e) => {
                  setQuestion(e.target.value);
                  setShowSampleQuestions(false);
                }}
                onKeyDown={handleKeyDown}
                placeholder="Ask a question about your document..."
                disabled={loading}
                rows="5"
                className="w-full p-4 bg-gray-800 border border-gray-600 rounded-xl text-gray-100 placeholder-gray-500
                         focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500
                         disabled:opacity-50 resize-none"
              />
              <button
                type="submit"
                disabled={loading || !question.trim() || files.length === 0}
                className="absolute bottom-3 right-3 p-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600
                         text-white rounded-lg transition-colors disabled:cursor-not-allowed"
                title="Send question"
              >
                <FiSend size={20} />
              </button>
            </div>
          </form>
        </div>

        {/* Right Panel - Sample Questions & Response */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          {/* Sample Questions */}
          {showSampleQuestions && !loading && !response && files.length > 0 && (
            <div className="animate-fade-in">
              <h3 className="text-lg font-bold text-gray-100 mb-4 flex items-center gap-2">
                Try these questions:
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {SAMPLE_QUESTIONS.map((sq) => {
                  const IconComponent = sq.icon;
                  return (
                    <button
                      key={sq.id}
                      onClick={() => handleSampleQuestionClick(sq.text)}
                      disabled={loading}
                      className="p-4 bg-gray-800 border border-gray-700 rounded-xl hover:border-green-500 
                               hover:bg-gray-700 transition-all duration-200 disabled:opacity-50
                               text-left group cursor-pointer"
                    >
                      <div className="flex items-start gap-3">
                        <div className="text-green-500 group-hover:text-green-400 transition-colors flex-shrink-0 mt-1">
                          <IconComponent size={20} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-100 group-hover:text-green-300 transition-colors">
                            {sq.text}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">{sq.category}</p>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Loading Indicator */}
          {loading && (
            <div className="h-full bg-gray-800 shadow-lg rounded-2xl p-6 flex flex-col items-center justify-center">
              <LoadingSpinner message="Analyzing your document..." />
            </div>
          )}

          {/* Response Panel */}
          {(response || streamingText) && (
            <>
              <ResponsePanel
                loading={loading}
                streamingText={streamingText}
                response={response}
                copied={copied}
                onCopy={handleCopy}
              />
              <div ref={responseEndRef} />
            </>
          )}

          {/* Empty State */}
          {!loading && !response && !streamingText && files.length === 0 && (
            <div className="h-full bg-gray-800 shadow-lg rounded-2xl p-6 flex flex-col items-center justify-center text-center">
              <div className="mb-4">
                <FiFileText className="w-16 h-16 text-gray-600 mx-auto" />
              </div>
              <h3 className="text-xl font-bold text-gray-100 mb-2">
                Get Started
              </h3>
              <p className="text-gray-400 max-w-md">
                Upload a PDF file and ask any question about its content. 
                Our AI will analyze it and provide detailed answers.
              </p>
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .animate-fade-in {
          animation: fadeIn 0.5s ease-out;
        }
      `}</style>
    </div>
  );
}
