//frontend/src/components/TriggerPipelineButton.jsx
import React, { useState } from "react";

const TriggerPipelineButton = () => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleTrigger = async () => {
    setLoading(true);
    try {
      const response = await fetch("/api/trigger-pipeline/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
      });

      const data = await response.json();
      setStatus(data.status || "Pipeline triggered");
    } catch (err) {
      setStatus("Error triggering pipeline");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={handleTrigger} disabled={loading}>
        {loading ? "Running..." : "Trigger Pipeline"}
      </button>
      {status && <p>{status}</p>}
    </div>
  );
};

export default TriggerPipelineButton;
