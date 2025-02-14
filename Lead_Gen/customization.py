import pandas as pd
import os
import random

# File path to the CSV file
original_csv_file = r"C:\Users\reich\Documents\GIT\katie\Lead_Gen\Leads_2025_02_14.csv"

# Get the basename of the CSV file (without the directory and file extension)
basename = os.path.basename(original_csv_file).replace(".csv", "")

# Generate the pickle file path using the basename and replacing the prefix
pickle_file = os.path.join(os.path.dirname(original_csv_file), f"Customized_{basename}.pkl")
csv_file = os.path.join(os.path.dirname(original_csv_file), f"Customized_{basename}.csv")

# Check if pickle file exists, otherwise load the CSV and add the customization column
if os.path.exists(pickle_file):
    df = pd.read_pickle(pickle_file)
else:
    # Load the CSV file into a DataFrame and add the 'customization' column
    df = pd.read_csv(original_csv_file)
    df['customization'] = None  # Placeholder for customization

# Loop through the first 10 rows with empty 'customization' column and assign a random number
N = 100

count = 0
for index, row in df[df['customization'].isnull()].head(N).iterrows():
    address = df.at[index, 'Address Line 1']
    description = df.at[index, 'Description']
    agent_name = df.at[index, 'Agent Name']
    video_tour_link = df.at[index, 'Video Tour Link']
    matterport_link = df.at[index, 'Matterport Link']
    video_tour_exists = not pd.isna(video_tour_link)
    matterport_exists = not pd.isna(matterport_link)
    
    

    # df.at[index, 'customization'] = []
    count += 1

# Save the modified DataFrame as both CSV and pickle files
df.to_csv(csv_file, index=False)
df.to_pickle(pickle_file)

print(f"Updated {count} rows with customization values.")

non_empty_count = df['customization'].notnull().sum()
total_count = len(df)

print(f"{non_empty_count} of {total_count} rows have be completed.")