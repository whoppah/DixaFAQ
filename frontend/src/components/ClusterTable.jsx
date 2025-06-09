//frontend/src/components/ClusterTable.jsx
import React from "react";
import { Table, Button, Tooltip } from "flowbite-react";

export default function ClusterTable({ clusters, onReview }) {
  return (
    <div className="overflow-x-auto">
      <Table hoverable striped>
        <Table.Head>
          <Table.HeadCell>Cluster ID</Table.HeadCell>
          <Table.HeadCell># Messages</Table.HeadCell>
          <Table.HeadCell>Top Message</Table.HeadCell>
          <Table.HeadCell>Matched FAQ</Table.HeadCell>
          <Table.HeadCell>Similarity</Table.HeadCell>
          <Table.HeadCell>Sentiment</Table.HeadCell>
          <Table.HeadCell>Summary</Table.HeadCell>
          <Table.HeadCell>Keywords</Table.HeadCell>
          <Table.HeadCell>Review</Table.HeadCell>
        </Table.Head>
        <Table.Body className="divide-y">
          {clusters.map((cluster) => (
            <Table.Row key={cluster.cluster_id}>
              <Table.Cell>{cluster.cluster_id}</Table.Cell>
              <Table.Cell>{cluster.message_count}</Table.Cell>
              <Table.Cell className="max-w-xs truncate">{cluster.top_message}</Table.Cell>
              <Table.Cell className="max-w-xs truncate">{cluster.matched_faq}</Table.Cell>
              <Table.Cell>{(cluster.similarity * 100).toFixed(1)}%</Table.Cell>
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
                <Button onClick={() => onReview(cluster)}>Review</Button>
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table>
    </div>
  );
}
