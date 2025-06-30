// frontend/src/components/MessageSentimentTimelineChart.jsx
import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export default function MessageSentimentTimelineChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis allowDecimals={false} />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="Positive" stroke="#10b981" />
        <Line type="monotone" dataKey="Neutral" stroke="#facc15" />
        <Line type="monotone" dataKey="Negative" stroke="#ef4444" />
      </LineChart>
    </ResponsiveContainer>
  );
}
