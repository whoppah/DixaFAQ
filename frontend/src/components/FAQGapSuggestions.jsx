//frontend/src/components/FAQGapSuggestions.jsx
import React from "react";

export default function FAQGapSuggestions({ suggestions }) {
  return (
    <div className="bg-white rounded-xl shadow-md p-6 transition-shadow hover:shadow-lg">
      <h2 className="text-lg font-semibold text-gray-800 mb-1">Suggested FAQs</h2>
      <p className="text-sm text-gray-500 mb-4">Based on gaps in chatbot coverage</p>

      <div className="space-y-4">
        {suggestions.length === 0 ? (
          <p className="text-sm text-gray-500">No suggestions available</p>
        ) : (
          suggestions.map((s, idx) => (
            <div key={idx} className="border rounded-lg p-3 hover:border-blue-500 transition">
              <h3 className="text-sm font-medium text-blue-600">{s.question}</h3>
              <p className="text-sm text-gray-700 mt-1">{s.answer}</p>
              <p className="text-xs text-gray-400 mt-2">Reason: {s.reason}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
