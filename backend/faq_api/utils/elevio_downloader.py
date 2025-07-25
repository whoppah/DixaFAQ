# backend/faq_api/utils/elevio_downloader.py
import requests
import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from html2text import html2text
import re
from datetime import datetime
from ..models import FAQ # Import your FAQ model for the fallback


class ElevioFAQDownloader:
    def __init__(self, api_key, jwt, base_url="https://api.elev.io/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.jwt = jwt
        self.headers = {
            "Authorization": f"Bearer {jwt}",
            "x-api-key": api_key,
            "Content-Type": "application/json",
        }
        self.output_dir = "faq_pdfs"

    def setup_output_directory(self):
        """Create output directory if it doesn't exist and verify write perms."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"Created directory: {self.output_dir}")
        else:
            print(f"Directory already exists: {self.output_dir}")

        test_file = os.path.join(self.output_dir, "test.txt")
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            print(f"✅ Directory is writable: {os.path.abspath(self.output_dir)}")
        except Exception as e:
            print(f"❌ Cannot write to directory: {e}")
            raise

    def get_all_articles(self):
        """Fetch all published articles from Elevio API, paginated."""
        articles = []
        page = 1
        page_size = 100

        while True:
            print(f"Fetching page {page}...")
            url = f"{self.base_url}/articles"
            params = {
                "page": page,
                "page_size": page_size,
                "status": "published",
            }
            try:
                resp = requests.get(url, headers=self.headers, params=params)
                resp.raise_for_status()
                data = resp.json()
                page_articles = data.get("articles", [])
                if not page_articles:
                    break
                articles.extend(page_articles)
                if len(page_articles) < page_size:
                    break
                page += 1
            except requests.exceptions.RequestException as e:
                print(f"Error fetching articles on page {page}: {e}")
                break

        print(f"Total articles fetched: {len(articles)}")
        return articles

    def get_article_details(self, article_id):
        """Fetch detailed article content including translations."""
        url = f"{self.base_url}/articles/{article_id}"
        try:
            resp = requests.get(url, headers=self.headers)
            resp.raise_for_status()
            data = resp.json()
            return data.get("article", {})
        except requests.exceptions.RequestException as e:
            print(f"Error fetching article {article_id}: {e}")
            return None

    def clean_text(self, html_content):
        """Convert HTML to clean markdown-like text."""
        if not html_content:
            return ""
        try:
            if not isinstance(html_content, str):
                html_content = str(html_content)
            text = html2text(html_content)
            text = re.sub(r"\n\s*\n", "\n\n", text)
            text = re.sub(r"[ \t]+", " ", text)
            return text.strip()
        except Exception as e:
            print(f"Error cleaning text: {e}")
            return str(html_content) if html_content else ""

    def create_pdf(self, article):
        """Create a PDF file for one article and return its path."""
        try:
            article_id = article.get("id", "unknown")
            print(f"  -> Creating PDF for article ID: {article_id}")

            # pick the English translation
            english = next(
                (t for t in article.get("translations", []) if t.get("language_id") == "en"),
                None
            )
            if not english:
                print(f"  -> No English translation found for article {article_id}")
                return None

            title = english.get("title") or "Untitled"
            body = english.get("body") or ""
            summary = english.get("summary") or ""
            keywords_list = english.get("keywords") or []
            tags_list = article.get("tags") or []

            # sanitize title for filename
            safe_title = re.sub(r"[^\w\s-]", "", title)
            safe_title = re.sub(r"[-\s]+", "-", safe_title).strip("-") or f"article_{article_id}"
            filename = f"{article_id}_{safe_title[:50]}.pdf"
            filepath = os.path.join(self.output_dir, filename)

            doc = SimpleDocTemplate(filepath, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Title
            story.append(Paragraph(title, ParagraphStyle(
                "Title", parent=styles["Heading1"], fontSize=16, spaceAfter=20
            )))
            story.append(Spacer(1, 12))

            # Summary
            if summary.strip():
                story.append(Paragraph("Summary", styles["Heading2"]))
                story.append(Paragraph(self.clean_text(summary), styles["Normal"]))
                story.append(Spacer(1, 12))

            # Keywords & Tags
            if keywords_list:
                story.append(Paragraph("Keywords", styles["Heading2"]))
                story.append(Paragraph(", ".join(keywords_list), styles["Normal"]))
                story.append(Spacer(1, 12))
            if tags_list:
                story.append(Paragraph("Tags", styles["Heading2"]))
                story.append(Paragraph(", ".join(tags_list), styles["Normal"]))
                story.append(Spacer(1, 12))

            # Content
            story.append(Paragraph("Content", styles["Heading2"]))
            if body.strip():
                for para in self.clean_text(body).split("\n\n"):
                    if para.strip():
                        story.append(Paragraph(para, styles["Normal"]))
                        story.append(Spacer(1, 6))
            else:
                story.append(Paragraph("No content available", styles["Normal"]))

            # Footer
            story.append(Spacer(1, 20))
            footer = (
                f"Article ID: {article_id} | "
                f"Created: {article.get('created_at', 'N/A')} | "
                f"Updated: {article.get('updated_at', 'N/A')}"
            )
            story.append(Paragraph(footer, styles["Normal"]))

            doc.build(story)
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"  ✅ PDF created: {filename} ({size} bytes)")
                return filepath
            else:
                print(f"  ❌ PDF not found after build: {filepath}")
                return None

        except Exception as e:
            print(f"  ❌ Error creating PDF for article {article.get('id')}: {e}")
            return None

    def download_all_faqs(self):
        """
        Fetch all FAQs from Elevio, generate PDFs, and return a list of
        {"question": ..., "answer": ...}. If Elevio has none, fall back
        to the latest FAQ in your DB.
        """
        print("🚀 Starting FAQ download process...")
        print(f"📂 CWD: {os.getcwd()}")
        self.setup_output_directory()

        articles = self.get_all_articles()

        # --- FALLBACK: use latest DB FAQ if no Elevio articles ---
        if not articles:
            print("❌ No Elevio articles found. Falling back to DB.")
            latest = FAQ.objects.order_by('-id').first()
            if latest:
                print(f"🔄 Using DB FAQ #{latest.id}: {latest.question[:60]}")
                return [{"question": latest.question, "answer": latest.answer}]
            else:
                print("❌ No FAQs found in database either.")
                return []

        print(f"🧾 Retrieved {len(articles)} Elevio articles.")
        for sample in articles[:3]:
            print(f"  • {sample.get('title', '—')}")

        created_pdfs, failed, extracted = [], [], []

        for idx, art in enumerate(articles, 1):
            print(f"\n🔄 Processing {idx}/{len(articles)}: ID={art.get('id')}")
            detail = self.get_article_details(art.get("id"))
            if not detail:
                failed.append(art.get("id"))
                continue

            pdf = self.create_pdf(detail)
            if pdf:
                created_pdfs.append(pdf)
            else:
                failed.append(art.get("id"))

            trans = next(
                (t for t in detail.get("translations", []) if t.get("language_id") == "en"),
                None
            )
            if not trans:
                continue

            q = (trans.get("title") or "").strip()
            a = self.clean_text(trans.get("body", ""))
            if q and a:
                extracted.append({"question": q, "answer": a})

        # summary
        print("\n===== SUMMARY =====")
        print(f"Processed: {len(articles)}")
        print(f"PDFs: {len(created_pdfs)} | Failed: {len(failed)}")
        print(f"Extracted FAQs: {len(extracted)}")
        print(f"Output dir: {os.path.abspath(self.output_dir)}")

        # save JSON for embedding
        json_path = os.path.join(self.output_dir, "elevio_faq_text.json")
        try:
            with open(json_path, "w", encoding="utf-8") as jf:
                json.dump(extracted, jf, indent=2, ensure_ascii=False)
            print(f"✅ Saved JSON: {json_path}")
        except Exception as e:
            print(f"❌ Could not write JSON: {e}")

        return extracted
