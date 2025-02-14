import json
import csv
import os
from datetime import datetime

# Define Path of Raw Data
path = r"C:\Users\reich\Documents\GIT\katie\Lead_Gen\Raw_Data\Waukesha.json"
input_file = path

# Define the fields to extract
column_headers = [
    "Listing Status", "Agent Name", "Agent Email", "Provider Link",
    "Address Line 1", "City", "State", "Zip", "List Price",
    "Video Tour Link", "Matterport Link", "Listing Link", "Description", 
]

# Create Path for Exported Data
date = datetime.now().strftime("%Y_%m_%d")
output_path = r"C:\Users\reich\Documents\GIT\katie\Lead_Gen"
output_file = os.path.join(output_path, f"Leads_{date}.csv")

# Read the JSON file
with open(input_file, "r", encoding="utf-8") as json_file:
    data = json.load(json_file)

# Ensure the data is a list of dictionaries
if not isinstance(data, list):
    raise ValueError("JSON data should be a list of dictionaries")

# Write to CSV file
with open(output_file, "w", newline="", encoding="utf-8") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=column_headers)
    writer.writeheader()
    
    for entry in data:
        # Extract agent details (handle list)
        agents_list = entry.get("source", {}).get("agents", [])
        agent_name = ", ".join(agent.get("agentName", "") for agent in agents_list if agent.get("agentName"))
        agent_email = ", ".join(str(agent.get("agentEmail", "")) for agent in agents_list if agent.get("agentEmail") is not None)

        # Ensure providerUrl exists and is a dictionary before accessing "href"
        provider_url = entry.get("providerUrl")
        provider_link = provider_url.get("href", "") if isinstance(provider_url, dict) else ""

        # Extract video tour links (if available)
        virtual_tours = entry.get("homeTours", {}).get("virtualTours", [])
        video_tour_link = ", ".join(tour.get("href", "") for tour in virtual_tours if tour.get("href"))

        # Extract Matterport links (if available)
        matterport_data = entry.get("matterport", {})  # Ensure it's a dictionary
        matterport_videos = matterport_data.get("videos", []) if isinstance(matterport_data, dict) else []
        matterport_link = ", ".join(video.get("href", "") for video in matterport_videos if video.get("href"))

        writer.writerow({
            "List Price": entry.get("listPrice", ""),
            "Description": entry.get("description", {}).get("text", ""),
            "Address Line 1": entry.get("location", {}).get("address", {}).get("line", ""),
            "City": entry.get("location", {}).get("address", {}).get("city", ""),
            "State": entry.get("location", {}).get("address", {}).get("stateCode", ""),
            "Zip": entry.get("location", {}).get("address", {}).get("postalCode", ""),
            "Listing Link": entry.get("href", ""),
            "Listing Status": entry.get("status", ""),
            "Provider Link": provider_link,
            "Agent Name": agent_name,
            "Agent Email": agent_email,
            "Video Tour Link": video_tour_link,
            "Matterport Link": matterport_link
        })

print(f"Data successfully exported to {output_file}")
