// frontend/src/components/FAQImprovementPanel.jsx
import React from "react";

export default function FAQImprovementPanel({ suggestions }) {
  if (!suggestions || suggestions.length === 0) {
    return (
      <p className="text-gray-500">
        No FAQ suggestions needed for current filters.
      </p>
    );
  }

  return (
    <div className="space-y-4">
      {suggestions.map((s, i) => {
        const matched = s.matched_faq || {};
        const hasMatchedFAQ = typeof matched === "object" && matched.question;

        return (
          <div key={i} className="border rounded p-4 bg-gray-50 space-y-2">
            <p className="text-sm text-gray-500">Cluster ID: {s.clusterId}</p>

            {hasMatchedFAQ && (
              <>
                <p><strong>Original FAQ:</strong> {matched.question}</p>
                {matched.answer && (
                  <p><em>A:</em> {matched.answer}</p>
                )}
              </>
            )}

            {!hasMatchedFAQ && (
              <p><strong>Original FAQ:</strong> {String(s.matched_faq)}</p>
            )}

            <p><strong>Coverage:</strong> {s.coverage} — {s.reason}</p>

            <div className="mt-2 space-y-1">
              <p className="font-semibold text-blue-600">Suggested FAQ:</p>
              <p><em>Q:</em> {s.question}</p>
              <p><em>A:</em> {s.answer}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
