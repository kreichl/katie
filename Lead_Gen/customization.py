import pandas as pd
import os
import requests
import json
import time
import logging

# Get the directory of the current script
script_folder = os.path.dirname(os.path.abspath(__file__))

# Configure logging
log_file = os.path.join(script_folder,"customization_process.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(levelname)s | %(message)s',
)

# Number of Rows to Loop through
N = 3

# Wait Time between Requests
constant_wait_time = 2

# Load Prompts
prompts_file = r"C:\Users\reich\Documents\GIT\katie\Lead_Gen\Prompts\prompts_combined.json"
with open(prompts_file, 'r') as f:
    opening_prompts = json.load(f)

# File Names
original_csv_file = r"C:\Users\reich\Documents\GIT\katie\Lead_Gen\CSV_files\Cleaned_Leads_2025_02_14.csv"
basename = os.path.basename(original_csv_file).replace(".csv", "")
csv_file = os.path.join(os.path.dirname(original_csv_file), f"Customized_{basename}.csv")

# Load Data
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
else:
    df = pd.read_csv(original_csv_file)
    df['salutation'] = None
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

def submit_request(address, agent_name, agent_email, description, max_retries=5):
    """Submits a request to OpenAI API to generate an email opening with retry handling."""
    input_string = f"Agent Name: {agent_name}\nAgent Email: {agent_email}\nListing Address: {address}\nListing Description:\"{description}\"\n\nGenerate an email opening."
    
    data = opening_prompts.copy()
    data["messages"].append({
        "role": "user",
        "content": input_string
    })

    retries = 0
    while retries < max_retries:
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response_json = response.json()

            if response.status_code == 200:
                if "choices" in response_json and response_json["choices"]:
                    input_tokens = response_json.get("usage", {}).get("prompt_tokens", "Unknown")
                    response_tokens = response_json.get("usage", {}).get("completion_tokens", "Unknown")
                    total_tokens = response_json.get("usage", {}).get("total_tokens", "0")
                    cost = total_tokens * (0.150/1e6)
                    
                    logging.info(f"Input tokens: {input_tokens}")
                    logging.info(f"Response tokens: {response_tokens}")
                    logging.info(f"Cost: ${cost*1000:,.4f} per 1,000 rows\n")


                    return response_json["choices"][0]["message"]["content"]
                else:
                    raise KeyError("Missing 'choices' key in API response.")
            
            elif response.status_code == 429:
                wait_time = 2 ** retries
                logging.warning(f"Rate limited. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                retries += 1
                continue
            else:
                raise ValueError(f"API Error {response.status_code}: {response_json}")

        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            break

        except json.JSONDecodeError:
            logging.error("Error: Response is not valid JSON.")
            break
    
    logging.error("Max retries reached. Skipping this request.")
    return None

# Main Processing Loop
count = 0

try:
    for index, row in df[df['video_line'].isnull()].head(N).iterrows():

        logging.info(f"Processing row {count+1} of {N}\n")

        
        address = df.at[index, 'Address Line 1']
        description = df.at[index, 'Description']
        agent_name = df.at[index, 'Agent Name']
        agent_email = df.at[index, 'Agent Email']
        video_tour_link = df.at[index, 'Video Tour Link']
        matterport_link = df.at[index, 'Matterport Link']
        video_tour_exists = not pd.isna(video_tour_link)
        matterport_exists = not pd.isna(matterport_link)

        # Generate Customized Email Opening
        response = submit_request(address, agent_name, agent_email, description)
        
        if response:
            try:
                response_json = json.loads(response)
                
                df.at[index, 'Agent Email'] = response_json.get("email", "")
                df.at[index, 'salutation'] = response_json.get("salutation", "")
                df.at[index, 'email_opening'] = response_json.get("opening", "")
                
                logging.info(f"Email: {response_json.get('email', '')}")
                logging.info(f"Salutation: {response_json.get('salutation', '')}")
                logging.info(f"Opening: {response_json.get('opening', '')}\n")

            except json.JSONDecodeError:
                logging.error("Error: AI Model did not return its response in JSON")
        else:
            logging.error("Error: No email opening generated.")

        # Create Video Line
        video_line = "I’d love to help bring even more attention to your future listings with a professionally edited video."
        if matterport_exists:
            video_line = "I’d love to complement your Matterport tour with a professionally edited video."
        elif video_tour_exists:
            video_line = "I see you’re already using listing videos, which is a great way to attract buyers."
        
        df.at[index, 'video_line'] = video_line
        time.sleep(constant_wait_time)
        count += 1

except Exception as e:
    logging.critical(f"Critical Error Encountered: {e}")
    
finally:
    df.to_csv(csv_file, index=False)
    non_empty_count = df['video_line'].notnull().sum()
    total_count = len(df)
    logging.info(f"Updated {count} rows with customization values.")
    logging.info(f"{non_empty_count} of {total_count} rows have been completed.\n")
