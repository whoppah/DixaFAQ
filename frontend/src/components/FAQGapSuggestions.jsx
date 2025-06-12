//frontend/src/components/FAQGapSuggestions.jsx
import React from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";

export default function FAQGapSuggestions({ suggestions }) {
  return (
    <Card className="bg-white shadow-md rounded-xl p-4 hover:shadow-lg transition-shadow">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-gray-800">FAQ Improvement Suggestions</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4 text-sm text-gray-700">
          {suggestions.length === 0 && <p>No new suggestions at this time.</p>}
          {suggestions.map((item, idx) => (
            <div key={idx} className="border-b pb-2">
              <p className="font-medium">{item.question}</p>
              <p className="text-xs text-gray-500">Reason: {item.reason}</p>
              <p className="text-xs text-gray-500">Matched FAQ: {item.matchedFaq || "None"}</p>
              <div className="mt-1">
                <Badge>{item.coverage}</Badge>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
