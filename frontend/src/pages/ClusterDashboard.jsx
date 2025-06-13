//frontend/src/pages/ClusterDashboard.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

import CardWrapper from "../components/CardWrapper";  
import MetricCard from "../components/MetricCard";  
import ClusterTable from "../components/ClusterTable";
import FAQMatchModal from "../components/FAQMatchModal";
import ClusterMapChart from "../components/ClusterMapChart";
import ClusterFrequencyChart from "../components/ClusterFrequencyChart";
import SentimentBarChart from "../components/SentimentBarChart";
import CoveragePieChart from "../components/CoveragePieChart";
import ResolutionScoreBarChart from "../components/ResolutionScoreBarChart";
import ResolutionTimelineChart from "../components/ResolutionTimelineChart";
import FAQImprovementPanel from "../components/FAQImprovementPanel";
import TopGapsByTopicChart from "../components/TopGapsByTopicChart";
import TriggerPipelineButton from "../components/TriggerPipelineButton";

axios.defaults.withCredentials = true;

export default function ClusterDashboard() {
  const [clusters, setClusters] = useState([]);
  const [clusterMap, setClusterMap] = useState([]);
  const [selectedCluster, setSelectedCluster] = useState(null);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);

  const navigate = useNavigate();

  const refreshData = async () => {
    setLoading(true);
    try {
      const res = await axios.get("/api/faq/clusters");
      setClusters(res.data?.clusters || []);
      setClusterMap(res.data?.cluster_map || []);
    } catch (err) {
      console.error("Failed to load clusters:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchUser = async () => {
    try {
      const res = await axios.get("/api/me/");
      setUser(res.data);
    } catch (err) {
      console.warn("Not authenticated, redirecting...");
      navigate("/login");
    }
  };

  useEffect(() => {
    fetchUser();
    refreshData();
  }, []);

  const handleOpenModal = (cluster) => {
    setSelectedCluster(cluster);
    setIsOpen(true);
  };

  const handleSelectClusterFromMap = (clusterId) => {
    const target = clusters.find((c) => c.cluster_id === clusterId);
    if (target) {
      setSelectedCluster(target);
      setIsOpen(true);
    }
  };

  const [sentimentFilter, setSentimentFilter] = useState("All");
  const [keywordFilter, setKeywordFilter] = useState("");
  const [coverageFilter, setCoverageFilter] = useState("All");
  const [minResolutionScore, setMinResolutionScore] = useState(1);
  const [dateRange, setDateRange] = useState({ from: "", to: "" });

  const filteredClusters = clusters.filter((cluster) => {
    const sentimentMatch =
      sentimentFilter === "All" || cluster.sentiment === sentimentFilter;
    const keywordMatch =
      keywordFilter === "" ||
      cluster.keywords.some((k) =>
        k.toLowerCase().includes(keywordFilter.toLowerCase())
      );
    const coverageMatch =
      coverageFilter === "All" || cluster.coverage === coverageFilter;
    const resolutionMatch = cluster.resolution_score >= minResolutionScore;

    const date = new Date(cluster.created_at);
    const from = dateRange.from ? new Date(dateRange.from) : null;
    const to = dateRange.to ? new Date(dateRange.to) : null;
    const dateMatch = (!from || date >= from) && (!to || date <= to);

    return (
      sentimentMatch &&
      keywordMatch &&
      coverageMatch &&
      resolutionMatch &&
      dateMatch
    );
  });

  const faqSuggestions = filteredClusters
    .filter((c) => c.faq_suggestion && c.faq_suggestion.question)
    .map((c) => ({
      clusterId: c.cluster_id,
      question: c.faq_suggestion.question,
      answer: c.faq_suggestion.answer,
      reason: c.resolution_reason,
      coverage: c.coverage,
      matched_faq: c.matched_faq,
      resolution_score: c.resolution_score,
      faq_suggestion: c.faq_suggestion
    }));

  const getSimulatedTimeline = (clusters) =>
    clusters.map((c, i) => ({
      cluster_id: c.cluster_id,
      date:
        c.created_at ||
        new Date(Date.now() - i * 86400000).toISOString().slice(0, 10),
    }));

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-10">
      <h1 className="text-4xl font-bold text-gray-800">Dashboard</h1>

      {user?.is_admin && (
        <TriggerPipelineButton onPipelineComplete={refreshData} isAdmin={true} />
      )}

      {loading ? (
        <p className="text-gray-500">Loading...</p>
      ) : (
        <>
          {/* Filters */}
          <div className="bg-white border rounded-xl p-4 shadow-sm flex flex-wrap gap-4 items-center">
            <select className="border p-2 rounded text-sm" value={sentimentFilter} onChange={(e) => setSentimentFilter(e.target.value)}>
              <option value="All">All Sentiments</option>
              <option value="Positive">Positive</option>
              <option value="Neutral">Neutral</option>
              <option value="Negative">Negative</option>
            </select>

            <input
              type="text"
              placeholder="Filter by keyword..."
              className="border p-2 rounded text-sm"
              value={keywordFilter}
              onChange={(e) => setKeywordFilter(e.target.value)}
            />

            <select className="border p-2 rounded text-sm" value={coverageFilter} onChange={(e) => setCoverageFilter(e.target.value)}>
              <option value="All">All Coverage</option>
              <option value="Fully">Fully</option>
              <option value="Partially">Partially</option>
              <option value="Not">Not</option>
            </select>

            <input
              type="number"
              min="1"
              max="5"
              placeholder="Min Resolution Score"
              className="border p-2 rounded w-48 text-sm"
              value={minResolutionScore}
              onChange={(e) => setMinResolutionScore(parseInt(e.target.value))}
            />

            <input type="date" className="border p-2 rounded text-sm" onChange={(e) => setDateRange({ ...dateRange, from: e.target.value })} />
            <input type="date" className="border p-2 rounded text-sm" onChange={(e) => setDateRange({ ...dateRange, to: e.target.value })} />
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <CardWrapper title="Sentiment Distribution">
              <SentimentBarChart clusters={filteredClusters} />
            </CardWrapper>

            <CardWrapper title="FAQ Match Quality">
              <CoveragePieChart clusters={filteredClusters} />
            </CardWrapper>

            <CardWrapper title="Resolution Score Distribution">
              <ResolutionScoreBarChart clusters={filteredClusters} />
            </CardWrapper>

            <CardWrapper title="Avg. Resolution Score Over Time">
              <ResolutionTimelineChart clusters={filteredClusters} />
            </CardWrapper>
          </div>

          <CardWrapper title="Top FAQ Gaps by Topic">
            <TopGapsByTopicChart clusters={filteredClusters} />
          </CardWrapper>

          <CardWrapper title="FAQ Improvement Suggestions">
            <FAQImprovementPanel suggestions={faqSuggestions} />
          </CardWrapper>

          <CardWrapper title="Cluster Map">
            <ClusterMapChart data={clusterMap} onSelectCluster={handleSelectClusterFromMap} />
          </CardWrapper>

          <CardWrapper title="Cluster Frequency Timeline">
            <ClusterFrequencyChart data={getSimulatedTimeline(filteredClusters)} />
          </CardWrapper>

          <CardWrapper title="All Clusters">
            <ClusterTable clusters={filteredClusters} onReview={handleOpenModal} />
          </CardWrapper>
        </>
      )}

      {selectedCluster && (
        <FAQMatchModal open={isOpen} onClose={() => setIsOpen(false)} cluster={selectedCluster} />
      )}
    </div>
  );
}
