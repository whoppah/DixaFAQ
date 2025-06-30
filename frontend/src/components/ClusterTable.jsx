// frontend/src/components/ClusterTable.jsx
import React from "react";
import { Table, Button, Tooltip } from "flowbite-react";

export default function ClusterTable({
  clusters,
  onReview,
  onViewMessages,
  currentPage,
  setCurrentPage,
  totalCount,
  itemsPerPage,
  sortBy,
  sortOrder,
  setSortBy,
  setSortOrder,
  selectedClusterId,      
  selectedRef  
}) {
  const handleSort = (column) => {
    if (sortBy === column) {
      setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortBy(column);
      setSortOrder("asc");
    }
  };

  const renderSortArrow = (column) => {
    if (sortBy !== column) return null;
    return sortOrder === "asc" ? " ▲" : " ▼";
  };

  const totalPages = Math.ceil(totalCount / itemsPerPage);

  return (
    <div className="overflow-x-auto space-y-4">
      <Table hoverable striped>
        <Table.Head>
          <Table.HeadCell onClick={() => handleSort("cluster_id")} className="cursor-pointer">
            Cluster ID{renderSortArrow("cluster_id")}
          </Table.HeadCell>
          <Table.HeadCell onClick={() => handleSort("message_count")} className="cursor-pointer">
            # Messages{renderSortArrow("message_count")}
          </Table.HeadCell>
          <Table.HeadCell>Messages</Table.HeadCell>
          <Table.HeadCell onClick={() => handleSort("top_message")} className="cursor-pointer">
            Top Message{renderSortArrow("top_message")}
          </Table.HeadCell>
          <Table.HeadCell>Matched FAQ</Table.HeadCell>
          <Table.HeadCell onClick={() => handleSort("similarity")} className="cursor-pointer">
            Similarity{renderSortArrow("similarity")}
          </Table.HeadCell>
          <Table.HeadCell onClick={() => handleSort("sentiment")} className="cursor-pointer">
            Sentiment{renderSortArrow("sentiment")}
          </Table.HeadCell>
          <Table.HeadCell>Summary</Table.HeadCell>
          <Table.HeadCell>Keywords</Table.HeadCell>
          <Table.HeadCell>Review</Table.HeadCell>
        </Table.Head>
        <Table.Body className="divide-y">
          {clusters.map((cluster) => (
            <Table.Row
              key={cluster.cluster_id}
              ref={cluster.cluster_id === selectedClusterId ? selectedRef : null}
              className={cluster.cluster_id === selectedClusterId ? "bg-blue-50" : ""}
            >
              <Table.Cell>{cluster.cluster_id}</Table.Cell>
              <Table.Cell>{cluster.message_count}</Table.Cell>
              <Table.Cell>
                <Button size="xs" onClick={() => onViewMessages(cluster)}>
                  View
                </Button>
              </Table.Cell>
              <Table.Cell className="max-w-xs truncate">{cluster.top_message}</Table.Cell>
              <Table.Cell className="max-w-xs truncate">
                {typeof cluster.matched_faq === "object" && cluster.matched_faq?.question
                  ? cluster.matched_faq.question
                  : String(cluster.matched_faq)}
              </Table.Cell>
              <Table.Cell>
                {typeof cluster.similarity === "number"
                  ? `${(cluster.similarity * 100).toFixed(1)}%`
                  : "N/A"}
              </Table.Cell>
              <Table.Cell>{cluster.sentiment}</Table.Cell>
              <Table.Cell className="max-w-xs truncate">{cluster.summary}</Table.Cell>
              <Table.Cell>
                <Tooltip content={cluster.keywords.join(", ")}>
                  <span>
                    {cluster.keywords.slice(0, 3).join(", ")}
                    {cluster.keywords.length > 3 ? "..." : ""}
                  </span>
                </Tooltip>
              </Table.Cell>
              <Table.Cell>
                <Button size="xs" onClick={() => onReview(cluster)}>
                  Review
                </Button>
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table>

      {/* Pagination Controls */}
      <div className="flex justify-center items-center gap-4 mt-2">
        <Button
          size="xs"
          disabled={currentPage === 1}
          onClick={() => setCurrentPage((p) => p - 1)}
        >
          Previous
        </Button>
        <span className="text-sm">Page {currentPage} of {totalPages}</span>
        <Button
          size="xs"
          disabled={currentPage >= totalPages}
          onClick={() => setCurrentPage((p) => p + 1)}
        >
          Next
        </Button>
      </div>
    </div>
  );
}
