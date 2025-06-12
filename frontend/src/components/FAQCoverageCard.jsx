//frontend/src/components/FAQCoverageCard.jsx
import React from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

export default function FAQCoverageCard({ full, partial, none }) {
  const total = full + partial + none;
  const fullPct = total ? ((full / total) * 100).toFixed(1) : 0;
  const partialPct = total ? ((partial / total) * 100).toFixed(1) : 0;
  const nonePct = total ? ((none / total) * 100).toFixed(1) : 0;

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>FAQ Coverage Breakdown</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4 text-sm">
        <div>
          <span className="font-medium">Fully Covered</span>
          <Progress value={fullPct} className="mt-1" />
          <span className="text-gray-600">{fullPct}%</span>
        </div>
        <div>
          <span className="font-medium">Partially Covered</span>
          <Progress value={partialPct} className="mt-1 bg-yellow-400" />
          <span className="text-gray-600">{partialPct}%</span>
        </div>
        <div>
          <span className="font-medium">Not Covered</span>
          <Progress value={nonePct} className="mt-1 bg-red-400" />
          <span className="text-gray-600">{nonePct}%</span>
        </div>
      </CardContent>
    </Card>
  );
}
