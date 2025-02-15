import pandas as pd
import os
import requests
import json

# Number of Rows to Loop through
N = 100

# Prompts File
email_opening_prompts_file = r"C:\Users\reich\Documents\GIT\katie\Lead_Gen\prompts_email_opening.json"
email_duplicates_prompts_file = r"C:\Users\reich\Documents\GIT\katie\Lead_Gen\prompts_multiple_emails.json"

# Load Prompts
with open(email_opening_prompts_file, 'r') as f:
    opening_prompts = json.load(f)
with open(email_duplicates_prompts_file, 'r') as f:
    duplicate_prompts = json.load(f)

# File Names
original_csv_file = r"C:\Users\reich\Documents\GIT\katie\Lead_Gen\Cleaned_Leads_2025_02_14.csv"
basename = os.path.basename(original_csv_file).replace(".csv", "")
pickle_file = os.path.join(os.path.dirname(original_csv_file), f"Customized_{basename}.pkl")
csv_file = os.path.join(os.path.dirname(original_csv_file), f"Customized_{basename}.csv")

# Load Data
if os.path.exists(pickle_file):
    df = pd.read_pickle(pickle_file)
else:
    df = pd.read_csv(original_csv_file)
    df['email_opening'] = None
    df['video_line'] = None

# OpenAI API Information
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("API key is not set in the environment variables.")
url = 'https://api.openai.com/v1/chat/completions'
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}

def submit_request_opening(address, agent_name, description):
    """Submits a request to OpenAI API to generate an email opening."""
    
    input_string = f"Agent Name: {agent_name}\nListing Address: {address}\nListing Description:\"{description}\"\n\nGenerate an email opening."
    
    data = opening_prompts.copy()
    data["messages"].append({
        "role": "user",
        "content": input_string
    })

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_json = response.json()

        # Ensure valid response
        if response.status_code != 200:
            raise ValueError(f"API Error {response.status_code}: {response_json}")

        if "choices" not in response_json or not response_json["choices"]:
            raise KeyError("Missing 'choices' key in API response.")

        return response_json["choices"][0]["message"]["content"]

    except Exception as e:
        print(f"Error in submit_request_opening: {e}")
        return None  # Return None if an error occurs

def submit_request_duplicates(email):
    """Submits a request to OpenAI API to process duplicate emails."""
    
    data = duplicate_prompts.copy()
    data["messages"].append({
        "role": "user",
        "content": email
    })

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_json = response.json()

        # Ensure valid response
        if response.status_code != 200:
            raise ValueError(f"API Error {response.status_code}: {response_json}")

        if "choices" not in response_json or not response_json["choices"]:
            raise KeyError("Missing 'choices' key in API response.")

        return response_json["choices"][0]["message"]["content"]

    except Exception as e:
        print(f"Error in submit_request_duplicates: {e}")
        return email  # Return original email if an error occurs

# Main Processing Loop
count = 0

try:
    for index, row in df[df['video_line'].isnull()].head(N).iterrows():
        address = df.at[index, 'Address Line 1']
        description = df.at[index, 'Description']
        agent_name = df.at[index, 'Agent Name']
        agent_email = df.at[index, 'Agent Email']
        video_tour_link = df.at[index, 'Video Tour Link']
        matterport_link = df.at[index, 'Matterport Link']
        video_tour_exists = not pd.isna(video_tour_link)
        matterport_exists = not pd.isna(matterport_link)

        # Generate Customized Email Opening
        email_opening = submit_request_opening(address, agent_name, description)
        df.at[index, 'email_opening'] = email_opening

        print("--------------------")
        print(email_opening if email_opening else "Error: No email opening generated.")

        # Create Video Line
        if not video_tour_exists and not matterport_exists:
            video_line = "I’d love to help bring even more attention to your future listings with a professionally edited video."
        elif matterport_exists:
            video_line = "I’d love to complement your Matterport tour with a professionally edited video."
        elif video_tour_exists:
            video_line = "I see you’re already using listing videos, which is a great way to attract buyers."
        else:
            video_line = "I’d love to help bring even more attention to your future listings with a professionally edited video."

        df.at[index, 'video_line'] = video_line

        # Check Email Field
        if "," in agent_email:
            single_email = submit_request_duplicates(agent_email)
            df.at[index, 'Agent Email'] = single_email

        count += 1

except Exception as e:
    print(f"\nCritical Error Encountered: {e}")
    
finally:
    # Save progress before exiting
    df.to_csv(csv_file, index=False)
    df.to_pickle(pickle_file)
    
    # Display stats
    non_empty_count = df['video_line'].notnull().sum()
    total_count = len(df)

    print(f"\nUpdated {count} rows with customization values.")
    print(f"{non_empty_count} of {total_count} rows have been completed.")
