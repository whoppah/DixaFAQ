//frontend/src/components/CoveragePieChart.jsx
import React from "react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export default function CoveragePieChart({ clusters }) {
  const count = { Fully: 0, Partially: 0, Not: 0 };

  clusters.forEach((c) => {
    count[c.coverage] = (count[c.coverage] || 0) + 1;
  });

  const data = Object.entries(count).map(([label, value]) => ({
    name: label,
    value,
  }));

  const COLORS = ["#10b981", "#facc15", "#ef4444"];

  return (
    <ResponsiveContainer width="100%" height={250}>
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          outerRadius={80}
          label
        >
          {data.map((_, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}
