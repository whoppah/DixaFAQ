// frontend/src/components/ClusterMapChart.jsx
import React from "react";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export default function ClusterMapChart({ data, onSelectCluster }) {
  const grouped = data.reduce((acc, point) => {
    const label = point.label;
    if (!acc[label]) acc[label] = [];
    acc[label].push(point);
    return acc;
  }, {});

  return (
    <ResponsiveContainer width="100%" height={500}>
      <ScatterChart>
        <CartesianGrid />
        <XAxis type="number" dataKey="x" />
        <YAxis type="number" dataKey="y" />
        <Tooltip />
        <Legend />
        {Object.entries(grouped).map(([label, points], index) => (
          <Scatter
            key={label}
            name={`Cluster ${label}`}
            data={points}
            fill={`hsl(${(index * 67) % 360}, 70%, 50%)`}
            onClick={(e) => onSelectCluster(parseInt(label))}
          />
        ))}
      </ScatterChart>
    </ResponsiveContainer>
  );
}
