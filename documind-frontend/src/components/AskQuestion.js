// src/components/AskQuestion.js
import React, { useState } from "react";

export default function AskQuestion({ onAsk }) {
  const [question, setQuestion] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (question.trim() !== "") {
      onAsk(question);
      setQuestion("");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask your question..."
      />
      <button type="submit">Ask</button>
    </form>
  );
}
