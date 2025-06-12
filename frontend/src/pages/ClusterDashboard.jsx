//frontend/src/pages/ClusterDashboard.jsx
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

import { Skeleton } from "@/components/ui/Skeleton";
import TriggerPipelineButton from "@/components/TriggerPipelineButton";
import TopQuestionsCard from "@/components/dashboard/TopQuestionsCard";
import FAQCoverageCard from "@/components/dashboard/FAQCoverageCard";
import FAQGapSuggestions from "@/components/dashboard/FAQGapSuggestions";
import ResolutionSentimentChart from "@/components/dashboard/ResolutionSentimentChart";
import MismatchAnalysisCard from "@/components/dashboard/MismatchAnalysisCard";
import ClusterMapCard from "@/components/dashboard/ClusterMapCard";

export default function ClusterDashboard() {
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);
  const [clusters, setClusters] = useState([]);
  const [clusterMap, setClusterMap] = useState([]);
  const navigate = useNavigate();

  const fetchAll = async () => {
    try {
      const userRes = await axios.get("/api/me/");
      setUser(userRes.data);

      const clusterRes = await axios.get("/api/faq/clusters");
      setClusters(clusterRes.data?.clusters || []);
      setClusterMap(clusterRes.data?.cluster_map || []);
    } catch (err) {
      console.error("Error fetching dashboard data:", err);
      navigate("/login");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, []);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-4">
        {[...Array(6)].map((_, i) => (
          <Skeleton key={i} className="h-56 w-full rounded-xl" />
        ))}
      </div>
    );
  }

  return (
    <div className="p-6 space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-gray-900">Cluster Insights Dashboard</h1>
        {user?.is_admin && (
          <TriggerPipelineButton onPipelineComplete={fetchAll} />
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <TopQuestionsCard clusters={clusters} />
        <FAQCoverageCard clusters={clusters} />
        <ResolutionSentimentChart clusters={clusters} />
        <FAQGapSuggestions clusters={clusters} />
        <MismatchAnalysisCard clusters={clusters} />
        <ClusterMapCard data={clusterMap} />
      </div>
    </div>
  );
}
