//frontend/src/components/TrendingTopicsLeaderboard.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";
import { Table, Tooltip } from "flowbite-react";
import CardWrapper from "../components/CardWrapper";
import { ArrowUpRight, ArrowDownRight } from "lucide-react";
import ClusterMessagesModal from "./ClusterMessagesModal"; 

export default function TrendingTopicsLeaderboard() {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedKeyword, setSelectedKeyword] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const fetchLeaderboard = async () => {
    setLoading(true);
    try {
      const res = await axios.get("/api/faq/trending-leaderboard/");
      setLeaderboard(res.data.leaderboard || []);
    } catch (error) {
      console.error("Failed to load trending leaderboard", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeaderboard();
  }, []);

  const getChangeColor = (change) => {
    if (change > 0) return "text-green-600";
    if (change < 0) return "text-red-500";
    return "text-gray-400";
  };

  const getChangeIcon = (change) => {
    if (change > 0) return <ArrowUpRight size={16} />;
    if (change < 0) return <ArrowDownRight size={16} />;
    return null;
  };

  return (
    <CardWrapper title="Trending Questions">
      {loading ? (
        <p className="text-gray-500">Loading trending keywords...</p>
      ) : leaderboard.length === 0 ? (
        <p className="text-gray-500">No trending data found for this week.</p>
      ) : (
        <div className="overflow-x-auto">
          <Table striped hoverable>
            <Table.Head>
              <Table.HeadCell>Keyword</Table.HeadCell>
              <Table.HeadCell>Mentions</Table.HeadCell>
              <Table.HeadCell>Prev Week</Table.HeadCell>
              <Table.HeadCell>Change</Table.HeadCell>
              <Table.HeadCell>Sentiment</Table.HeadCell>
            </Table.Head>
            <Table.Body className="divide-y">
              {leaderboard.map((item, idx) => (
                <Table.Row key={idx}>
                  <Table.Cell className="font-medium text-blue-600 cursor-pointer"
                    onClick={() => {
                      setSelectedKeyword(item.keyword);
                      setShowModal(true);
                    }}
                  >
                    {item.keyword}
                  </Table.Cell>
                  <Table.Cell>{item.count}</Table.Cell>
                  <Table.Cell>{item.previous_count}</Table.Cell>
                  <Table.Cell className={getChangeColor(item.change)}>
                    <div className="flex items-center gap-1">
                      {getChangeIcon(item.change)}
                      {item.change > 0 ? `+${item.change}` : item.change}
                    </div>
                  </Table.Cell>
                  <Table.Cell>
                    <Tooltip
                      content={
                        `Pos: ${item.sentiment?.positive || 0}, ` +
                        `Neu: ${item.sentiment?.neutral || 0}, ` +
                        `Neg: ${item.sentiment?.negative || 0}`
                      }
                    >
                      <span className="text-xs">
                        {item.sentiment?.score > 0
                          ? "Positive"
                          : item.sentiment?.score < 0
                          ? "Negative"
                          : "Neutral"}
                      </span>
                    </Tooltip>
                  </Table.Cell>
                </Table.Row>
              ))}
            </Table.Body>
          </Table>
        </div>
      )}

      {/* Optional modal showing related messages per keyword */}
      {showModal && selectedKeyword && (
        <ClusterMessagesModal
          open={showModal}
          onClose={() => setShowModal(false)}
          cluster={{
            clusterId: selectedKeyword,
            messages: leaderboard
              .find((k) => k.keyword === selectedKeyword)
              ?.messages || [],
          }}
        />
      )}
    </CardWrapper>
  );
}
