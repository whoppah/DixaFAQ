//frontend/src/pages/ClusterDashboard.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";
import ClusterTable from "../components/ClusterTable";
import FAQMatchModal from "../components/FAQMatchModal";
import ClusterMapChart from "../components/ClusterMapChart";
import ClusterFrequencyChart from "../components/ClusterFrequencyChart";

export default function ClusterDashboard() {
  const [clusters, setClusters] = useState([]);
  const [clusterMap, setClusterMap] = useState([]);
  const [selectedCluster, setSelectedCluster] = useState(null);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [sentimentFilter, setSentimentFilter] = useState("All");
  const [keywordFilter, setKeywordFilter] = useState("");

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

    return sentimentMatch && keywordMatch;
  });

  const getSimulatedTimeline = (clusters) =>
    clusters.map((c, i) => ({
      cluster_id: c.cluster_id,
      date: new Date(Date.now() - i * 86400000).toISOString().slice(0, 10),
    }));

  return (
    <div className="container mx-auto px-4 py-6 space-y-10">
      <h1 className="text-3xl font-bold text-blue-700">📊 Cluster Insight Dashboard</h1>

      {loading ? (
        <p className="text-gray-500">Loading...</p>
      ) : (
        <>
          <ClusterMapChart
            data={clusterMap}
            onSelectCluster={handleSelectClusterFromMap}
          />

          <ClusterFrequencyChart data={getSimulatedTimeline(clusters)} />

          <div className="flex flex-wrap gap-4 items-center">
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
          </div>

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
