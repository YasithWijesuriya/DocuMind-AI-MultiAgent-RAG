import React from "react";
import AskForm from "./components/AskForm";

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex flex-col">
      <header className="sticky top-0 z-50 bg-white shadow-md border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-6 flex flex-col sm:flex-row items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg shadow-md">
              <svg
                className="h-6 w-6 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <div className="flex flex-col">
              <h1 className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-blue-600 via-blue-700 to-blue-800 bg-clip-text text-transparent">
                DOC-MIND
              </h1>
              <p className="text-sm text-gray-500 font-medium">
                AI Document Question Answering System
              </p>
            </div>
          </div>

          <div className="mt-3 sm:mt-0 flex items-center gap-2 px-3 py-1.5 bg-green-50 rounded-full border border-green-200">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm font-medium text-green-700">System Ready</span>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-3xl mx-auto px-6 py-10 w-full">
        <AskForm />
      </main>

      <footer className="bg-black border-t border-gray-200">
        <div className="max-w-2xl mx-auto px-6 py-6 text-center text-white text-sm">
          <hr className="mb-3 border-gray-400" />
          <p>© 2026 DOC-MIND. Powered by LangGraph & Advanced RAG.</p>
        </div>
      </footer>
    </div>
  );
}
