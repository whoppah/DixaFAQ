import React, { useState, useEffect } from "react";
import { Table, Button, Modal } from "flowbite-react";
import FAQMatchModal from "../components/FAQMatchModal";

const mockData = [
  {
    clusterId: 0,
    messageCount: 14,
    topMessage: "Hoe kan ik mijn bestelling volgen?",
    matchedFaq: "Hoe werkt verzending via Brenger?",
    similarity: 0.87,
    gptEvaluation: "Partially covered – the FAQ mentions shipping, but not tracking.",
  },
  {
    clusterId: 1,
    messageCount: 9,
    topMessage: "Wanneer ontvang ik mijn betaling?",
    matchedFaq: "Wanneer word ik uitbetaald?",
    similarity: 0.95,
    gptEvaluation: "Fully covered – FAQ clearly explains payout schedule.",
  },
];

export default function ClusterDashboard() {
  const [selectedCluster, setSelectedCluster] = useState(null);
  const [isOpen, setIsOpen] = useState(false);

  const handleOpenModal = (cluster) => {
    setSelectedCluster(cluster);
    setIsOpen(true);
  };

  return (
    <div className="container mx-auto px-4 py-6">
      <h1 className="text-3xl font-bold mb-6">📊 Cluster Match Dashboard</h1>

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
          {mockData.map((cluster) => (
            <Table.Row key={cluster.clusterId}>
              <Table.Cell>{cluster.clusterId}</Table.Cell>
              <Table.Cell>{cluster.messageCount}</Table.Cell>
              <Table.Cell>{cluster.topMessage}</Table.Cell>
              <Table.Cell>{cluster.matchedFaq}</Table.Cell>
              <Table.Cell>{(cluster.similarity * 100).toFixed(1)}%</Table.Cell>
              <Table.Cell>
                <Button onClick={() => handleOpenModal(cluster)}>Review</Button>
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table>

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
