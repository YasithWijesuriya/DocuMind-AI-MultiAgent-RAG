import React, { useState } from "react";
import { FiFileText,FiUpload  } from "react-icons/fi";


export default function FileUploadZone({ onFileChange, disabled, fileCount, fileNames }) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const input = document.getElementById("file-upload");
      input.files = files;
      onFileChange({ target: { files } });
    }
  };

  return (
    <div className="w-full font-sans">
      <input
        id="file-upload"
        type="file"
        multiple
        accept=".pdf"
        onChange={onFileChange}
        disabled={disabled}
        className="hidden"
      />

      <label
      htmlFor="file-upload"
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`w-full h-full min-h-[420px] flex flex-col items-center justify-center
                rounded-3xl border-2 border-dashed transition-all duration-300 cursor-pointer
                group relative overflow-hidden
                ${disabled
                    ? "bg-gray-700 border-gray-600 text-gray-400"
                    : isDragging
                    ? "bg-gray-700 border-gray-500 text-gray-100 scale-105"
                    : "bg-gray-800 border-gray-600 text-gray-100 hover:border-gray-400 hover:bg-gray-700"
                  }`}
    >



        {/* Background gradient animation */}
        <div className="absolute inset-0 bg-gradient-to-r from-blue-200/0 via-blue-100/5 to-cyan-100/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

        {/* Content */}
        <div className="relative z-10 flex flex-col items-center justify-center text-center">
          {/* Icon with animation */}
        <div className="mb-6 relative group">
          {/* Main Icon */}
          <FiUpload
            className={`w-13 h-13 text-green-100 transition-all duration-500 ease-in-out ${
              disabled
                ? "text-gray-400"
                : "group-hover:scale-110 group-hover:text-green-200"
            } ${isDragging ? "scale-125 rotate-3" : ""}`}
          />
        </div>


          <h2 className="text-5xl font-bold bg-gradient-to-r from-green-200 to-cyan-200 bg-clip-text text-transparent hover:scale-105 transition-transform duration-300">
            {isDragging ? "Drop files here" : "Upload Documents"}
          </h2>

          <p className="mt-4 text-gray-300 max-w-md text-md">
            {isDragging
              ? "Release to upload your PDFs"
              : "Drag & drop your PDF files here or click to browse"}
          </p>

        <div className="mt-6 flex items-center justify-center gap-2 text-[12px] uppercase tracking-widest text-gray-500 font-semibold">
        <FiFileText className="w-5 h-5 text-gray-500" />
        <span>PDF only • Up to 50MB per file</span>
         </div>

        </div>
      </label>

      {/* Success state */}
      {fileCount > 0 && (
        <div className="mt-6 p-5 bg-gradient-to-r from-green-200/40 to-cyan-700/50 rounded-2xl border border-green-400/30 animate-slide-up shadow-lg shadow-blue-100/10">
          <div className="flex items-start gap-3">
            <div className="text-green-300 text-xl mt-1">✓</div>
            <div className="flex-1">
              <p className="text-sm font-bold text-white mb-1">
                {fileCount} File{fileCount !== 1 ? "s" : ""} Selected
              </p>
              <p className="text-xs text-green-200/80 truncate max-w-full font-mono">{fileNames}</p>
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .animate-slide-up {
          animation: slideUp 0.4s ease-out;
        }
      `}</style>
    </div>
  );
}
