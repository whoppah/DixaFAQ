//frontend/src/pages/ClusterDashboard.jsx
import React, { useState, useEffect, useRef } from "react";
import axios from "../lib/axios";
import { useNavigate } from "react-router-dom";
import { Button, Select } from "flowbite-react";
import { HiOutlineInformationCircle } from "react-icons/hi";

import CardWrapper from "../components/CardWrapper";
import MetricCard from "../components/MetricCard";
import ClusterTable from "../components/ClusterTable";
import FAQMatchModal from "../components/FAQMatchModal";
import ClusterMapChart from "../components/ClusterMapChart";
import MessageSentimentTimelineChart from "../components/MessageSentimentTimelineChart";
import SentimentBarChart from "../components/SentimentBarChart";
import CoveragePieChart from "../components/CoveragePieChart";
import ResolutionScoreBarChart from "../components/ResolutionScoreBarChart";
import ResolutionTimelineChart from "../components/ResolutionTimelineChart";
import FAQImprovementPanel from "../components/FAQImprovementPanel";
import TopGapsByTopicChart from "../components/TopGapsByTopicChart";
import TriggerPipelineButton from "../components/TriggerPipelineButton";
import FAQDeflectionTrends from "../components/FAQDeflectionTrends";
import TrendingTopicsLeaderboard from "../components/TrendingTopicsLeaderboard";
import TopProcessGapsPanel from "../components/TopProcessGapsPanel";
import ClusterMessagesModal from "../components/ClusterMessagesModal";
import DashboardHelpPanel from "../components/DashboardHelpPanel";

