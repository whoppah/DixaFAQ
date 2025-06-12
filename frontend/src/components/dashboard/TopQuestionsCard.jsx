//frontend/src/components/dashboard/TopQuestionsCard.jsx
import React from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";

export default function TopQuestionsCard({ questions }) {
  return (
    <Card className="bg-white shadow-md rounded-xl p-4 hover:shadow-lg transition-shadow">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-gray-800">Top User Questions</CardTitle>
      </CardHeader>
      <CardContent>
        <ol className="list-decimal list-inside text-sm text-gray-700 space-y-1">
          {questions.slice(0, 15).map((q, idx) => (
            <li key={idx} className="truncate">{q}</li>
          ))}
        </ol>
      </CardContent>
    </Card>
  );
}
