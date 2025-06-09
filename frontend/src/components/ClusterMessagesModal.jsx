// ClusterMessagesModal.jsx
import React from "react";
import { Modal } from "flowbite-react";

export default function ClusterMessagesModal({ open, onClose, cluster }) {
  return (
    <Modal show={open} onClose={onClose} size="lg">
      <Modal.Header>Cluster {cluster.clusterId} — All Messages</Modal.Header>
      <Modal.Body>
        <ul className="space-y-2">
          {cluster.messages.map((msg, idx) => (
            <li key={idx} className="p-2 bg-gray-100 rounded">{msg}</li>
          ))}
        </ul>
      </Modal.Body>
    </Modal>
  );
}
