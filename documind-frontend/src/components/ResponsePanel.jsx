import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function ResponsePanel({
  loading,
  streamingText,
  response,
  copied,
  onCopy,
}) {
  if (!loading && !response) return null;

  const content = loading ? streamingText : response;

  return (
<div className="h-full bg-gray-800 shadow-lg rounded-2xl p-6 flex flex-col transition-all">
  <div className="flex justify-between items-center mb-4">
    <h2 className="text-2xl font-bold text-gray-100"> AI ANSWER </h2>
    {!loading && (
      <button
        onClick={onCopy}
        className="px-3 py-1.5 rounded-lg text-sm font-medium bg-gray-700 text-gray-100 hover:bg-gray-600"
      >
        {copied ? "✓ Copied" : "Copy"}
      </button>
    )}
  </div>

  <div className="flex-1 bg-gray-900 border border-gray-700 rounded-xl p-6 overflow-y-auto">
    <div className="prose max-w-none prose-invert text-gray-100">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {loading ? streamingText : response}
      </ReactMarkdown>
      {loading && (
        <span className="inline-flex gap-1 ml-2">
          <span className="w-1.5 h-1.5 bg-gray-100 rounded-full animate-pulse" />
          <span className="w-1.5 h-1.5 bg-gray-100 rounded-full animate-pulse delay-150" />
          <span className="w-1.5 h-1.5 bg-gray-100 rounded-full animate-pulse delay-300" />
        </span>
      )}
    </div>
  </div>
</div>
 );
}
