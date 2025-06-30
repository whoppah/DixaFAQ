// frontend/src/components/ClusterMapChart.jsx
import React from "react";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

// Custom tooltip content
const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.[0]) return null;

  const { payload: cluster } = payload[0];
  return (
    <div className="bg-white p-3 shadow-lg rounded border text-sm">
      <p><strong>Cluster ID:</strong> {cluster.label}</p>
      <p><strong>Top Message:</strong> {cluster.top_message?.slice(0, 80) || "N/A"}</p>
      <p><strong>Sentiment:</strong> {cluster.sentiment}</p>
      <p><strong>Coverage:</strong> {cluster.coverage}</p>
      <p><strong>Resolution Score:</strong> {cluster.resolution_score}</p>
    </div>
  );
};

// Color clusters by coverage
const getColorByCoverage = (coverage) => {
  switch (coverage) {
    case "Fully":
      return "#22c55e"; // green
    case "Partially":
      return "#facc15"; // yellow
    case "Not":
      return "#ef4444"; // red
    default:
      return "#a1a1aa"; // gray
  }
};

export default function ClusterMapChart({ data, onSelectCluster }) {
  // Group points by label
  const grouped = data.reduce((acc, point) => {
    const label = point.label;
    if (!acc[label]) acc[label] = [];
    acc[label].push(point);
    return acc;
  }, {});

  return (
    <ResponsiveContainer width="100%" height={500}>
      <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
        <CartesianGrid />
        <XAxis type="number" dataKey="x" name="X" />
        <YAxis type="number" dataKey="y" name="Y" />
        <Tooltip content={<CustomTooltip />} />
        {Object.entries(grouped).map(([label, points]) => (
          <Scatter
            key={label}
            name={`Cluster ${label}`}
            data={points}
            fill={getColorByCoverage(points[0]?.coverage)}
            onClick={({ payload }) => onSelectCluster && onSelectCluster(payload)}
          />
        ))}
      </ScatterChart>
    </ResponsiveContainer>
  );
}
