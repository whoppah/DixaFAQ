#backend/faq_api/utils/elevio_downloader.py
import requests
import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from html2text import html2text
import re
from datetime import datetime


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

    def get_all_articles(self):
        """Fetch all published articles from Elevio API"""
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
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
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
        """Fetch detailed article content including translations"""
        url = f"{self.base_url}/articles/{article_id}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("article", {})
        except requests.exceptions.RequestException as e:
            print(f"Error fetching article {article_id}: {e}")
            return None

    def clean_text(self, html_content):
        """Convert HTML to clean text"""
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
        """Create a PDF for a single article"""
        try:
            article_id = article.get("id", "unknown")
            print(f"  -> Creating PDF for article ID: {article_id}")

            english_translation = None
            for translation in article.get("translations", []):
                if translation.get("language_id") == "en":
                    english_translation = translation
                    break
            if not english_translation:
                print(f"  -> No English translation found for article {article_id}")
                return None

            title = english_translation.get("title") or "Untitled"
            body = english_translation.get("body") or ""
            summary = english_translation.get("summary") or ""

            keywords_list = english_translation.get("keywords") or []
            keywords = ", ".join(str(k) for k in keywords_list if k) if isinstance(keywords_list, list) else ""

            tags_list = article.get("tags") or []
            tags = ", ".join(str(t) for t in tags_list if t) if isinstance(tags_list, list) else ""

            if not isinstance(title, str):
                title = str(title) if title is not None else "Untitled"

            safe_title = re.sub(r"[^\w\s-]", "", title)
            safe_title = re.sub(r"[-\s]+", "-", safe_title)
            if not safe_title or safe_title.isspace():
                safe_title = f"article_{article_id}"

            filename = f"{article_id}_{safe_title[:50]}.pdf"
            filepath = os.path.join(self.output_dir, filename)

            print(f"  -> Creating file: {filename}")
            print(f"  -> Full path: {os.path.abspath(filepath)}")

            doc = SimpleDocTemplate(filepath, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            title_style = ParagraphStyle(
                "CustomTitle", parent=styles["Heading1"], fontSize=16, spaceAfter=20
            )
            heading_style = ParagraphStyle(
                "CustomHeading", parent=styles["Heading2"], fontSize=12, spaceAfter=10, spaceBefore=15
            )

            safe_title_display = title if title.strip() else "Untitled Article"
            story.append(Paragraph(safe_title_display, title_style))
            story.append(Spacer(1, 12))

            if summary.strip():
                story.append(Paragraph("Summary", heading_style))
                clean_summary = self.clean_text(summary)
                if clean_summary:
                    story.append(Paragraph(clean_summary, styles["Normal"]))
                    story.append(Spacer(1, 12))

            if keywords.strip():
                story.append(Paragraph("Keywords", heading_style))
                story.append(Paragraph(keywords, styles["Normal"]))
                story.append(Spacer(1, 12))

            if tags.strip():
                story.append(Paragraph("Tags", heading_style))
                story.append(Paragraph(tags, styles["Normal"]))
                story.append(Spacer(1, 12))

            story.append(Paragraph("Content", heading_style))

            if body.strip():
                clean_body = self.clean_text(body)
                if clean_body:
                    paragraphs = clean_body.split("\n\n")
                    for para in paragraphs:
                        if para.strip():
                            try:
                                story.append(Paragraph(para.strip(), styles["Normal"]))
                                story.append(Spacer(1, 6))
                            except Exception as para_error:
                                print(f"  -> Error adding paragraph: {para_error}")
                                story.append(Paragraph("Content formatting error", styles["Normal"]))
                else:
                    story.append(Paragraph("No content available", styles["Normal"]))
            else:
                story.append(Paragraph("No content available", styles["Normal"]))

            story.append(Spacer(1, 20))
            footer_text = f"Article ID: {article_id} | Created: {article.get('created_at', 'N/A')} | Updated: {article.get('updated_at', 'N/A')}"
            story.append(Paragraph(footer_text, styles["Normal"]))

            try:
                doc.build(story)
                if os.path.exists(filepath):
                    file_size = os.path.getsize(filepath)
                    print(f"  ✅ PDF created successfully: {filename} ({file_size} bytes)")
                    return filepath
                else:
                    print(f"  ❌ PDF file not found after creation: {filepath}")
                    return None
            except Exception as pdf_error:
                print(f"  ❌ PDF build error: {pdf_error}")
                return None

        except Exception as e:
            print(f"  ❌ Error creating PDF for article {article.get('id', 'unknown')}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def download_all_faqs(self):
        """Main method to download all FAQs and create PDFs"""
        print("Starting FAQ download process...")
        print(f"Current working directory: {os.getcwd()}")
        self.setup_output_directory()
        articles = self.get_all_articles()
        if not articles:
            print("No articles found!")
            return []

        created_pdfs = []
        failed_articles = []

        for i, article in enumerate(articles, 1):
            try:
                article_id = article.get("id", "unknown")
                article_title = article.get("title", "Unknown")
                if not isinstance(article_title, str):
                    article_title = str(article_title) if article_title is not None else "Unknown"
                print(f"Processing article {i}/{len(articles)}: {article_title}")
                detailed_article = self.get_article_details(article_id)
                if detailed_article:
                    pdf_path = self.create_pdf(detailed_article)
                    if pdf_path:
                        created_pdfs.append(pdf_path)
                    else:
                        failed_articles.append(article_id)
                else:
                    failed_articles.append(article_id)
                    print(f"  -> Failed to get details for article {article_id}")
            except Exception as e:
                article_id = article.get("id", "unknown")
                failed_articles.append(article_id)
                print(f"  -> Error processing article {article_id}: {e}")
                continue

        print(f"\n{'=' * 50}")
        print(f"SUMMARY:")
        print(f"Total articles processed: {len(articles)}")
        print(f"PDFs created successfully: {len(created_pdfs)}")
        print(f"Failed articles: {len(failed_articles)}")
        print(f"Output directory: {os.path.abspath(self.output_dir)}")

        if os.path.exists(self.output_dir):
            actual_files = [f for f in os.listdir(self.output_dir) if f.endswith(".pdf")]
            print(f"Actual PDF files in directory: {len(actual_files)}")
            if actual_files:
                print("Sample files:")
                for f in actual_files[:5]:
                    file_path = os.path.join(self.output_dir, f)
                    file_size = os.path.getsize(file_path)
                    print(f"  - {f} ({file_size} bytes)")

        if failed_articles:
            print(f"Failed article IDs: {failed_articles[:10]}...")

        summary_file = os.path.join(self.output_dir, "download_summary.txt")
        with open(summary_file, "w") as f:
            f.write(f"FAQ Download Summary\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total articles processed: {len(articles)}\n")
            f.write(f"PDFs created: {len(created_pdfs)}\n")
            f.write(f"Failed articles: {len(failed_articles)}\n\n")
            if failed_articles:
                f.write(f"Failed article IDs: {', '.join(map(str, failed_articles))}\n\n")
            f.write("Successfully created files:\n")
            for pdf in created_pdfs:
                f.write(f"- {os.path.basename(pdf)}\n")

        return created_pdfs
