//frontend/src/components/SentimentBarChart.jsx
import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

export default function SentimentBarChart({ clusters }) {
  const count = { Positive: 0, Neutral: 0, Negative: 0 };

  clusters.forEach((c) => {
    const sentiment = (c.sentiment || "").toLowerCase();
    if (sentiment === "positive") count.Positive += 1;
    else if (sentiment === "neutral") count.Neutral += 1;
    else if (sentiment === "negative") count.Negative += 1;
  });


  const data = Object.entries(count).map(([sentiment, value]) => ({
    sentiment,
    value,
  }));

  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="sentiment" />
        <YAxis allowDecimals={false} />
        <Tooltip />
        <Bar dataKey="value" fill="#6366f1" />
      </BarChart>
    </ResponsiveContainer>
  );
}
