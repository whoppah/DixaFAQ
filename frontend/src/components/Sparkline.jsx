// components/Sparkline.jsx
import React from "react";
import { LineChart, Line, ResponsiveContainer } from "recharts";

export default function Sparkline({ data }) {
  return (
    <ResponsiveContainer width={100} height={30}>
      <LineChart data={data}>
        <Line type="monotone" dataKey="value" stroke="#6366f1" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
