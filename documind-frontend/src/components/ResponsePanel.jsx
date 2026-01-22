import React from "react";

export default function ResponsePanel({ loading, streamingText, response, copied, onCopy }) {
  if (!loading && !response) return null;

  return (
    <div className="mt-6 bg-white shadow-lg rounded-xl p-6">
      <div className="flex justify-between items-center mb-3">
        <h3 className="font-bold text-lg">Answer</h3>
        {!loading && (
          <button
            onClick={onCopy}
            className="px-3 py-1 rounded-lg text-sm bg-gray-100 hover:bg-gray-200 transition"
          >
            {copied ? "✓ Copied" : "Copy"}
          </button>
        )}
      </div>
      <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded-lg max-h-96 overflow-y-auto font-mono">
        {loading ? streamingText + "▌" : response}
      </pre>
    </div>
  );
}
