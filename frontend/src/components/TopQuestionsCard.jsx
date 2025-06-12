//frontend/src/components/TopQuestionsCard.jsx
import React from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export default function TopQuestionsCard({ topQuestions }) {
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Top 15 Customer Questions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {topQuestions && topQuestions.length > 0 ? (
          <ol className="list-decimal list-inside space-y-1 text-sm text-gray-800">
            {topQuestions.slice(0, 15).map((question, idx) => (
              <li key={idx}>{question}</li>
            ))}
          </ol>
        ) : (
          <p className="text-sm text-gray-500">No questions found.</p>
        )}
      </CardContent>
    </Card>
  );
}
