//frontend/src/pages/ClusterDashboard.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";
import ClusterTable from "../components/ClusterTable";
import FAQMatchModal from "../components/FAQMatchModal";
import ClusterMapChart from "../components/ClusterMapChart";
import ClusterFrequencyChart from "../components/ClusterFrequencyChart";
import SentimentBarChart from "../components/SentimentBarChart";
import CoveragePieChart from "../components/CoveragePieChart";
import ResolutionScoreBarChart from "../components/ResolutionScoreBarChart";
import ResolutionTimelineChart from "../components/ResolutionTimelineChart";


export default function ClusterDashboard() {
  const [clusters, setClusters] = useState([]);
  const [clusterMap, setClusterMap] = useState([]);
  const [selectedCluster, setSelectedCluster] = useState(null);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  // Filters
  const [sentimentFilter, setSentimentFilter] = useState("All");
  const [keywordFilter, setKeywordFilter] = useState("");
  const [coverageFilter, setCoverageFilter] = useState("All");
  const [minResolutionScore, setMinResolutionScore] = useState(1);
  const [dateRange, setDateRange] = useState({ from: "", to: "" });

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await axios.get("/api/faq/clusters");
        setClusters(res.data.clusters);
        setClusterMap(res.data.cluster_map);
      } catch (err) {
        console.error("Failed to load clusters:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
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

    const resolutionMatch =
      cluster.resolution_score >= minResolutionScore;

    const date = new Date(cluster.created_at);
    const from = dateRange.from ? new Date(dateRange.from) : null;
    const to = dateRange.to ? new Date(dateRange.to) : null;
    const dateMatch =
      (!from || date >= from) && (!to || date <= to);

    return (
      sentimentMatch &&
      keywordMatch &&
      coverageMatch &&
      resolutionMatch &&
      dateMatch
    );
  });

  const getSimulatedTimeline = (clusters) =>
    clusters.map((c, i) => ({
      cluster_id: c.cluster_id,
      date: c.created_at || new Date(Date.now() - i * 86400000).toISOString().slice(0, 10),
    }));

  return (
    <div className="container mx-auto px-4 py-6 space-y-10">
      <h1 className="text-3xl font-bold text-blue-700">📊 Cluster Insight Dashboard</h1>

      {loading ? (
        <p className="text-gray-500">Loading...</p>
      ) : (
        <>
          {/* Filter Controls */}
          <div className="bg-white p-4 rounded shadow flex flex-wrap gap-4 items-center">
            <select
              className="border p-2 rounded"
              value={sentimentFilter}
              onChange={(e) => setSentimentFilter(e.target.value)}
            >
              <option value="All">All Sentiments</option>
              <option value="Positive">Positive</option>
              <option value="Neutral">Neutral</option>
              <option value="Negative">Negative</option>
            </select>

            <input
              type="text"
              placeholder="Filter by keyword..."
              className="border p-2 rounded"
              value={keywordFilter}
              onChange={(e) => setKeywordFilter(e.target.value)}
            />

            <select
              className="border p-2 rounded"
              value={coverageFilter}
              onChange={(e) => setCoverageFilter(e.target.value)}
            >
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
              className="border p-2 rounded w-48"
              value={minResolutionScore}
              onChange={(e) => setMinResolutionScore(parseInt(e.target.value))}
            />

            <input
              type="date"
              className="border p-2 rounded"
              onChange={(e) =>
                setDateRange({ ...dateRange, from: e.target.value })
              }
            />
            <input
              type="date"
              className="border p-2 rounded"
              onChange={(e) =>
                setDateRange({ ...dateRange, to: e.target.value })
              }
            />
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <SentimentBarChart clusters={filteredClusters} />
            <CoveragePieChart clusters={filteredClusters} />
            <ResolutionScoreBarChart clusters={filteredClusters} />
            <ResolutionTimelineChart clusters={filteredClusters} />
          </div>


          <ClusterMapChart
            data={clusterMap}
            onSelectCluster={handleSelectClusterFromMap}
          />

          <ClusterFrequencyChart data={getSimulatedTimeline(filteredClusters)} />

          <ClusterTable clusters={filteredClusters} onReview={handleOpenModal} />
        </>
      )}

      {selectedCluster && (
        <FAQMatchModal
          open={isOpen}
          onClose={() => setIsOpen(false)}
          cluster={selectedCluster}
        />
      )}
    </div>
  );
}
