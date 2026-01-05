// src/components/UploadDocuments.js
import React, { useState } from "react";
import { useDropzone } from "react-dropzone";

export default function UploadDocuments({ onFilesUploaded }) {
  const [files, setFiles] = useState([]);

  const { getRootProps, getInputProps } = useDropzone({
    accept: { "application/pdf": [".pdf"] },
    onDrop: (acceptedFiles) => {
      setFiles(acceptedFiles);
      onFilesUploaded(acceptedFiles);
    },
  });

  return (
    <div className="upload-container" {...getRootProps()}>
      <input {...getInputProps()} />
      <p>Drag & drop PDF files here, or click to select files</p>
      <ul>
        {files.map((f) => (
          <li key={f.path}>{f.path}</li>
        ))}
      </ul>
    </div>
  );
}
