import os
import requests
import json
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")

load_dotenv()
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")

def fetch_and_save_html(job_url, record_id):
    # Create the html_cache subfolder relative to the current script
    folder_path = Path(__file__).parent / "html_cache"
    folder_path.mkdir(parents=True, exist_ok=True)

    # Unique filename: recordID + timestamp.html
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = folder_path / f"{record_id}_{timestamp}.html"

    # Fetch with Playwright
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(job_url, timeout=60000)
        page.wait_for_selector('h1', timeout=60000)  # Upwork job titles are inside <h1> tags
        html = page.content()
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        browser.close()
        print(f"✅ HTML saved to {filename}")

    return filename

def scrape_from_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    visible_text = soup.get_text()

    # Full Description
    meta = soup.find("meta", attrs={"name": "description"})
    description = meta["content"].strip() if meta else None

    # Client Location
    location_block = soup.find('li', attrs={"data-qa": "client-location"})
    location = location_block.find('strong').text.strip() if location_block and location_block.find('strong') else None

    # Spend
    spent = None
    spent_block = soup.find('strong', attrs={"data-qa": "client-spend"})
    if spent_block:
        raw = spent_block.get_text()
        match = re.search(r"\$([\d.,]+)([KkMm]?)", raw)
        if match:
            spent = f"${match.group(1).strip()}{match.group(2).strip()}"

    # Project Length
    project_length = next((s for s in [
        "Less than 1 month", "1 to 3 months",
        "3 to 6 months", "More than 6 months"
    ] if s in visible_text), None)

    # Hours per week
    hours_week = next((s for s in [
        "Less than 30 hrs/week", "More than 30 hrs/week"
    ] if s in visible_text), None)

    return {
        "Full Description": description,
        "Client Location": location,
        "Lead Amount Spent": spent,
        "Project Length": project_length,
        "Hours/Week": hours_week,
        "Scraped?": True
    }

# Airtable API update
def update_airtable_record(record_id, fields: dict):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}/{record_id}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"fields": fields}
    response = requests.patch(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        print("✅ Airtable updated")
    else:
        print("❌ Airtable update failed:", response.text)

def scrape_and_update(job_url, record_id):  
    print(f"🔍 Scraping: {job_url}")
    html_file = fetch_and_save_html(job_url, record_id)
    fields = scrape_from_file(html_file)
    print("🔎 Extracted:", fields)
    update_airtable_record(record_id, fields)