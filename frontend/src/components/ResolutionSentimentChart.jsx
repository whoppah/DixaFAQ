//frontend/src/components/ResolutionSentimentChart.jsx
import React from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

export default function ResolutionSentimentChart({ clusters }) {
  const categories = ["Positive", "Neutral", "Negative"];
  const scoresBySentiment = {
    Positive: [],
    Neutral: [],
    Negative: [],
  };

  clusters.forEach((cluster) => {
    const sentiment = cluster.sentiment;
    if (scoresBySentiment[sentiment]) {
      scoresBySentiment[sentiment].push(cluster.resolution_score);
    }
  });

  const averageScore = (arr) =>
    arr.length ? (arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(2) : 0;

  const data = {
    labels: categories,
    datasets: [
      {
        label: "Avg Resolution Score",
        data: categories.map((cat) => averageScore(scoresBySentiment[cat])),
        backgroundColor: ["#22c55e", "#facc15", "#ef4444"],
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { display: false },
    },
    scales: {
      y: { beginAtZero: true, max: 5 },
    },
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Resolution Score by Sentiment</CardTitle>
      </CardHeader>
      <CardContent>
        <Bar data={data} options={options} />
      </CardContent>
    </Card>
  );
}
