import os
import arxiv
from openai import OpenAI
import requests
import smtplib
from email.message import EmailMessage
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

KEYWORDS = [
    "metamaterials",
    "nanomaterials",
    "mechanics",
    ] 

MAX_RESULTS = 3  # papers per key word

TOREAD_FOLDER = os.path.expanduser("~/Downloads/ToRead")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_SMTP_SERVER = "smtp.gmail.com" # don't change
EMAIL_SMTP_PORT = 587 # don't change
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

# setup OpenAI
client = OpenAI()
client.api_key = OPENAI_API_KEY

# ensure folder exists
today_folder = os.path.join(TOREAD_FOLDER, datetime.now().strftime("%Y-%m-%d"))
os.makedirs(today_folder, exist_ok=True)

summaries = []

# fetch and process papers
for keyword in KEYWORDS:
    search = arxiv.Search(
        query=keyword,
        max_results=MAX_RESULTS,
        sort_by=arxiv.SortCriterion.SubmittedDate # most recent
    )

    for result in search.results():
        print(f"Found: {result.title}")
        print("----------------")

        # download PDF
        pdf_url = result.pdf_url
        response = requests.get(pdf_url)

        print(f"Successfully retrieved: {result.pdf_url}")
        print("----------------")

        safe_title = "".join(c for c in result.title if c.isalnum() or c in (' ', '_')).rstrip()
        pdf_filename = os.path.join(today_folder, f"{safe_title}.pdf")

        with open(pdf_filename, 'wb') as f:
            f.write(response.content)
        
        print(f"Successfully wrote to {pdf_filename}")
        print("----------------")

        # summarize abstract
        prompt = f"Summarize the following paper abstract in 1-2 sentences:\n\n{result.summary}"
        response = client.responses.create(
            model="gpt-4o",
            input=[
                {
                    "role": "system",
                    "content": "You are a research assistant"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        summary_text = response.output_text.strip()
        summaries.append((result.title, summary_text, pdf_url))

        print(f"Successfully summarized {pdf_filename}")

# now send the email
print("Sending email...")
msg = EmailMessage()
msg['Subject'] = f"Your Daily Paper Digest ({datetime.now().strftime('%Y-%m-%d')})"
msg['From'] = EMAIL_ADDRESS
msg['To'] = RECIPIENT_EMAIL

email_body = "Today's Papers:\n\n"
for title, summary, pdf_url in summaries:
    email_body += f"📄 {title}\n{summary}\n{pdf_url}\n"

msg.set_content(email_body)

with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.send_message(msg)

print("Daily digest sent!")
