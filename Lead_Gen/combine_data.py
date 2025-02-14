import json
import csv
import os
from datetime import datetime

# Define the directory containing raw JSON files
raw_data_dir = r"C:\Users\reich\Documents\GIT\katie\Lead_Gen\Raw_Data"

# Define the output CSV file
date = datetime.now().strftime("%Y_%m_%d")
output_path = r"C:\Users\reich\Documents\GIT\katie\Lead_Gen"
output_file = os.path.join(output_path, f"Leads_{date}.csv")

# Define the fields to extract
column_headers = [
    "Listing Status", "Agent Name", "Agent Email", "Agent Company", "Provider Link",
    "Address Line 1", "City", "State", "Zip", "List Price",
    "Video Tour Link", "Matterport Link", "Listing Link", "Description",
]

# Initialize row count
total_rows = 0

# Open CSV file once and append all data
with open(output_file, "w", newline="", encoding="utf-8") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=column_headers)
    writer.writeheader()

    # Loop through all JSON files in Raw_Data directory
    for filename in os.listdir(raw_data_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(raw_data_dir, filename)
            
            # Read JSON data
            with open(file_path, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)

            # Ensure data is a list of dictionaries
            if not isinstance(data, list):
                raise ValueError(f"JSON data in {filename} should be a list of dictionaries")

            for entry in data:
                # Extract agent details from advertisers
                advertisers_list = entry.get("advertisers", [])
                agent_name = ", ".join(advertiser.get("name", "") for advertiser in advertisers_list if advertiser.get("name"))
                agent_email = ", ".join(str(advertiser.get("email", "")) for advertiser in advertisers_list if advertiser.get("email") is not None)
                agent_company = ", ".join(advertiser.get("href", "") for advertiser in advertisers_list if advertiser.get("href"))

                # Ensure providerUrl exists and is a dictionary before accessing "href"
                provider_url = entry.get("providerUrl")
                provider_link = provider_url.get("href", "") if isinstance(provider_url, dict) else ""

                # Extract video tour links (if available)
                home_tours = entry.get("homeTours")
                video_tour_link = ""
                if isinstance(home_tours, dict):
                    virtual_tours = home_tours.get("virtualTours", [])
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
                    "Agent Company": agent_company,
                    "Video Tour Link": video_tour_link,
                    "Matterport Link": matterport_link
                })
                
                total_rows += 1  # Increment row count

# Print the total number of rows
print(f"Data successfully exported to {output_file}")
print(f"Total rows added: {total_rows}")
