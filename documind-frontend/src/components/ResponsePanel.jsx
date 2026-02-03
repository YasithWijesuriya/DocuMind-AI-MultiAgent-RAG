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
      {/* Header Section */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-white tracking-tight">
          AI ANSWER
        </h2>
        {!loading && (
          <button
            onClick={onCopy}
            className="px-4 py-2 rounded-lg text-sm font-semibold bg-green-600 text-white hover:bg-green-700 transition-colors duration-200 flex items-center gap-2"
          >
            {copied ? (
              <>
                <span>✓</span>
                <span>Copied</span>
              </>
            ) : (
              <>
                <span></span>
                <span>Copy</span>
              </>
            )}
          </button>
        )}
      </div>

      <div className="flex-1 bg-gray-900 border border-gray-700 rounded-xl p-8 overflow-y-auto">
        <div className="prose prose-invert max-w-none text-gray-100 space-y-4">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              h1: ({ node, ...props }) => (
                <h1
                  {...props}
                  className="text-4xl font-bold text-white mt-8 mb-4 border-b-2 border-blue-500 pb-3"
                />
              ),
              h2: ({ node, ...props }) => (
                <h2
                  {...props}
                  className="text-2xl font-bold text-blue-300 mt-6 mb-3"
                />
              ),
              h3: ({ node, ...props }) => (
                <h3
                  {...props}
                  className="text-xl font-bold text-blue-200 mt-4 mb-2"
                />
              ),
              
              p: ({ node, ...props }) => (
                <p {...props} className="text-gray-100 leading-relaxed mb-3" />
              ),
              
              ul: ({ node, ...props }) => (
                <ul
                  {...props}
                  className="list-disc list-inside space-y-2 text-gray-100 ml-2 mb-4"
                />
              ),
              ol: ({ node, ...props }) => (
                <ol
                  {...props}
                  className="list-decimal list-inside space-y-2 text-gray-100 ml-2 mb-4"
                />
              ),
              li: ({ node, ...props }) => (
                <li {...props} className="text-gray-100 ml-2" />
              ),
              
              code: ({ node, inline, ...props }) => {
                if (inline) {
                  return (
                    <code
                      {...props}
                      className="bg-gray-800 text-orange-300 px-2 py-1 rounded text-sm font-mono border border-gray-700"
                    />
                  );
                }
                return (
                  <code
                    {...props}
                    className="block bg-gray-950 text-green-300 p-4 rounded-lg overflow-x-auto text-sm font-mono border border-gray-700 mb-4"
                  />
                );
              },
              
              blockquote: ({ node, ...props }) => (
                <blockquote
                  {...props}
                  className="border-l-4 border-blue-500 bg-gray-950 pl-4 py-2 my-4 text-gray-300 italic"
                />
              ),
              
              table: ({ node, ...props }) => (
                <table
                  {...props}
                  className="border-collapse border border-gray-700 w-full my-4"
                />
              ),
              thead: ({ node, ...props }) => (
                <thead
                  {...props}
                  className="bg-gray-700 text-white font-bold"
                />
              ),
              tbody: ({ node, ...props }) => (
                <tbody {...props} className="text-gray-100" />
              ),
              tr: ({ node, ...props }) => (
                <tr {...props} className="border border-gray-700" />
              ),
              th: ({ node, ...props }) => (
                <th
                  {...props}
                  className="border border-gray-700 px-4 py-2 text-left font-bold"
                />
              ),
              td: ({ node, ...props }) => (
                <td {...props} className="border border-gray-700 px-4 py-2" />
              ),
              
              a: ({ node, ...props }) => (
                <a
                  {...props}
                  className="text-blue-400 hover:text-blue-300 underline transition-colors"
                />
              ),
              
              hr: ({ node, ...props }) => (
                <hr
                  {...props}
                  className="border-0 h-0.5 bg-gradient-to-r from-gray-700 to-gray-900 my-6"
                />
              ),
            }}
          >
            {content}
          </ReactMarkdown>

          {loading && (
            <div className="flex items-center gap-2 pt-4">
              <span className="text-gray-400 text-sm">Processing</span>
              <span className="inline-flex gap-1.5">
                <span className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
                <span className="w-2 h-2 bg-blue-400 rounded-full animate-pulse delay-150" />
                <span className="w-2 h-2 bg-blue-400 rounded-full animate-pulse delay-300" />
              </span>
            </div>
          )}
        </div>
      </div>

      {!loading && response && (
        <div className="mt-4 text-xs text-gray-400 flex justify-between">
          <span>✓ Response complete</span>
          <span className="text-gray-500">
            {response.length} characters
          </span>
        </div>
      )}
    </div>
  );
}
