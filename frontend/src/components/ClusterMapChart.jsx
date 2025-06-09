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

export default function ClusterMapChart({ data }) {
  const grouped = data.reduce((acc, point) => {
    const label = point.label;
    if (!acc[label]) acc[label] = [];
    acc[label].push(point);
    return acc;
  }, {});

  return (
    <div className="w-full h-[500px] bg-white shadow p-4 rounded">
      <h2 className="text-lg font-semibold mb-4">Cluster Map</h2>
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart>
          <CartesianGrid />
          <XAxis type="number" dataKey="x" name="X" />
          <YAxis type="number" dataKey="y" name="Y" />
          <Tooltip cursor={{ strokeDasharray: "3 3" }} />
          <Legend />
          {Object.entries(grouped).map(([label, points], index) => (
            <Scatter
              key={label}
              name={`Cluster ${label}`}
              data={points}
              fill={`hsl(${(index * 67) % 360}, 70%, 50%)`}
            />
          ))}
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
