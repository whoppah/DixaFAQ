//frontend/src/components/MismatchAnalysisCard.jsx
import React from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function MismatchAnalysisCard({ clusters }) {
  const mismatches = clusters.filter(
    (c) => c.coverage !== "Fully" && c.similarity < 0.8
  );

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>FAQ Mismatch Analysis</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4 text-sm">
        {mismatches.length > 0 ? (
          mismatches.map((item, idx) => (
            <div key={idx} className="bg-gray-50 p-3 rounded border">
              <p className="font-medium text-gray-800 mb-1">{item.top_message}</p>
              <p className="text-gray-600">
                <strong>Matched FAQ:</strong> {item.matched_faq || "None"}
              </p>
              <div className="flex gap-2 mt-2">
                <Badge variant="outline">Coverage: {item.coverage}</Badge>
                <Badge variant="outline">Similarity: {item.similarity}</Badge>
              </div>
            </div>
          ))
        ) : (
          <p className="text-gray-500">No mismatches found.</p>
        )}
      </CardContent>
    </Card>
  );
}
