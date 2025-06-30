//frontend/src/pages/ClusterDashboard.jsx
import React, { useState, useEffect, useRef} from "react";
import axios from "../lib/axios";
import { useNavigate } from "react-router-dom";
import { HiOutlineInformationCircle } from "react-icons/hi";
import { Modal, Button } from "flowbite-react";

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
import FAQDeflectionTrends from "../components/FAQDeflectionTrends";
import TrendingTopicsLeaderboard from "../components/TrendingTopicsLeaderboard";
import TopProcessGapsPanel from "../components/TopProcessGapsPanel";
import ClusterMessagesModal from "../components/ClusterMessagesModal";

export default function ClusterDashboard() {
  const [clusters, setClusters] = useState([]);
  const [clusterMap, setClusterMap] = useState([]);
  const [selectedCluster, setSelectedCluster] = useState(null);
  const selectedClusterId = selectedCluster?.cluster_id || null;

  const [isOpen, setIsOpen] = useState(false);
  const [showMessagesModal, setShowMessagesModal] = useState(false);
  const [showInfoModal, setShowInfoModal] = useState(false);
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

  const refreshData = async () => {
    setLoading(true);
    try {
      const res = await axios.get("/api/faq/clusters/");
      setClusters(res.data?.clusters || []);
      setClusterMap(res.data?.cluster_map || []);
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

  useEffect(() => {
    refreshData();
    fetchProcessGaps();
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

  const getSimulatedTimeline = (clusters) =>
    clusters.map((c, i) => ({
      cluster_id: c.cluster_id,
      date:
        c.created_at ||
        new Date(Date.now() - i * 86400000).toISOString().slice(0, 10),
    }));
  useEffect(() => {
    if (selectedRef.current) {
      selectedRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [selectedClusterId]);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-10">
      {/* Info Button */}
      <div className="flex justify-end mb-4">
        <button
          className="inline-flex items-center text-sm text-blue-600 border border-blue-600 px-3 py-1 rounded hover:bg-blue-50 transition"
          onClick={() => setShowInfoModal(true)}
        >
          <HiOutlineInformationCircle className="mr-1 h-4 w-4" />
          Help: Chart Explanations
        </button>
      </div>

      {/* Modal */}
      <Modal show={showInfoModal} onClose={() => setShowInfoModal(false)} size="lg">
        <Modal.Header>Dashboard Chart Explanations</Modal.Header>
        <Modal.Body>
          <div className="max-h-[70vh] overflow-y-auto space-y-6 text-sm text-gray-800">
            
            <div>
              <strong>FAQ Coverage & Deflection</strong>
              <p>Understand which FAQs successfully deflect support load and which ones need improvement.</p>
              <ul className="list-disc ml-5 mt-2 text-gray-600">
                <li><em>High deflection + low score</em>: Popular FAQ, but users are still confused — needs better wording or structure.</li>
                <li><em>Low deflection + high score</em>: Accurate FAQ that isn't being surfaced enough — improve linking or chatbot intent detection.</li>
                <li><em>Partially covered topics</em>: Users get incomplete help — revise the answer or split it into clearer FAQs.</li>
              </ul>
            </div>
      
            <div>
              <strong>Process Gaps</strong>
              <p>Highlights frequent questions that aren't addressed in any FAQ. These likely point to unclear processes or missing documentation.</p>
              <ul className="list-disc ml-5 mt-2 text-gray-600">
                <li>Use these clusters to write new internal SOPs or customer-facing help articles.</li>
                <li>Each gap includes examples of real user questions — use them to write better, targeted answers.</li>
              </ul>
            </div>
      
            <div>
              <strong>Top Questions (High Volume)</strong>
              <p>Clusters sorted by volume show the most common questions your users ask.</p>
              <ul className="list-disc ml-5 mt-2 text-gray-600">
                <li>If no FAQ is matched or the score is low, you're missing key coverage in your help center.</li>
                <li>These clusters should be a priority for new or improved FAQs.</li>
              </ul>
            </div>
      
            <div>
              <strong>Weak FAQ Matches</strong>
              <p>These are cases where the chatbot gives an answer, but GPT believes it does not resolve the user's issue.</p>
              <ul className="list-disc ml-5 mt-2 text-gray-600">
                <li>Look at the GPT score and justification to understand what’s missing.</li>
                <li>Suggested FAQs offer a rewrite tailored to the user's actual question.</li>
              </ul>
            </div>
      
            <div>
              <strong>FAQ Mismatch Analysis</strong>
              <p>This cross-section of coverage gaps, weak matches, and suggested questions shows what’s missing in your FAQ system.</p>
              <ul className="list-disc ml-5 mt-2 text-gray-600">
                <li><em>Cluster Map</em>: Explore topic groupings visually — select outliers or isolated dots to find emerging or niche topics.</li>
                <li><em>Top Gaps by Topic</em>: Reveals thematic blind spots — e.g., delivery, refunds, onboarding.</li>
                <li><em>Suggested FAQs</em>: Automatically proposed Q&As for poorly answered or uncovered topics.</li>
              </ul>
            </div>
      
          </div>
        </Modal.Body>
        <Modal.Footer>
          <Button onClick={() => setShowInfoModal(false)}>Close</Button>
        </Modal.Footer>
      </Modal>

      {selectedCluster && (
        <ClusterMessagesModal
          open={showMessagesModal}
          onClose={() => setShowMessagesModal(false)}
          cluster={selectedCluster}
        />
      )}
      {/*<h1 className="text-4xl font-bold text-gray-800">Dashboard</h1>*/}
      {user?.is_admin && <TriggerPipelineButton onPipelineComplete={refreshData} />}

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

          <CardWrapper title="Cluster Timeline">
            <ClusterFrequencyChart data={getSimulatedTimeline(clusters)} />
          </CardWrapper>

          {/* Search and Sort Controls */}
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
