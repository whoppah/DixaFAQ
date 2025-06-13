//frontend/src/components/TopProcessGapsPanel.jsx
import React from "react";

export default function TopProcessGapsPanel({ data }) {
  return (
    <div className="space-y-4">
      {data.map((gap, idx) => (
        <div key={idx} className="border rounded-lg p-4 shadow-sm bg-white">
          <h3 className="text-lg font-semibold text-gray-800">{gap.topic}</h3>
          <p className="text-sm text-gray-600 mb-2">
            <strong>{gap.count}</strong> related clusters
          </p>
          <div className="text-sm text-gray-700">
            <p className="font-medium">Common Questions:</p>
            <ul className="list-disc list-inside">
              {gap.examples.slice(0, 5).map((q, i) => (
                <li key={i}>{q}</li>
              ))}
            </ul>
          </div>
        </div>
      ))}
    </div>
  );
}
