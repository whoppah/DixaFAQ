//frontend/src/components/FAQDeflectionTrends.jsx
import React, { useEffect, useState } from "react";
import axios from "axios";
import CardWrapper from "./CardWrapper";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend
} from "recharts";

export default function FAQDeflectionTrends() {
  const [faqData, setFaqData] = useState([]);
  const [selectedFaqIndex, setSelectedFaqIndex] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTrends = async () => {
      try {
        const res = await axios.get("/api/faq/deflection-metrics/");
        setFaqData(res.data.faq_performance || []);
      } catch (err) {
        console.error("Failed to fetch FAQ performance", err);
      } finally {
        setLoading(false);
      }
    };

    fetchTrends();
  }, []);

  const selectedFaq = faqData[selectedFaqIndex];

  return (
    <CardWrapper title="FAQ Deflection Performance">
      {loading ? (
        <p className="text-gray-500">Loading FAQ metrics...</p>
      ) : faqData.length === 0 ? (
        <p className="text-gray-500">No data found.</p>
      ) : (
        <>
          <div className="mb-4">
            <label className="text-sm font-medium text-gray-700">
              Select FAQ:
            </label>
            <select
              className="ml-2 border p-1 rounded text-sm"
              value={selectedFaqIndex}
              onChange={(e) => setSelectedFaqIndex(Number(e.target.value))}
            >
              {faqData.map((faq, idx) => (
                <option key={idx} value={idx}>
                  {faq.question.slice(0, 80)}...
                </option>
              ))}
            </select>
          </div>

          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={selectedFaq.trend}>
              <XAxis dataKey="week" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="deflection_count"
                name="Deflection Count"
                stroke="#3b82f6"
                strokeWidth={2}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="avg_resolution_score"
                name="Avg. Resolution Score"
                stroke="#10b981"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </>
      )}
    </CardWrapper>
  );
}
