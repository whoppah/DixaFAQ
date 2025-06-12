//frontend/src/components/ClusterMapCard.jsx
import React from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import ClusterMapChart from "./ClusterMapChart";

export default function ClusterMapCard({ data, onSelectCluster }) {
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Cluster Map</CardTitle>
      </CardHeader>
      <CardContent>
        <ClusterMapChart data={data} onSelectCluster={onSelectCluster} />
      </CardContent>
    </Card>
  );
}
