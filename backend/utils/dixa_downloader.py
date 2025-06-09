#backend/utils/dixa_downloader.py
import requests
import os
import json
import time
import datetime


class DixaDownloader:
    def __init__(self, api_token, start_date, end_date, step=datetime.timedelta(days=31),conversations_url="https://exports.dixa.io/v1/conversation_export", messages_url= "https://exports.dixa.io/v1/message_export"):
        self.conversations_url = conversations_url
        self.messages_url = messages_url
        self.api_token = api_token
        self.start = start_date
        self.end = end_date
        self.step = step
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }
        self.output_dir = "dixa_data"

    def setup_output_directory(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"Created directory: {self.output_dir}")
        else:
            print(f"Directory already exists: {self.output_dir}")

        # Test write permissions
        test_file = os.path.join(self.output_dir, "test.txt")
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            print(f"✅ Directory is writable: {os.path.abspath(self.output_dir)}")
        except Exception as e:
            print(f"❌ Cannot write to directory: {e}")
            raise

    def daterange(self):
        while self.start < self.end:
            yield (self.start, min(self.start + self.step, self.end))
            self.start += self.step

    def fetch_data(self, url, start, end):
        params = {
            "created_after": start.isoformat(),
            "created_before": end.isoformat()
        }
        print(f"Fetching data from {start} to {end}")
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            try:
                result = response.json()
                if isinstance(result, dict):
                    return result.get("data", [])
                elif isinstance(result, list):
                    return result
                else:
                    print("Unexpected response format")
                    return []
            except json.JSONDecodeError:
                print("Failed to decode JSON")
                return []
        else:
            print(f"Failed: {response.status_code} - {response.text}")
            return []


    def save_json(self, filename, data):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Saved {filename}")

    # Main loop
    def download_all_dixa_data(self):
        "Main function to download all the dixa data"
        print("Starting Dixa Download download process...")
        print(f"Current working directory: {os.getcwd()}")
        self.setup_output_directory()

        all_messages = []
        all_conversations = []

        for start, end in self.daterange():
            print(f"Processing range {start} to {end}...")

            # Fetch and save all conversations
            conv_data = self.fetch_data(self.conversations_url, start, end)
            all_conversations.extend(conv_data)
            self.save_json(os.path.join(self.output_dir, f"conversations_{start}_{end}.json"), conv_data)
            time.sleep(6)

            # Fetch and save all messages
            msg_data = self.fetch_data(self.messages_url, start, end)
            all_messages.extend(msg_data)
            self.save_json(os.path.join(self.output_dir, f"messages_{start}_{end}.json"), msg_data)
            time.sleep(20)
        
        return all_messages,all_conversations
