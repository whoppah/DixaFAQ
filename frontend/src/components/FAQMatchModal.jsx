import React from "react";
import { Modal } from "flowbite-react";

export default function FAQMatchModal({ open, onClose, cluster }) {
  return (
    <Modal show={open} onClose={onClose} size="lg">
      <Modal.Header>
        Cluster {cluster.clusterId} — GPT Evaluation
      </Modal.Header>
      <Modal.Body>
        <div className="space-y-4">
          <p>
            <strong>Top Message:</strong><br />
            {cluster.topMessage}
          </p>
          <p>
            <strong>Matched FAQ:</strong><br />
            {cluster.matchedFaq}
          </p>
          <p>
            <strong>Similarity Score:</strong> {(cluster.similarity * 100).toFixed(1)}%
          </p>
          <div className="p-4 bg-gray-100 border rounded-md">
            <strong>GPT Evaluation:</strong>
            <p>{cluster.gptEvaluation}</p>
          </div>
        </div>
      </Modal.Body>
    </Modal>
  );
}
