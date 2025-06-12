//frontend/src/components/TopQuestionsCard.jsx
import React from "react";

export default function TopQuestionsCard({ questions }) {
  return (
    <div className="bg-white rounded-xl shadow-md p-6 transition-shadow hover:shadow-lg">
      <h2 className="text-lg font-semibold text-gray-800 mb-1">Top 15 Questions</h2>
      <p className="text-sm text-gray-500 mb-4">Most frequent user queries</p>
      <ol className="space-y-2 list-decimal list-inside text-sm text-gray-700">
        {questions.slice(0, 15).map((q, idx) => (
          <li key={idx} className="hover:text-blue-600 transition-colors">
            {q}
          </li>
        ))}
      </ol>
    </div>
  );
}
