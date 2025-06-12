//frontend/src/components/ResolutionTimelineChart.jsx
import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

export default function ResolutionTimelineChart({ clusters }) {
  const grouped = clusters.reduce((acc, c) => {
    const date = c.created_at?.slice(0, 10);
    if (!date) return acc;
    if (!acc[date]) acc[date] = [];
    acc[date].push(c.resolution_score);
    return acc;
  }, {});

  const data = Object.entries(grouped).map(([date, scores]) => ({
    date,
    avg_score: scores.reduce((a, b) => a + b, 0) / scores.length,
  }));

  return (
    <ResponsiveContainer width="100%" height={250}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis domain={[1, 5]} allowDecimals={false} />
        <Tooltip />
        <Line type="monotone" dataKey="avg_score" stroke="#3b82f6" />
      </LineChart>
    </ResponsiveContainer>
  );
}
