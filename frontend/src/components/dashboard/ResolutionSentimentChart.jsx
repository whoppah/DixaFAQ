// frontend/src/components/dashboard/ResolutionSentimentChart.jsx
import React from "react";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";

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
        backgroundColor: ["#16a34a", "#facc15", "#dc2626"],
        borderRadius: 8,
        barThickness: 36,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: (context) => `${context.parsed.y} / 5`,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 5,
        ticks: {
          stepSize: 1,
          color: "#64748b",
        },
        grid: {
          color: "#e2e8f0",
        },
      },
      x: {
        ticks: {
          color: "#334155",
          font: {
            weight: "600",
          },
        },
        grid: {
          display: false,
        },
      },
    },
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-6 w-full h-[350px]">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-800">
          Resolution Score by Sentiment
        </h2>
      </div>
      <div className="h-full w-full">
        <Bar data={data} options={options} />
      </div>
    </div>
  );
}