export default function ClusterDashboard() {
  const [clusters, setClusters] = useState([]);
  const [clusterMap, setClusterMap] = useState([]);
  const [selectedCluster, setSelectedCluster] = useState(null);
  const selectedClusterId = selectedCluster?.cluster_id || null;

  const [isOpen, setIsOpen] = useState(false);
  const [showMessagesModal, setShowMessagesModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState({ is_admin: true });
  const [processGaps, setProcessGaps] = useState([]);
  const selectedRef = useRef(null);
  const navigate = useNavigate();

  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState("cluster_id");
  const [sortOrder, setSortOrder] = useState("asc");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  const [messageTimeline, setMessageTimeline] = useState([]);
  const [authorOptions, setAuthorOptions] = useState([]);
  const [selectedAuthor, setSelectedAuthor] = useState("All");

  const refreshData = async () => {
    setLoading(true);
    try {
      const res = await axios.get("/api/faq/clusters/");
      const allClusters = res.data?.clusters || [];
      const mapPoints = res.data?.cluster_map || [];

      const enrichedMap = mapPoints.map((point) => {
        const meta = allClusters.find((c) => c.cluster_id === point.label) || {};
        return {
          ...point,
          top_message: meta.top_message,
          sentiment: meta.sentiment,
          coverage: meta.coverage,
          resolution_score: meta.resolution_score,
        };
      });

      setClusters(allClusters);
      setClusterMap(enrichedMap);
    } catch (err) {
      console.error("Failed to load clusters:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchProcessGaps = async () => {
    try {
      const res = await axios.get("/api/faq/top-process-gaps/");
      setProcessGaps(res.data.process_gaps || []);
    } catch (e) {
      console.error("Failed to fetch process gaps", e);
    }
  };

  const fetchMessageTimeline = async () => {
    try {
      const res = await axios.get("/api/messages/?ordering=created_at");
      const messages = res.data || [];

      const timeline = {};
      const authors = new Set();

      messages.forEach((msg) => {
        const date = msg.created_at.slice(0, 10);
        const author = msg.author_name || "Unknown";
        const sentiment = msg.sentiment || "neutral";

        authors.add(author);

        if (!timeline[date]) {
          timeline[date] = { date, positive: 0, neutral: 0, negative: 0 };
        }

        if (sentiment === "positive") timeline[date].positive += 1;
        else if (sentiment === "negative") timeline[date].negative += 1;
        else timeline[date].neutral += 1;
      });

      setMessageTimeline(Object.values(timeline));
      setAuthorOptions(["All", ...Array.from(authors)]);
    } catch (err) {
      console.error("Failed to fetch messages:", err);
    }
  };

  useEffect(() => {
    refreshData();
    fetchProcessGaps();
    fetchMessageTimeline();
  }, []);

  const handleOpenModal = (cluster) => {
    setSelectedCluster(cluster);
    setIsOpen(true);
  };

  const handleOpenMessagesModal = (cluster) => {
    setSelectedCluster(cluster);
    setShowMessagesModal(true);
  };

  const handleSelectClusterFromMap = (clusterId) => {
    const target = clusters.find((c) => c.cluster_id === clusterId);
    if (target) {
      setSelectedCluster(target);
      const indexInSorted = sortedClusters.findIndex(c => c.cluster_id === clusterId);
      const page = Math.floor(indexInSorted / itemsPerPage) + 1;
      setCurrentPage(page);
      setIsOpen(true);
    }
  };

  const filteredClusters = clusters.filter((c) =>
    c.top_message.toLowerCase().includes(search.toLowerCase())
  );

  const sortedClusters = [...filteredClusters].sort((a, b) => {
    const valA = a[sortBy];
    const valB = b[sortBy];
    if (typeof valA === "number") {
      return sortOrder === "asc" ? valA - valB : valB - valA;
    } else {
      return sortOrder === "asc"
        ? String(valA).localeCompare(String(valB))
        : String(valB).localeCompare(String(valA));
    }
  });

  const paginatedClusters = sortedClusters.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const faqSuggestions = clusters
    .filter((c) => c.faq_suggestion && c.faq_suggestion.question)
    .map((c) => ({
      clusterId: c.cluster_id,
      question: c.faq_suggestion.question,
      answer: c.faq_suggestion.answer,
      reason: c.resolution_reason,
      coverage: c.coverage,
      matched_faq: c.matched_faq,
      resolution_score: c.resolution_score,
    }));

  const filteredTimeline = selectedAuthor === "All"
    ? messageTimeline
    : messageTimeline.filter((msg) => msg.author === selectedAuthor);

  useEffect(() => {
    if (selectedRef.current) {
      selectedRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [selectedClusterId]);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-10">
      {/* Top Bar */}
      <div className="flex justify-between items-center mb-4">
        <div className="flex gap-2 items-center">
          <DashboardHelpPanel />
          {user?.is_admin && <TriggerPipelineButton onPipelineComplete={refreshData} />}
        </div>
      </div>

      {selectedCluster && (
        <ClusterMessagesModal
          open={showMessagesModal}
          onClose={() => setShowMessagesModal(false)}
          cluster={selectedCluster}
        />
      )}

      {loading ? (
        <p className="text-gray-500">Loading...</p>
      ) : (
        <>
          <TrendingTopicsLeaderboard />

          <CardWrapper title="FAQ Deflection Performance">
            <FAQDeflectionTrends />
          </CardWrapper>

          <CardWrapper title="Top Process Gaps">
            <TopProcessGapsPanel data={processGaps} />
          </CardWrapper>

          {/* Summary Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <MetricCard label="Clusters" value={clusters.length} />
            <MetricCard
              label="Unmatched"
              value={clusters.filter((c) => c.coverage === "Not covered").length}
            />
            <MetricCard
              label="Coverage %"
              value={
                ((clusters.filter((c) => c.coverage === "Fully").length / clusters.length) * 100).toFixed(1) + "%"
              }
            />
            <MetricCard
              label="Avg. Resolution Score"
              value={
                (
                  clusters.reduce((sum, c) => sum + (c.resolution_score || 0), 0) / clusters.length
                ).toFixed(2)
              }
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <CardWrapper title="Sentiment Distribution">
              <SentimentBarChart clusters={clusters} />
            </CardWrapper>
            <CardWrapper title="FAQ Match Quality">
              <CoveragePieChart clusters={clusters} />
            </CardWrapper>
            <CardWrapper title="Resolution Score Distribution">
              <ResolutionScoreBarChart clusters={clusters} />
            </CardWrapper>
            <CardWrapper title="Avg. Resolution Over Time">
              <ResolutionTimelineChart clusters={clusters} />
            </CardWrapper>
          </div>

          <CardWrapper title="Top FAQ Gaps by Topic">
            <TopGapsByTopicChart clusters={clusters} />
          </CardWrapper>

          <CardWrapper title="FAQ Suggestions">
            <FAQImprovementPanel suggestions={faqSuggestions} />
          </CardWrapper>

          <CardWrapper title="Cluster Map">
            <ClusterMapChart data={clusterMap} onSelectCluster={handleSelectClusterFromMap} />
          </CardWrapper>

          <CardWrapper title="Message Sentiment Over Time">
            <div className="mb-4 w-1/3">
              <Select value={selectedAuthor} onChange={(e) => setSelectedAuthor(e.target.value)}>
                {authorOptions.map((a) => (
                  <option key={a} value={a}>
                    {a}
                  </option>
                ))}
              </Select>
            </div>
            <MessageSentimentTimelineChart data={filteredTimeline} />
          </CardWrapper>

          <div className="flex justify-between items-center mb-4">
            <input
              type="text"
              placeholder="Search top message..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="border p-2 rounded w-1/3"
            />
          </div>

          <CardWrapper title="All Clusters">
            <ClusterTable
              clusters={paginatedClusters}
              selectedClusterId={selectedClusterId}
              selectedRef={selectedRef}
              onReview={handleOpenModal}
              onViewMessages={handleOpenMessagesModal}
              currentPage={currentPage}
              setCurrentPage={setCurrentPage}
              totalCount={sortedClusters.length}
              itemsPerPage={itemsPerPage}
              sortBy={sortBy}
              sortOrder={sortOrder}
              setSortBy={setSortBy}
              setSortOrder={setSortOrder}
            />
          </CardWrapper>
        </>
      )}

      {selectedCluster && (
        <FAQMatchModal open={isOpen} onClose={() => setIsOpen(false)} cluster={selectedCluster} />
      )}
    </div>
  );
}
