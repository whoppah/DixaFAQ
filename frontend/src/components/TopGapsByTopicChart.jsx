import React from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from "recharts";

export default function TopGapsByTopicChart({ clusters }) {
  const topicCounts = clusters
    .filter(c => c.coverage !== "Fully")
    .reduce((acc, c) => {
      const label = c.topic_label || "Unlabeled";
      acc[label] = (acc[label] || 0) + 1;
      return acc;
    }, {});

  const data = Object.entries(topicCounts).map(([label, count]) => ({
    topic: label,
    gaps: count,
  }));

  return (
    <div className="bg-white shadow p-4 rounded w-full">
      <h2 className="text-lg font-semibold mb-2">Top FAQ Gaps by Topic</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" />
          <YAxis dataKey="topic" type="category" width={200} />
          <Tooltip />
          <Bar dataKey="gaps" fill="#f87171" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
