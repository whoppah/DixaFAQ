//frontend/src/components/TopGapsByTopicChart.jsx
import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  CartesianGrid,
  LabelList,
} from "recharts";

// Dynamic color scale
const getBarColor = (count) => {
  if (count >= 5) return "#ef4444"; // red
  if (count >= 3) return "#facc15"; // yellow
  return "#10b981"; // green
};

// Truncate label for Y axis
const truncate = (label, max = 30) => {
  return label.length > max ? label.slice(0, max) + "…" : label;
};

// Custom tooltip with full topic label
const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.[0]) return null;
  const { topic, count } = payload[0].payload;
  return (
    <div className="bg-white p-3 shadow-md border rounded text-sm">
      <p><strong>Topic:</strong> {topic}</p>
      <p><strong>Gap Count:</strong> {count}</p>
    </div>
  );
};

export default function TopGapsByTopicChart({ clusters = [] }) {
  // Aggregate counts by topic_label
  const topicMap = {};
  clusters.forEach((c) => {
    const topic = c.topic_label || "Unknown";
    topicMap[topic] = (topicMap[topic] || 0) + 1;
  });

  const chartData = Object.entries(topicMap)
    .map(([topic, count]) => ({ topic, count }))
    .sort((a, b) => b.count - a.count); // sort descending

  return (
    <ResponsiveContainer width="100%" height={500}>
      <BarChart
        layout="vertical"
        data={chartData}
        margin={{ top: 20, right: 30, left: 100, bottom: 20 }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" allowDecimals={false} />
        <YAxis
          dataKey="topic"
          type="category"
          tickFormatter={(label) => truncate(label)}
          width={200}
        />
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey="count">
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={getBarColor(entry.count)} />
          ))}
          <LabelList dataKey="count" position="right" />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
