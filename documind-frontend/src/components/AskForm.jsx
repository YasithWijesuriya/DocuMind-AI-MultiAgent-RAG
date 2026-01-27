import React, { useState } from "react";
import FileUploadZone from "./FileUploadZone";
import ResponsePanel from "./ResponsePanel";
import LoadingSpinner from "./LoadingSpinner";

export default function AskForm() {
  const [question, setQuestion] = useState("");
  const [files, setFiles] = useState([]);
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const [fileNames, setFileNames] = useState("");
  const [copied, setCopied] = useState(false);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFiles(e.target.files);
      setFileNames(Array.from(e.target.files).map(f => f.name).join(", "));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim() || files.length === 0) return;

    setLoading(true);
    setResponse("");
    setStreamingText("");

    const formData = new FormData();
    formData.append("question", question);
    Array.from(files).forEach(file => formData.append("files", file));

    try {
      const res = await fetch("http://localhost:8000/ask", {
        method: "POST",
        body: formData,
      });

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let full = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n").filter(Boolean);

        for (const line of lines) {
          const data = JSON.parse(line);
          if (data.type === "text") {
            setStreamingText(prev => prev + data.content);
            full += data.content;
          }
          if (data.type === "complete") {
            full = data.content;
          }
        }
      }
      setResponse(full);
    } catch (err) {
      setResponse("Error occurred");
    }
    setLoading(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { 
      e.preventDefault(); 
      handleSubmit(e); 
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">
      {/* LEFT PANEL */}
      <div className="bg-gray-800 rounded-2xl shadow-lg p-6 space-y-6 animate-fade-in">
        <FileUploadZone
          onFileChange={handleFileChange}
          disabled={loading}
          fileCount={files.length}
          fileNames={fileNames}
        />

        <form onSubmit={handleSubmit} className="space-y-4">
          <textarea
            placeholder="Ask questions from your documents..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
            rows={6}
            className="w-full rounded-xl border border-gray-600 bg-gray-700 px-4 py-3
                      focus:ring-2 focus:ring-gray-400 outline-none
                      transition resize-none text-gray-100 placeholder-gray-400"
          />

          <button
            disabled={loading || !question.trim() || files.length === 0}
            className={`w-full flex justify-center items-center gap-2 text-gray-100 font-semibold py-3 rounded-xl transition-all duration-300
              ${!question.trim() || files.length === 0
                ? "bg-gray-700 cursor-not-allowed text-gray-400"
                : "bg-gray-700 text-green-400 hover:bg-gray-600 hover:scale-[1.02]"
              }`}
          >
            {loading ? <LoadingSpinner /> : "Ask from DOCU-MIND"}
          </button>
        </form>
      </div>

      {/* RIGHT PANEL */}
      <div className="lg:sticky lg:top-28 h-fit">
        <ResponsePanel
          loading={loading}
          streamingText={streamingText}
          response={response}
          copied={copied}
          onCopy={() => {
            navigator.clipboard.writeText(response);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
          }}
        />
      </div>
    </div>

  );
}
