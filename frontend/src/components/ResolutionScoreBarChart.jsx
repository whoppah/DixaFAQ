import React from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer,
} from "recharts";

export default function ResolutionScoreBarChart({ clusters }) {
  const counts = [1, 2, 3, 4, 5].map(score => ({
    score: score,
    count: clusters.filter(c => c.resolution_score === score).length
  }));

  return (
    <div className="bg-white shadow p-4 rounded w-full max-w-2xl">
      <h2 className="text-lg font-semibold mb-2">📊 Resolution Score Distribution</h2>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={counts}>
          <CartesianGrid />
          <XAxis dataKey="score" />
          <YAxis allowDecimals={false} />
          <Tooltip />
          <Bar dataKey="count" fill="#34d399" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
