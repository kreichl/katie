from flask import Flask, request, jsonify
import threading
from scrape_and_update_airtable import scrape_and_update

app = Flask(__name__)

@app.route("/scrape", methods=["POST"])
def scrape():
    data = request.json
    job_url = data.get("url")
    record_id = data.get("record_id")

    if not job_url or not record_id:
        return jsonify({"error": "Missing url or record_id"}), 400

    # Run scraping in a new thread so webhook returns immediately
    threading.Thread(target=scrape_and_update, args=(job_url, record_id)).start()

    return jsonify({"status": "Scraping started"}), 200

if __name__ == "__main__":
    app.run(port=5000)
