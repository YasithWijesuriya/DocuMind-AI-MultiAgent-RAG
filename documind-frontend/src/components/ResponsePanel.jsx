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
    <div className="mt-8 bg-white shadow-xl rounded-2xl p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-5">
        <h2 className="text-2xl font-bold text-gray-900">
          Answer
        </h2>

        {!loading && (
          <button
            onClick={onCopy}
            className="px-3 py-1.5 rounded-lg text-sm font-medium
                       bg-gray-100 hover:bg-gray-200 transition"
          >
            {copied ? "✓ Copied" : "Copy"}
          </button>
        )}
      </div>

      {/* Answer body */}
      <div className="bg-gray-50 border border-gray-200 rounded-xl p-6">
        <div
          className="
            prose max-w-none prose-slate

            /* Main title (#) */
            prose-h1:text-3xl
            prose-h1:font-bold
            prose-h1:mb-6
            prose-h1:mt-0

            /* Section headings (##) */
            prose-h2:text-2xl
            prose-h2:font-bold
            prose-h2:mt-10
            prose-h2:mb-4
            prose-h2:border-b
            prose-h2:border-gray-200
            prose-h2:pb-2

            /* Sub-headings (###) */
            prose-h3:text-xl
            prose-h3:font-semibold
            prose-h3:mt-8
            prose-h3:mb-3

            /* Paragraphs */
            prose-p:text-gray-700
            prose-p:leading-relaxed
            prose-p:mb-4

            /* Lists */
            prose-ul:mb-4
            prose-ol:mb-4
            prose-li:mb-2

            /* Blockquotes (citations feel) */
            prose-blockquote:border-l-4
            prose-blockquote:border-gray-300
            prose-blockquote:pl-4
            prose-blockquote:text-gray-600

            /* Code blocks */
            prose-pre:bg-slate-900
            prose-pre:text-slate-100
            prose-pre:rounded-xl
            prose-pre:p-4
          "
        >
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {content}
          </ReactMarkdown>

          {/* Streaming cursor */}
          {loading && (
            <span className="inline-flex items-center gap-1 ml-2">
            <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse" />
            <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse delay-150" />
            <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse delay-300" />
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
