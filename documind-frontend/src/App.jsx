import React from "react";
import AskForm from "./components/AskForm";

export default function App() {
  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex flex-col">
           
      <header className="sticky top-0 z-50 bg-gray-800 shadow-md border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-6 py-6 flex flex-col sm:flex-row items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-gray-700 rounded-lg shadow-md">
              <svg
                className="h-8 w-8 text-green-500"
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
              <h1 className="text-3xl sm:text-3xl font-bold text-white">
                <span className="text-green-600">DOCU</span>-MIND
              </h1>
              <p className="text-sm text-gray-400 font-medium">
                AI Document Question Answering System
              </p>
            </div>
          </div>

          <div className="mt-3 sm:mt-0 flex items-center gap-3 px-4 py-2 bg-gray-800 border border-gray-600 rounded-full shadow-inner shadow-black/20 relative">
  
  <span className="relative flex">
    <span className="absolute inline-flex h-3 w-3 rounded-full bg-green-400 opacity-50 animate-ping"></span>
    <span className="relative inline-flex h-3 w-3 rounded-full bg-green-400"></span>
  </span>

  <span className="text-sm font-medium text-gray-100">
    System Ready
  </span>

  <span className="absolute -top-1 -right-2 h-2 w-2 bg-green-300 rounded-full blur-md opacity-30"></span>
</div>
        </div>
      </header>

      <main className="flex-1 w-full px-4 lg:px-10 py-6">
        <AskForm />
      </main>

      <footer className="bg-gray-800 shadow-md border-t border-gray-700">
        <div className="max-w-2xl mx-auto px-6 py-6 font-bold text-center text-sm text-gray-400">
          <hr className="mb-3 border-gray-700" />
          <p>© 2026 DOCU-MIND. Powered by LangGraph & Advanced RAG.</p>
        </div>
      </footer>
    </div>
  );
}
