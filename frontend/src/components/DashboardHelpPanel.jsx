//frontend/src/components/DashboardHelpPanel.jsx
import React, { useState } from "react";
import { HiOutlineInformationCircle } from "react-icons/hi";
import { Modal, Button } from "flowbite-react";

export default function DashboardHelpPanel() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button
        size="xs"
        onClick={() => setOpen(true)}
        className="flex items-center gap-1 border border-blue-600 text-blue-600 hover:bg-blue-50"
      >
        <HiOutlineInformationCircle className="h-4 w-4" />
        Help
      </Button>

      <Modal show={open} onClose={() => setOpen(false)} size="lg">
        <Modal.Header>Dashboard Chart Explanations</Modal.Header>
        <Modal.Body>
          <div className="max-h-[70vh] overflow-y-auto space-y-6 text-sm text-gray-800">
            <section>
              <strong>FAQ Coverage & Deflection</strong>
              <p>
                Understand which FAQs successfully deflect support load and which ones need improvement.
              </p>
              <ul className="list-disc ml-5 mt-2 text-gray-600">
                <li><em>High deflection + low score</em>: Popular FAQ, but users are still confused.</li>
                <li><em>Low deflection + high score</em>: Accurate FAQ that isn’t seen enough.</li>
                <li><em>Partially covered topics</em>: Users get incomplete help — revise the answer.</li>
              </ul>
            </section>

            <section>
              <strong>Process Gaps</strong>
              <p>Questions that aren’t covered by any FAQ often signal unclear processes or documentation gaps.</p>
              <ul className="list-disc ml-5 mt-2 text-gray-600">
                <li>Use these to improve SOPs or write new FAQs.</li>
              </ul>
            </section>

            <section>
              <strong>Top Questions (High Volume)</strong>
              <p>Shows most frequent clusters. Prioritize missing or weak FAQ matches.</p>
            </section>

            <section>
              <strong>Weak FAQ Matches</strong>
              <p>GPT says the bot answered, but user’s issue wasn't resolved. Suggested FAQs fix this.</p>
            </section>

            <section>
              <strong>FAQ Mismatch Analysis</strong>
              <ul className="list-disc ml-5 mt-2 text-gray-600">
                <li><em>Cluster Map</em>: Explore topics visually — find niche/emerging ones.</li>
                <li><em>Top Gaps by Topic</em>: Thematic blind spots (e.g., shipping, refunds).</li>
                <li><em>Suggested FAQs</em>: Proposed improvements by GPT.</li>
              </ul>
            </section>
          </div>
        </Modal.Body>
        <Modal.Footer>
          <Button onClick={() => setOpen(false)}>Close</Button>
        </Modal.Footer>
      </Modal>
    </>
  );
}
