//frontend/src/components/FAQCoverageCard.jsx
import React from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

export default function FAQCoverageCard({ fully, partially, none }) {
  const total = fully + partially + none || 1;
  const fullPercent = (fully / total) * 100;
  const partialPercent = (partially / total) * 100;
  const nonePercent = (none / total) * 100;

  return (
    <Card className="bg-white shadow-md rounded-xl p-4 hover:shadow-lg transition-shadow">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-gray-800">FAQ Coverage</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span>Fully Covered</span><span>{Math.round(fullPercent)}%</span>
          </div>
          <Progress value={fullPercent} className="bg-gray-200" />
          
          <div className="flex justify-between pt-2">
            <span>Partially Covered</span><span>{Math.round(partialPercent)}%</span>
          </div>
          <Progress value={partialPercent} className="bg-yellow-200" />

          <div className="flex justify-between pt-2">
            <span>Not Covered</span><span>{Math.round(nonePercent)}%</span>
          </div>
          <Progress value={nonePercent} className="bg-red-200" />
        </div>
      </CardContent>
    </Card>
  );
}
