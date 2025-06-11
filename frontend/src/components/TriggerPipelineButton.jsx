//frontend/src/components/TriggerPipelineButton.jsx
import React, { useState } from "react";

export default function TriggerPipelineButton() {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");

  const triggerPipeline = async () => {
    setLoading(true);
    setStatus("");
    try {
      const res = await fetch("/api/trigger-pipeline/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      const data = await res.json();
      setStatus(data.status || "Pipeline triggered");
    } catch (error) {
      console.error("Failed to trigger pipeline:", error);
      setStatus("❌ Failed to trigger pipeline");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-2">
      <button
        onClick={triggerPipeline}
        disabled={loading}
        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded shadow"
      >
        {loading ? "Running pipeline..." : "🚀 Trigger Data Pipeline"}
      </button>
      {status && <span className="text-sm text-gray-700">{status}</span>}
    </div>
  );
}
