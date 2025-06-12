//frontend/src/components/FAQCoverageCard.jsx
import React from "react";

export default function FAQCoverageCard({ coverageStats }) {
  const { fully, partially, notCovered } = coverageStats;
  const total = fully + partially + notCovered;

  const barWidth = (value) => `${(value / total) * 100}%`;

  return (
    <div className="bg-white rounded-xl shadow-md p-6 transition-shadow hover:shadow-lg">
      <h2 className="text-lg font-semibold text-gray-800 mb-1">FAQ Coverage</h2>
      <p className="text-sm text-gray-500 mb-4">How well user questions are covered</p>

      <div className="space-y-2">
        <div className="flex justify-between text-sm text-gray-700">
          <span>Fully Covered</span>
          <span>{fully}</span>
        </div>
        <div className="w-full bg-gray-100 h-2 rounded-full">
          <div className="h-full bg-green-500 rounded-full" style={{ width: barWidth(fully) }} />
        </div>

        <div className="flex justify-between text-sm text-gray-700">
          <span>Partially Covered</span>
          <span>{partially}</span>
        </div>
        <div className="w-full bg-gray-100 h-2 rounded-full">
          <div className="h-full bg-yellow-400 rounded-full" style={{ width: barWidth(partially) }} />
        </div>

        <div className="flex justify-between text-sm text-gray-700">
          <span>Not Covered</span>
          <span>{notCovered}</span>
        </div>
        <div className="w-full bg-gray-100 h-2 rounded-full">
          <div className="h-full bg-red-400 rounded-full" style={{ width: barWidth(notCovered) }} />
        </div>
      </div>
    </div>
  );
}
