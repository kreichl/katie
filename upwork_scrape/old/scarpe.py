from bs4 import BeautifulSoup
import re
import json

def parse_upwork_html_with_regex(file_path, output_json_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    # Full raw HTML text (NOT just visible text) because we need the script content
    raw_html = str(soup)

    # Visible text for some fields
    visible_text = soup.get_text(separator="\n")

    # Job Title
    page_title = soup.find('title')
    job_title = page_title.text.strip() if page_title else None

    # Job Description
    meta_description = soup.find('meta', attrs={'name': 'description'})
    description = meta_description['content'].strip() if meta_description else None

    # Client Location
    location = None
    location_block = soup.find('li', attrs={"data-qa": "client-location"})
    if location_block and location_block.find('strong'):
        location = location_block.find('strong').text.strip()

    # Client Total Spent
    spent = None
    spent_block = soup.find('strong', attrs={"data-qa": "client-spend"})
    if spent_block:
        spent_text = spent_block.get_text()
        spent_match = re.search(r"\$([\d.,]+)", spent_text)
        if spent_match:
            spent = f"${spent_match.group(1)}"

    # Client Rating
    rating = None
    rating_match = re.search(r"([0-9]\.[0-9]+)\s*star rating", visible_text)
    if rating_match:
        rating = rating_match.group(1)

    # Project Length
    project_length = None
    for option in ["Less than 1 month", "1 to 3 months", "3 to 6 months", "More than 6 months"]:
        if option in visible_text:
            project_length = option
            break

    # Hours per Week
    hours_per_week = None
    for option in ["Less than 30 hrs/week", "More than 30 hrs/week"]:
        if option in visible_text:
            hours_per_week = option
            break

    # Payment Verified (NEW: from raw HTML)
    payment_verified = "No"  # default
    payment_match = re.search(r"isPaymentMethodVerified:([a-z])", raw_html)
    if payment_match:
        if payment_match.group(1) == "d":
            payment_verified = "Yes"
        else:
            payment_verified = "No"

    # Output
    data = {
        "job_title": job_title,
        "description": description,
        "client_location": location,
        "client_total_spent": spent,
        "client_rating": rating,
        "project_length": project_length,
        "hours_per_week": hours_per_week,
        "payment_verified": payment_verified
    }

    # Save JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"✅ Saved parsed data to {output_json_path}")

# Example usage
parse_upwork_html_with_regex('upwork_job.html', 'upwork_job_clean.json')