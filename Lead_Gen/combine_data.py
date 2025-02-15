import json
import csv
import os
from datetime import datetime

# Define the directory containing raw JSON files and the output directory for CSV
raw_data_dir = r"C:\Users\reich\Documents\GIT\katie\Lead_Gen\Raw_Data"
output_path = r"C:\Users\reich\Documents\GIT\katie\Lead_Gen\CSV_files"

# Generate output CSV file name with the current date
date = datetime.now().strftime("%Y_%m_%d")
output_file = os.path.join(output_path, f"Leads_{date}.csv")

# Define the CSV column headers
column_headers = [
    "Listing Status", "Agent Name", "Agent Email", "Agent Company", "Provider Link",
    "Address Line 1", "City", "State", "Zip", "List Price",
    "Video Tour Link", "Matterport Link", "Listing Link", "Description",
]

def export_json_to_csv(raw_data_dir, output_file):
    """
    This function reads multiple JSON files from a specified directory, extracts relevant property and agent data,
    and exports the cleaned data to a CSV file.
    
    The JSON files are expected to contain a list of properties, each with associated agent and listing details.
    
    Args:
    - raw_data_dir (str): Directory containing the raw JSON files.
    - output_file (str): Path where the output CSV file will be saved.
    """
    # Initialize total rows count
    total_rows = 0

    # Open CSV file and prepare to write data
    with open(output_file, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=column_headers)
        writer.writeheader()

        # Loop through all JSON files in the raw data directory
        for filename in os.listdir(raw_data_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(raw_data_dir, filename)

                # Read the JSON data from the file
                with open(file_path, "r", encoding="utf-8") as json_file:
                    data = json.load(json_file)

                # Ensure the data is a list of dictionaries
                if not isinstance(data, list):
                    raise ValueError(f"JSON data in {filename} should be a list of dictionaries")

                # Process each entry in the JSON data
                for entry in data:
                    # Extract agent details from the 'advertisers' field
                    advertisers_list = entry.get("advertisers", [])
                    agent_name = ", ".join(advertiser.get("name", "") for advertiser in advertisers_list if advertiser.get("name"))
                    agent_email = ", ".join(str(advertiser.get("email", "")) for advertiser in advertisers_list if advertiser.get("email") is not None)
                    agent_company = ", ".join(advertiser.get("href", "") for advertiser in advertisers_list if advertiser.get("href"))

                    # Extract provider link from 'providerUrl' if it's a dictionary
                    provider_url = entry.get("providerUrl")
                    provider_link = provider_url.get("href", "") if isinstance(provider_url, dict) else ""

                    # Extract video tour link if available
                    home_tours = entry.get("homeTours")
                    video_tour_link = ""
                    if isinstance(home_tours, dict):
                        virtual_tours = home_tours.get("virtualTours", [])
                        video_tour_link = ", ".join(tour.get("href", "") for tour in virtual_tours if tour.get("href"))

                    # Extract Matterport links if available
                    matterport_data = entry.get("matterport", {})
                    matterport_videos = matterport_data.get("videos", []) if isinstance(matterport_data, dict) else []
                    matterport_link = ", ".join(video.get("href", "") for video in matterport_videos if video.get("href"))

                    # Write the extracted data to the CSV file
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
                    
                    total_rows += 1  # Increment row count for each processed entry

    # Print summary of the process
    print(f"Data successfully exported to {output_file}")
    print(f"Total rows added: {total_rows}")

# Run the export function
export_json_to_csv(raw_data_dir, output_file)