//frontend/src/components/ClusterTable.jsx
import React from "react";
import { Table, Button } from "flowbite-react";

export default function ClusterTable({ clusters, onReview }) {
  return (
    <Table hoverable striped>
      <Table.Head>
        <Table.HeadCell>Cluster ID</Table.HeadCell>
        <Table.HeadCell># Messages</Table.HeadCell>
        <Table.HeadCell>Top Message</Table.HeadCell>
        <Table.HeadCell>Matched FAQ</Table.HeadCell>
        <Table.HeadCell>Similarity</Table.HeadCell>
        <Table.HeadCell>Review</Table.HeadCell>
      </Table.Head>
      <Table.Body className="divide-y">
        {clusters.map((cluster) => (
          <Table.Row key={cluster.clusterId}>
            <Table.Cell>{cluster.clusterId}</Table.Cell>
            <Table.Cell>{cluster.messageCount}</Table.Cell>
            <Table.Cell>{cluster.topMessage}</Table.Cell>
            <Table.Cell>{cluster.matchedFaq}</Table.Cell>
            <Table.Cell>{(cluster.similarity * 100).toFixed(1)}%</Table.Cell>
            <Table.Cell>
              <Button onClick={() => onReview(cluster)}>Review</Button>
            </Table.Cell>
          </Table.Row>
        ))}
      </Table.Body>
    </Table>
  );
}
