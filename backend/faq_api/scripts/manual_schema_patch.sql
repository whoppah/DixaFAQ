-- Step 1: Ensure message_id is primary key
ALTER TABLE faq_api_message
DROP CONSTRAINT IF EXISTS faq_api_message_pkey,
ADD PRIMARY KEY (message_id);

-- Step 2: Create the through table if it doesn't exist
CREATE TABLE IF NOT EXISTS faq_api_clusterresultmessage (
    id SERIAL PRIMARY KEY,
    cluster_result_id INTEGER NOT NULL REFERENCES faq_api_clusterresult(id) ON DELETE CASCADE,
    message_id VARCHAR(255) NOT NULL REFERENCES faq_api_message(message_id) ON DELETE CASCADE
);
