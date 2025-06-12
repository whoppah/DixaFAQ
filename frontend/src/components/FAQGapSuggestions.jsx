//frontend/src/components/FAQGapSuggestions.jsx
import React from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function FAQGapSuggestions({ suggestions }) {
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Potential FAQ Additions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {suggestions.length > 0 ? (
          suggestions.map((item, idx) => (
            <div key={idx} className="border p-3 rounded-md bg-gray-50">
              <p className="font-medium text-gray-800 mb-1">{item.question}</p>
              <p className="text-sm text-gray-600">{item.answer}</p>
              <div className="flex flex-wrap gap-2 mt-2">
                <Badge variant="secondary">Cluster: {item.clusterId}</Badge>
                <Badge variant="outline">Coverage: {item.coverage}</Badge>
                <Badge variant="outline">Matched: {item.matchedFaq || "None"}</Badge>
              </div>
            </div>
          ))
        ) : (
          <p className="text-sm text-gray-500">No gaps identified at this time.</p>
        )}
      </CardContent>
    </Card>
  );
}
