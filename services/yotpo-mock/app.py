import random
import string
from datetime import datetime, timedelta

from flask import Flask, jsonify, request

app = Flask(__name__)

STATUSES = ["sent", "delivered", "bounced", "opened", "clicked"]

def random_email():
    user = ''.join(random.choices(string.ascii_lowercase, k=8))
    domain = random.choice(["gmail.com", "yahoo.com", "example.com"])
    return f"{user}@{domain}"

def random_status():
    return random.choice(STATUSES)

def random_created_at():
    now = datetime.utcnow()
    delta = timedelta(days=random.randint(0, 365))
    return (now - delta).strftime("%Y-%m-%dT%H:%M:%SZ")

@app.route("/v1/emails", methods=["GET"])
def get_emails():
    # Require X-Yotpo-Token header
    token = request.headers.get("X-Yotpo-Token")
    # For testing, accept any non-empty token, or set a specific value if desired
    if not token or token != "test-token":
        return jsonify({"error": "Unauthorized: missing or invalid X-Yotpo-Token header"}), 401
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    emails = []
    for i in range(per_page):
        emails.append({
            "id": (page - 1) * per_page + i + 1,
            "email": random_email(),
            "status": random_status(),
            "created_at": random_created_at()
        })
    next_page = page + 1 if page < 5 else None
    return jsonify({"emails": emails, "next_page": next_page})

@app.route("/v1/random", methods=["GET"])
def get_random():
    return jsonify({"value": random.randint(1, 1000000)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
