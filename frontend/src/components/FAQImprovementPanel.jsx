import React from "react";

export default function FAQImprovementPanel({ suggestions }) {
  return (
    <div className="bg-white shadow rounded p-4 w-full">
      <h2 className="text-lg font-semibold mb-4">🛠️ FAQ Improvement Suggestions</h2>
      {suggestions.length === 0 ? (
        <p className="text-gray-500">No FAQ suggestions needed for current filters.</p>
      ) : (
        <div className="space-y-4">
          {suggestions.map((s, i) => (
            <div key={i} className="border rounded p-4 bg-gray-50">
              <p className="text-sm text-gray-500 mb-1">Cluster ID: {s.clusterId}</p>
              <p><strong>Original FAQ:</strong> {s.matchedFaq}</p>
              <p><strong>Coverage:</strong> {s.coverage} — {s.reason}</p>
              <p className="mt-2"><strong>🔁 Suggested FAQ:</strong></p>
              <p><em>Q:</em> {s.question}</p>
              <p><em>A:</em> {s.answer}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
