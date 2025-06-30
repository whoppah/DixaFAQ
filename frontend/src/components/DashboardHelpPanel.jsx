// frontend/src/components/DashboardHelpPanel.jsx
import React, { useState } from "react";
import { HiOutlineInformationCircle } from "react-icons/hi";
import { Modal, Button } from "flowbite-react";

export default function DashboardHelpPanel() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        className="inline-flex items-center text-sm text-white bg-blue-500 hover:bg-blue-600 px-3 py-1 rounded shadow transition"
        onClick={() => setOpen(true)}
      >
        <HiOutlineInformationCircle className="mr-1 h-4 w-4" />
        Help
      </button>

      <Modal show={open} onClose={() => setOpen(false)} size="lg">
        <Modal.Header>Dashboard Component Guide</Modal.Header>
        <Modal.Body>
          <div className="max-h-[70vh] overflow-y-auto space-y-6 text-sm text-gray-800">
            {/* COMPONENT-BY-COMPONENT DESCRIPTION */}
            <section>
              <strong>Cluster Map</strong>
              <p>Visualizes each message cluster as a point in 2D space, colored by coverage status.</p>
              <p>**Backend Source**: `/api/faq/clusters/` → `cluster_map` data.</p>
              <p>Each point includes:</p>
              <ul className="list-disc ml-5 mt-1">
                <li>Cluster ID</li>
                <li>Top Message</li>
                <li>Sentiment (computed from messages)</li>
                <li>Coverage status ("Fully", "Partially", "Not")</li>
                <li>Resolution Score (from GPT)</li>
              </ul>
              <p><strong>Interpretation:</strong> Click a cluster to drill into FAQs and review resolution quality.</p>
            </section>

            <section>
              <strong>Message Sentiment Over Time</strong>
              <p>Tracks daily counts of messages classified as Positive, Neutral, or Negative.</p>
              <p>**Backend Source**: `/api/faq/dashboard-clusters-with-messages/` → timeline messages.</p>
              <p><strong>Sentiment Inference:</strong> each message is labeled using Hugging Face model (`sentiment.py`).</p>
              <p><strong>Interpretation:</strong> Spikes in Negative messages may indicate issues in support or content gaps.</p>
            </section>

            <section>
              <strong>Coverage Pie Chart</strong>
              <p>Shows how many clusters are Fully, Partially, or Not covered by an FAQ.</p>
              <p>**Backend Source**: `/api/faq/clusters/` → `coverage` field for each cluster.</p>
              <p><strong>GPT Prompt:</strong></p>
              <pre className="bg-gray-100 p-2 rounded text-xs whitespace-pre-wrap">
{`System:
Evaluate if the matched FAQ fully, partially, or doesn't address the question.
User:
Top message: "{top_message}"
Matched FAQ: "{faq.question}"
Answer: "{faq.answer}"`}
              </pre>
              <p><strong>Interpretation:</strong> Aim to minimize "Not covered" cases by revising or creating FAQs.</p>
            </section>

            <section>
              <strong>Sentiment Bar Chart</strong>
              <p>Aggregates the sentiment of each cluster (positive/neutral/negative).</p>
              <p>**Backend Source**: `sentiment.py` runs per message and aggregates per cluster.</p>
              <p><strong>GPT Prompt:</strong></p>
              <pre className="bg-gray-100 p-2 rounded text-xs whitespace-pre-wrap">
{"You are a sentiment analysis expert. Classify the following message as one of the following: Positive, Neutral, or Negative. Message: {text}. Respond with one word only."}
              </pre>
              <p><strong>Interpretation:</strong> Track how users are feeling about topics.</p>
            </section>

            <section>
              <strong>GPT Evaluation Modal</strong>
              <p>Appears when reviewing a cluster. It includes GPT's evaluation of how well the FAQ addressed the top question.</p>
              <p><strong>Prompt (gpt.py):</strong></p>
              <pre className="bg-gray-100 p-2 rounded text-xs whitespace-pre-wrap">
{`System:
You are a support quality evaluator.
User:
Message: "{top_message}"
FAQ: "{faq.question}"
Answer: "{faq.answer}"
Does the answer fully resolve the user's concern? Respond with one of:
- Fully covered
- Partially covered
- Not covered
Then explain why.`}
              </pre>
              <p><strong>Output:</strong> stored in `gpt_evaluation`, `coverage`, and `resolution_score` fields.</p>
            </section>

            <section>
              <strong>FAQ Suggestions</strong>
              <p>Lists new questions and answers proposed by GPT where existing FAQs were weak or missing.</p>
              <p><strong>Prompt used:</strong></p>
              <pre className="bg-gray-100 p-2 rounded text-xs whitespace-pre-wrap">
{`System:
Create a better FAQ based on the conversation.
User:
Here is a cluster of related user messages:
"{cluster_messages}"
Current FAQ: "{matched_faq.question}" → "{matched_faq.answer}"
Create a clearer or new FAQ if needed.`}
              </pre>
              <p><strong>Interpretation:</strong> Use these to improve automation coverage.</p>
            </section>

            <section>
              <strong>Resolution Score Timeline</strong>
              <p>Line chart showing average GPT resolution score per day.</p>
              <p><strong>Backend Source:</strong> From cluster-level GPT evaluation results.</p>
              <p><strong>Interpretation:</strong> Drop in score = quality regression or new unresolved topics.</p>
            </section>

            <section>
              <strong>Trending Topics</strong>
              <p>Shows weekly change in keyword usage with sentiment trend.</p>
              <p><strong>Backend Source:</strong> `/api/faq/trending-leaderboard/` (keyword frequency + trend + sentiment).</p>
              <p><strong>Interpretation:</strong> Track new surges in user interest or problems (e.g., shipping delays, refund bugs).</p>
            </section>

            <section>
              <strong>Cluster Table</strong>
              <p>Full list of all clusters including:</p>
              <ul className="list-disc ml-5 mt-1">
                <li>Top message</li>
                <li>Matched FAQ</li>
                <li>Similarity score</li>
                <li>Sentiment</li>
                <li>Summary & Keywords</li>
              </ul>
              <p><strong>GPT Usage:</strong> Summaries and keywords generated via `gpt.py` with prompts :</p>
              <pre className="bg-gray-100 p-2 rounded text-xs whitespace-pre-wrap">
{"You are a clustering assistant. Given the following messages, label the topic in 2–4 descriptive words (e.g., 'Shipping Delay', 'Login Issue','Refund Request').Messages. Respond with just the label."}
              </pre>
              <p><strong>Interpretation:</strong> Use this for detailed audit and prioritization.</p>
            </section>

            <section>
              <strong>Top Process Gaps</strong>
              <p>Shows which topics frequently lack any matching FAQ.</p>
              <p><strong>Backend Logic:</strong> Topics extracted where GPT said "Not covered".</p>
              <p><strong>Interpretation:</strong> Improve internal SOPs or document missing flows (e.g., payment limits, policy changes).</p>
            </section>

            <section>
              <strong>Top FAQ Gaps by Topic</strong>
              <p>Bar chart showing the count of uncovered issues by topic label.</p>
              <p><strong>Interpretation:</strong> Use to prioritize thematic FAQ or training updates (e.g., "returns", "setup", "delivery").</p>
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
