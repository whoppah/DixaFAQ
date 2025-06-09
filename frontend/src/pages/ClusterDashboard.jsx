//frontend/src/pages/ClusterDashboard.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";
import ClusterTable from "../components/ClusterTable";
import ClusterMapChart from "../components/ClusterMapChart";
import FAQMatchModal from "../components/FAQMatchModal";

export default function ClusterDashboard() {
  const [clusters, setClusters] = useState([]);
  const [clusterMap, setClusterMap] = useState([]);
  const [selectedCluster, setSelectedCluster] = useState(null);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);

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

  return (
    <div className="container mx-auto px-4 py-6 space-y-10">
      <h1 className="text-3xl font-bold text-blue-700">📊 Cluster Insight Dashboard</h1>
      
      {loading ? (
        <p className="text-gray-500">Loading...</p>
      ) : (
        <>
          <ClusterMapChart data={clusterMap} />
          <ClusterTable clusters={clusters} onReview={handleOpenModal} />
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
