// src/components/ResponseDisplay.js
import React from "react";

export default function ResponseDisplay({ response }) {
  if (!response) return null;

  return (
    <div className="response-display">
      <h3>Route: {response.route}</h3>
      <h4>Final Answer:</h4>
      <p>{response.final_answer}</p>
      <h4>Validation Status:</h4>
      <p>{response.validation.status}</p>
      <h4>Validation Report:</h4>
      <p>{response.validation.report}</p>
    </div>
  );
}
