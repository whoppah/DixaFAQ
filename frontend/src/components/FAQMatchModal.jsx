//frontend/src/components/FaAQMatchModal.jsx
import React from "react";
import { Modal } from "flowbite-react";

export default function FAQMatchModal({ open, onClose, cluster }) {
  return (
    <Modal show={open} onClose={onClose} size="lg">
      <Modal.Header>
        Cluster {cluster.clusterId} — GPT Evaluation
      </Modal.Header>
      <Modal.Body>
        <div className="space-y-4 text-sm text-gray-800">
          <div>
            <strong className="text-gray-600">Top Message:</strong>
            <p>{cluster.topMessage}</p>
          </div>
          <div>
            <strong className="text-gray-600">Matched FAQ:</strong>
            <p>{cluster.matchedFaq}</p>
          </div>
          <div>
            <strong className="text-gray-600">Similarity Score:</strong>
            <p>{(cluster.similarity * 100).toFixed(1)}%</p>
          </div>
          <div className="p-4 bg-gray-100 border rounded-md">
            <strong className="block mb-1 text-gray-700">GPT Evaluation:</strong>
            <p>{cluster.gptEvaluation}</p>
          </div>
        </div>
      </Modal.Body>
    </Modal>
  );
}
