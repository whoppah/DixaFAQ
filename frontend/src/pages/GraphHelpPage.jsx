//src/pages/GraphHelpPage.jsx
import React from "react";

export default function GraphHelpPage() {
  return (
    <div className="max-w-4xl mx-auto px-6 py-10 space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">📊 Dashboard Guide</h1>
      <p className="text-gray-600">Here's a breakdown of what each graph shows and how to interpret it:</p>

      <section>
        <h2 className="text-xl font-semibold text-blue-700">FAQ Deflection Performance</h2>
        <p className="text-gray-700">Shows weekly trends of FAQ usage and resolution effectiveness.</p>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-blue-700">Trending Questions</h2>
        <p className="text-gray-700">Highlights keywords/topics gaining popularity week-over-week.</p>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-blue-700">Cluster Map</h2>
        <p className="text-gray-700">A 2D scatterplot of semantically similar user messages, grouped by clusters.</p>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-blue-700">Coverage Pie / Sentiment Bar / Resolution Charts</h2>
        <p className="text-gray-700">These show how well each cluster is covered by current FAQs, the emotional tone of messages, and how well they are resolved.</p>
      </section>

      {/* Add more explanations as needed */}
    </div>
  );
}
