//frontend/src/components/ClusterFrequencyChart.jsx
import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function ClusterFrequencyChart({ data }) {
  // Count clusters per date
  const grouped = data.reduce((acc, item) => {
    acc[item.date] = (acc[item.date] || 0) + 1;
    return acc;
  }, {});

  const chartData = Object.entries(grouped).map(([date, count]) => ({
    date,
    count,
  }));

  return (
    <div className="w-full h-[300px] bg-white shadow p-4 rounded">
      <h2 className="text-lg font-semibold mb-4">📈 Cluster Frequency Timeline</h2>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis allowDecimals={false} />
          <Tooltip />
          <Line type="monotone" dataKey="count" stroke="#2563eb" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
