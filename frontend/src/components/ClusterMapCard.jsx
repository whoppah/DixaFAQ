//frontend/src/components/ClusterMapCard.jsx
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

export default function ClusterMapCard({ data, onSelectCluster }) {
  const grouped = data.reduce((acc, point) => {
    const label = point.label;
    if (!acc[label]) acc[label] = [];
    acc[label].push(point);
    return acc;
  }, {});

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">Cluster Map</h2>
      <div className="w-full h-[400px]">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" dataKey="x" name="UMAP-X" />
            <YAxis type="number" dataKey="y" name="UMAP-Y" />
            <Tooltip cursor={{ strokeDasharray: '3 3' }} />
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
      </div>
      <p className="text-sm text-gray-500 mt-3">Click on a cluster to inspect its messages and evaluation details.</p>
    </div>
  );
}
