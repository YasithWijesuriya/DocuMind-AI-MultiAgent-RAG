import React, { useState } from "react";
import UploadDocuments from "./components/UploadDocuments";
import AskQuestion from "./components/AskQuestion"
import ResponseDisplay from "./components/ResponseDisplay";
import axios from "axios";

function App() {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [response, setResponse] = useState(null);

  const handleFilesUploaded = (files) => {
    setUploadedFiles(files);
  };

  const handleAsk = async (question) => {
    if (uploadedFiles.length === 0) {
      alert("Please upload at least one document.");
      return;
    }

    const formData = new FormData();
    uploadedFiles.forEach((file) => formData.append("files", file));
    formData.append("question", question);

    try {
      const res = await axios.post("http://localhost:8000/ask", formData);
      setResponse(res.data);
    } catch (error) {
      console.error(error);
      alert("Error processing your question");
    }
  };

  return (
    <div className="App">
      <h1>DocuMind - Intelligent Document Assistant</h1>
      <UploadDocuments onFilesUploaded={handleFilesUploaded} />
      <AskQuestion onAsk={handleAsk} />
      <ResponseDisplay response={response} />
    </div>
  );
}

export default App;
