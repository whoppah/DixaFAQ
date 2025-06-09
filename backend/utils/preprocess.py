#backend/utils/preprocess.py
import os
import json
import re
import spacy
from langdetect import detect
from html2text import html2text
from html import unescape

class MessagePreprocessor:
    def __init__(self):
        # Load English and Dutch spaCy models
        self.nlp_models = {
            "en": spacy.load("en_core_web_sm"),
            "nl": spacy.load("nl_core_news_sm")
        }

    def detect_language(self, text):
        try:
            return detect(text)
        except Exception:
            return "en"  # Fallback

    def clean_html(self, text):
        """Convert HTML to clean, plain text with extra post-processing."""
        if not isinstance(text, str) or not text.strip():
            return ""

        try:
            text = html2text(text)
        except Exception:
            pass

        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'(\*\*|__|\*|`)', '', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = unescape(text)
        text = text.encode("ascii", "ignore").decode()
        repetitive_phrases = [
            r"\bkind regards\b",
            r"\bbest regards\b",
            r"\bmet vriendelijke groet(en)?\b",
            r"\bthanks\b",
            r"\bthank you\b",
            r"\bcheers\b", # increase the list later!
            r"\bbevestiging\b",  # confirmation
            r"\bbedankt voor je bericht\b",  # thank you for your message
            r"\bwe zullen zo snel mogelijk antwoorden\b",  # we will respond as soon as possible
            r"\buw e-mail hebben ontvangen\b",  # we have received your email
            r"\bonze excuses\b",  # our apologies
            r"\bwe doen ons best\b",  # we do our best
            r"\bwacht u op de komst\b",  # are you waiting for the arrival
            r"\bautomatisch\b",  # automatic
            r"\bgeduld\b",  # patience
            r"\bDear Customer, This is a confirmation that we recovered your email. We will reply as soon as possible.\b",
            r"\bDear customer, we are a bit busier at the moment and have not yet goths to your email.\b",
            r"\bDear Customer, This is an automatic confirmation that we have recovered your email. To help you as quickly as Possible, we have already prepared Answers to frequently asked questions. Good news: as much as 95% of Questions are resolved direct -with this! Do you have a Question about the payout of your sold item? Then click here.\b",
            r"\bThis is a confirmation that\b",
            r"\bThank you for filling out the form via WhatsApp. This is a confirmation we received the form.\b",
            r"\bCeci Est une Confirmation Que Nous Avons Reçu le Formular\b",
            r"\bMerci d'avoir rempli le formulaire via WhatsApp\b",
            r"\bCher Client, Ceci Est Une Confirmation Que Nous Avons Bien Reçu Votre e-mail\b",
            r"\bWe will respond to your message as soon as possible\b",
            r"\bDear, what a pity to hear that you have decided to remove your account from our platform\b",
            r"\bDear customer, This is an automatically generated response\b",
            r"\bDear customer, This is an automatic confirmation that we have received your email.\b",
            r"\bGood afternoon! Thank you for your message.\b",
            r"\b(No message text)\b",
            r"\bAll Rights Reserved\b",
            r"\bSent from my iPhone\b",
            r"\bGraag gedaan!\b",
            r"\bVerstuurd vanaf mijn iPhone\b",
            r"\bwe are a bit busier at the moment and have not yet\b",
            r"\b(No text, check original email if available)\b",
            r"\bDankjewel voor je bericht aan Vintage.nl We reageren zo snel als mogelijk op je bericht.\b",
            r"\bno, I need more help\b",
            r"\bWe will respond to your message as soon as possible\b",
            r"\bGoedemiddag! Dank voor je bericht. Ik heb het voor je aangepast!\b"
            r"\bBeste, Wat jammer om te horen dat u besloten heeft uw account van ons platform te verwijderen\b",
            r"\bGood afternoon! Thank you for your message. What a pity! I made it right and deleted your account.\b",
            r"\bGood afternoon! Thank you for your message. What a pity! I made it right and your account has been deleted.\b",
            r"\bHello 👋 I'm Whoppah AI, I will try to answer your questions, how can I help you today?\b",
            r"\bGet more help\b",
            r"\bGraag gedaan!\b",
            r"\bWat jammer! Ik heb het in orde gemaakt en je account\b",
            r"\bGoedemiddag! Dank voor je bericht. Ik heb de advertentie gereactiveerd!\b", #reactivate advs
            r"\bGeneral questions about Whoppah\b",
            r"\bGoedemiddag! Dank voor je bericht. Ik heb het voor je aangepast!\b",
            r"\bBeste, Wat jammer om te horen dat u besloten heeft uw account van ons platform te verwijderen.\b",
            r"\bBeste,Wat jammer om te horen dat u besloten heeft uw account van ons platform te verwijderen\b",
            r"\bBeste, Bedankt voor uw bericht! We hebben met succes een advertentie verlengd. Fijne dag!\b",
            r"\bGoedemiddag! Dank voor je bericht. Wat jammer dat je niets hebt vernomen! Heb je de verkoper al een Whoppah chat bericht gestuurd?\b",
            r"\bGoedemiddag! Dank voor je bericht. Ik zie dat het item is afgeleverd maar de koper heeft aangegeven het niet in goede orde te hebben ontvangen.\b", #buyer received order not in good order
            r"\bGoedemorgen!Dank voor je bericht. Helaas is dit geen betrouwbaar bericht, maar een scam\b", #scam,
            r"\bBeste, Dank je wel voor je bericht! Het lijkt erop dat je de verkoper via de chat wilde beantwoorden, maar per ongeluk naar de klantenservice hebt gestuurd\b", #customer service instead of client
            r"\bBeste,Hartelijk dank voor je bericht! Helaas bevat je e-mail geen tekst. We horen graag hoe we je verder kunnen helpen. Ik kijk uit naar je reactie!\b", #notext
            r"\bBeste, dank je wel voor je bericht! Zou je de koper alsjeblieft via de Whoppah-chat kunnen informeren over de situatie, zodat hij ook weet wat er aan de hand is? Ik heb de bestelling inmiddels geannuleerd en de terugbetaling naar de koper in gang gezet.Ik wens je nog een fijne dag!\b",
            r"\bThank you for filling out the form via WhatsApp. This is a confirmation we recedived the form. We will reply as soon as possible.\b",
            r"\bI'm sorry, it seems I Couldn't Find the Right Answer for your Question. Could you Try Asking It Differently? Alternatively, I can direct you to additional help.\b"
        ]
        for phrase in repetitive_phrases:
            text = re.sub(phrase, "", text, flags=re.IGNORECASE)

        return text.strip()

    def anonymize_text(self, text):
        """Clean and anonymize a text field using regex and spaCy NER."""
        if not isinstance(text, str) or not text.strip():
            return text

        text = self.clean_html(text)

        # Regex-based anonymization
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        text = re.sub(r'https?://\S+', '[URL]', text)
        text = re.sub(r'\[.*?\]\(mailto:.*?\)', '[EMAIL_LINK]', text)
        text = re.sub(r'\b\d{7,15}\b', '[PHONE]', text)
        text = re.sub(r'Verstuurd vanaf mijn \w+', '[DEVICE_SIGNATURE]', text, flags=re.IGNORECASE)

        # spaCy NER-based anonymization
        lang = self.detect_language(text)
        lang = lang if lang in self.nlp_models else "en"
        doc = self.nlp_models[lang](text)

        anonymized = text
        for ent in reversed(doc.ents):
            if ent.label_ in ("PERSON", "ORG", "GPE", "LOC"):
                anonymized = anonymized[:ent.start_char] + f'[{ent.label_}]' + anonymized[ent.end_char:]

        return anonymized

    def anonymize_message(self, msg):
        msg = msg.copy()

        msg["text"] = self.anonymize_text(msg.get("text", ""))

        # Conditionally anonymize author_name
        author_name = msg.get("author_name", "")
        if author_name and author_name.lower() not in ["system user", "whoppahai"]:
            msg["author_name"] = "[AUTHOR_NAME]"

        # Always anonymize these fields if present
        for field in ["author_email", "from"]:
            if msg.get(field):
                msg[field] = f"[{field.upper()}]"

        # Anonymize lists of recipients
        for field in ["to", "cc", "bcc"]:
            msg[field] = ["[EMAIL]" for _ in msg.get(field, [])]

        return msg

    def process_file(self, input_path, output_path):
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        with open(input_path, "r", encoding="utf-8") as f:
            messages = json.load(f)

        print(f"Processing {len(messages)} messages...")

        anonymized = [self.anonymize_message(msg) for msg in messages]

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(anonymized, f, indent=2, ensure_ascii=False)

        print(f"✅ Anonymized output saved to: {output_path}")

        return anonymized

