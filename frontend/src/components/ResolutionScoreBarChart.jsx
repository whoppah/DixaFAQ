//frontend/src/components/ResolutionScoreBarChart.jsx
import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

export default function ResolutionScoreBarChart({ clusters }) {
  const counts = [1, 2, 3, 4, 5].map((score) => ({
    score,
    count: clusters.filter((c) => c.resolution_score === score).length,
  }));

  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={counts}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="score" />
        <YAxis allowDecimals={false} />
        <Tooltip />
        <Bar dataKey="count" fill="#34d399" />
      </BarChart>
    </ResponsiveContainer>
  );
}
