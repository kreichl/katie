import pandas as pd
import os
import random
import requests
import json

# Number of Rows to Loop through
N = 1

# File Names
original_csv_file = r"C:\Users\reich\Documents\GIT\katie\Lead_Gen\Cleaned_Leads_2025_02_14.csv"
basename = os.path.basename(original_csv_file).replace(".csv", "")
pickle_file = os.path.join(os.path.dirname(original_csv_file), f"Customized_{basename}.pkl")
csv_file = os.path.join(os.path.dirname(original_csv_file), f"Customized_{basename}.csv")

# Load Data
if os.path.exists(pickle_file):
    df = pd.read_pickle(pickle_file)
else:
    # Load the CSV file into a DataFrame and add the 'customization' column
    df = pd.read_csv(original_csv_file)
    df['customization'] = None 

# OpenAI API Information
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("API key is not set in the environment variables.")
url = 'https://api.openai.com/v1/chat/completions'
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}

# Loop through rows
count = 0
for index, row in df[df['customization'].isnull()].head(N).iterrows():

    # Extract Relevant Data
    address = df.at[index, 'Address Line 1']
    description = df.at[index, 'Description']
    agent_name = df.at[index, 'Agent Name']
    video_tour_link = df.at[index, 'Video Tour Link']
    matterport_link = df.at[index, 'Matterport Link']
    video_tour_exists = not pd.isna(video_tour_link)
    matterport_exists = not pd.isna(matterport_link)

    print(f"Matterport: {matterport_exists}")
    print(f"Video Tour: {video_tour_exists}")

    # If no Video or Matterport
    if not video_tour_exists and not matterport_exists:
        print(f"{address}")
    
    # df.at[index, 'customization'] = ["Video"]

    count += 1

# Save the modified DataFrame as both CSV and pickle files
df.to_csv(csv_file, index=False)
df.to_pickle(pickle_file)

# Display Stats
non_empty_count = df['customization'].notnull().sum()
total_count = len(df)

# print(f"Updated {count} rows with customization values.")
# print(f"{non_empty_count} of {total_count} rows have be completed.")