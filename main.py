import feedparser
import pickle
import os
import smtplib
from email.mime.text import MIMEText

RSS_URL = "https://www.reddit.com/r/survivalgaming/new/.rss"
KEYWORDS = ["season", "realistic", "primitive"]
PICKLE_FILE = "seen.pkl"

EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
TO_EMAIL = os.environ.get("TO_EMAIL")

def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, [TO_EMAIL], msg.as_string())

# Load seen posts
if os.path.exists(PICKLE_FILE):
    with open(PICKLE_FILE, "rb") as f:
        seen_posts = pickle.load(f)
else:
    seen_posts = set()

# Fetch feed
feed = feedparser.parse(RSS_URL)

for entry in feed.entries:

    # Use link as permanent ID
    post_id = entry.link  

    title = entry.title.lower()
    summary = getattr(entry, "summary", "").lower()

    if post_id not in seen_posts and (
        any(k in title for k in KEYWORDS) or
        any(k in summary for k in KEYWORDS)
    ):
        snippet = entry.summary[:200] if hasattr(entry, "summary") else ""
        email_body = f"{entry.title}\n\n{snippet}\n\nLink: {entry.link}"

        send_email(f"[Reddit Alert] {entry.title}", email_body)
        seen_posts.add(post_id)

# Save updated seen posts
with open(PICKLE_FILE, "wb") as f:
    pickle.dump(seen_posts, f)

print("Done")
