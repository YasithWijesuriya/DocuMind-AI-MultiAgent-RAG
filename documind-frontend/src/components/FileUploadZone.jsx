import React from "react";

export default function FileUploadZone({ onFileChange, disabled, fileCount, fileNames }) {
  return (
    <div>
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
        className={`flex flex-col items-center justify-center px-6 py-12 border-2 border-dashed rounded-xl cursor-pointer transition-all ${
          disabled
            ? "border-gray-200 bg-gray-50 cursor-not-allowed opacity-50"
            : "border-blue-300 bg-blue-50 hover:border-blue-500 hover:bg-blue-100"
        }`}
      >
        <svg className="w-12 h-12 text-blue-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4v16m8-8H4" />
        </svg>
        <p className="text-center text-gray-900 font-semibold">Click to upload <span className="text-gray-600">or drag and drop</span></p>
        <p className="text-xs text-gray-500 mt-1">PDF files up to 50MB each</p>
      </label>

      {fileCount > 0 && (
        <div className="mt-4 p-4 bg-green-50 rounded-lg border border-green-200">
          <p className="text-sm font-medium text-green-800">
            {fileCount} file{fileCount !== 1 ? "s" : ""} selected
          </p>
          <p className="text-xs text-green-700 truncate max-w-full">{fileNames}</p>
        </div>
      )}
    </div>
  );
}
