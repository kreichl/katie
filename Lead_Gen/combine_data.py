import json
import csv
import os
from datetime import datetime

# Define Path of Raw Data
path = r"C:\Users\reich\Documents\GIT\katie\Lead_Gen\Raw_Data\Waukesha.json"
input_file = path

# Define the fields to extract
column_headers = ["List Price", "Address Line 1", "Description"]

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
        writer.writerow({
            "List Price": entry.get("listPrice", ""),
            "Description": entry.get("description", {}).get("text", ""),
            "Address Line 1": entry.get("location", {}).get("address", "").get("line", ""),
        })

print(f"Data successfully exported to {output_file}")