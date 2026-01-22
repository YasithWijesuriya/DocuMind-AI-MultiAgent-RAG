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
      const names = Array.from(e.target.files).map((f) => f.name).join(", ");
      setFileNames(names);
    } else {
      setFiles([]);
      setFileNames("");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!question.trim()) {
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

    const formData = new FormData();
    formData.append("question", question);
    Array.from(files).forEach((file) => formData.append("files", file));

    try {
      const res = await fetch("http://localhost:8000/ask", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let fullResponse = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n").filter(Boolean);

        for (const line of lines) {
          try {
            const data = JSON.parse(line);
            if (data.type === "text") {
              setStreamingText((prev) => prev + data.content);
              fullResponse += data.content;
            } else if (data.type === "complete") {
              fullResponse = data.content;
            } else if (data.type === "error") {
              throw new Error(data.content);
            }
          } catch (err) {
            console.error("Stream parse error:", err);
          }
        }
      }

      setResponse(fullResponse || streamingText);
    } catch (err) {
      setResponse(`Error: ${err.message}`);
    }

    setLoading(false);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(response);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="max-w-3xl mx-auto py-8 px-4">
      {/* Form */}
      <div className="bg-white rounded-xl shadow-lg p-8 mb-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Question Input */}
          <div>
            <label className="block text-base font-semibold text-gray-900 mb-2">
              Your Question
            </label>
            <textarea
              placeholder="Ask anything about your documents..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={loading}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none placeholder-gray-400 resize-none disabled:bg-gray-50 disabled:text-gray-500 transition"
              rows={5}
            />
            <p className="text-xs text-gray-500 mt-1">{question.length} characters</p>
          </div>

          {/* File Upload */}
          <FileUploadZone
            onFileChange={handleFileChange}
            disabled={loading}
            fileCount={files.length}
            fileNames={fileNames}
          />

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || !question.trim() || files.length === 0}
            className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white font-semibold rounded-lg transition duration-200 ease-in-out"
          >
            {loading ? <LoadingSpinner message="Processing..." /> : "Ask"}
          </button>
        </form>
      </div>

      {/* Response Panel */}
      <ResponsePanel
        loading={loading}
        streamingText={streamingText}
        response={response}
        copied={copied}
        onCopy={handleCopy}
      />
    </div>
  );
}
