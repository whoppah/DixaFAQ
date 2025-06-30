//frontend/src/pages/ClusterDashboard.jsx
import React, { useState, useEffect } from "react";
import axios from "../lib/axios"; 
import { useNavigate, Link } from "react-router-dom";
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



export default function ClusterDashboard() {
  const [clusters, setClusters] = useState([]);
  const [clusterMap, setClusterMap] = useState([]);
  const [selectedCluster, setSelectedCluster] = useState(null);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);
  const [showInfoModal, setShowInfoModal] = useState(false);

  const navigate = useNavigate();

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

  //const fetchUser = async () => {
    //try {
      //const res = await axios.get("/api/faq/current-user-info/");;
      //setUser(res.data);
    //} catch (err) {
      //console.warn("Not authenticated, redirecting...");
    //  navigate("/login");
    //}
  //};
  
  const fetchUser = async () => {
    setUser({ is_admin: true }); // to show the start pipeline button superadmin
  };

  const [processGaps, setProcessGaps] = useState([]);

  const fetchProcessGaps = async () => {
    try {
      const res = await axios.get("/api/faq/top-process-gaps/");
      setProcessGaps(res.data.process_gaps || []);
    } catch (e) {
      console.error("Failed to fetch process gaps", e);
    }
  };
  
  useEffect(() => {
    fetchUser();
    refreshData();
    fetchProcessGaps();   
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
      {/* Info button */}
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
          <div className="space-y-4 text-sm text-gray-800">
            <div>
              <strong>FAQ Deflection Performance</strong>
              <p>Shows how well each FAQ reduces support load over time.</p>
            </div>
            <div>
              <strong>Trending Questions</strong>
              <p>Keywords that have surged in volume this week compared to last week.</p>
            </div>
            <div>
              <strong>Resolution Score Timeline</strong>
              <p>Tracks the average resolution score per day over recent messages.</p>
            </div>
            <div>
              <strong>Sentiment Distribution</strong>
              <p>Shows how many clusters are positive, neutral, or negative in tone.</p>
            </div>
            <div>
              <strong>Cluster Map</strong>
              <p>2D representation of clusters. Each point is a group of related messages.</p>
            </div>
            <div>
              <strong>Top Process Gaps</strong>
              <p>Topics with high volume but low FAQ coverage.</p>
            </div>
          </div>
        </Modal.Body>
        <Modal.Footer>
          <Button onClick={() => setShowInfoModal(false)}>Close</Button>
        </Modal.Footer>
      </Modal>

       {/*<h1 className="text-4xl font-bold text-gray-800">Dashboard</h1>*/}

      {user?.is_admin && (
        <TriggerPipelineButton onPipelineComplete={refreshData} isAdmin={true} />
      )}

      {loading ? (
        <p className="text-gray-500">Loading...</p>
      ) : (
        <>
          {/* Trending Leaderboard */}
          <TrendingTopicsLeaderboard />

          {/* FAQ Deflection performance */}
          <CardWrapper title="FAQ Deflection Performance">
            <FAQDeflectionTrends />
          </CardWrapper>

          {/* Top Process Gaps Panel */}
          <CardWrapper title="Top Process Gaps">
            <TopProcessGapsPanel data={processGaps} />
          </CardWrapper>


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

            <CardWrapper title="Avg. Resolution Score Over Time">
              <ResolutionTimelineChart clusters={clusters} />
            </CardWrapper>
          </div>

          <CardWrapper title="Top FAQ Gaps by Topic">
            <TopGapsByTopicChart clusters={clusters} />
          </CardWrapper>

          <CardWrapper title="FAQ Improvement Suggestions">
            <FAQImprovementPanel suggestions={faqSuggestions} />
          </CardWrapper>

          <CardWrapper title="Cluster Map">
            <ClusterMapChart data={clusterMap} onSelectCluster={handleSelectClusterFromMap} />
          </CardWrapper>

          <CardWrapper title="Cluster Frequency Timeline">
            <ClusterFrequencyChart data={getSimulatedTimeline(clusters)} />
          </CardWrapper>

          <CardWrapper title="All Clusters">
            <ClusterTable clusters={clusters} onReview={handleOpenModal} />
          </CardWrapper>
        </>
      )}

      {selectedCluster && (
        <FAQMatchModal open={isOpen} onClose={() => setIsOpen(false)} cluster={selectedCluster} />
      )}
    </div>
  );
}
