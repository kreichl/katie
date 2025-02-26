import pandas as pd
import os
import requests
import json
import time
import logging

# Constants for process control
N = 1000  # Number of rows to process in one run
constant_wait_time = 8  # Time to wait between requests (in seconds)

# Get the directory of the current script
script_folder = os.path.dirname(os.path.abspath(__file__))

# Configure logging to track the customization process
log_file = os.path.join(script_folder, "customization_process.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
)

# Load opening prompts from a JSON file
prompts_file = r"C:\Users\reich\Documents\GIT\katie\Lead_Gen\Prompts\prompts_combined.json"

# Define file paths
original_csv_file = r"C:\Users\reich\Documents\GIT\katie\Lead_Gen\CSV_files\Cleaned_Leads_2025_02_14.csv"
basename = os.path.basename(original_csv_file).replace(".csv", "")
csv_file = os.path.join(os.path.dirname(original_csv_file), f"Customized_{basename}.csv")

# Load the CSV file or create a new one with necessary columns
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
else:
    df = pd.read_csv(original_csv_file)
    df['salutation'] = None
    df['email_opening'] = None
    df['video_line'] = None

# OpenAI API setup
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("API key is not set in the environment variables.")
url = 'https://api.openai.com/v1/chat/completions'
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}

def generate_ai_request(prompts_file, user_prompt, max_retries=5):
    """
    Submits a generic request to the OpenAI API with retry handling.

    Args:
    - prompts_file (dict): The JSON prompts file containing the base template.
    - user_prompt (str): The specific user input to be appended to the prompts.
    - max_retries (int): The maximum number of retries in case of failure (default is 5).

    Returns:
    - str: The response generated by the AI, or None if the request fails.
    """
    retries = 0

    # Load the prompt template
    with open(prompts_file, 'r') as f:
        data = json.load(f)

    # Append the user prompt to the template
    data["messages"].append({
        "role": "user",
        "content": user_prompt
    })

    # Retry logic
    while retries < max_retries:
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response_json = response.json()

            # Check the response status
            if response.status_code == 200:
                if "choices" in response_json and response_json["choices"]:
                    input_tokens = response_json.get("usage", {}).get("prompt_tokens", "Unknown")
                    response_tokens = response_json.get("usage", {}).get("completion_tokens", "Unknown")
                    total_tokens = response_json.get("usage", {}).get("total_tokens", "0")
                    cost = total_tokens * (0.150/1e6)

                    # logging.info(f"Input tokens: {input_tokens}")
                    # logging.info(f"Response tokens: {response_tokens}")
                    # logging.info(f"Cost: ${cost*1000:,.4f} per 1,000 rows\n")

                    return response_json["choices"][0]["message"]["content"]
                else:
                    raise KeyError("Missing 'choices' key in API response.")
            
            elif response.status_code == 429:
                wait_time = 2 ** retries
                logging.warning(f"Rate limited. Retrying in {wait_time} seconds...")
                print(f"Rate limited. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                retries += 1
                continue
            else:
                raise ValueError(f"API Error {response.status_code}: {response_json}")

        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            print(f"Request failed: {e}")
            break

        except json.JSONDecodeError:
            logging.error("Response is not valid JSON.")
            print("Error: Response is not valid JSON.")
            break
    
    logging.error("Max retries reached. Skipping this request.")
    print("Error: Max retries reached. Skipping this request.")
    return None


def submit_request(address, agent_name, agent_email, description, prompts_file, max_retries=5):
    """
    Submits a request to the OpenAI API to generate an email opening with retry handling using the generate_ai_request function.
    
    Args:
    - address (str): The address of the property.
    - agent_name (str): The name of the agent.
    - agent_email (str): The email of the agent.
    - description (str): The property description.
    - prompts_file (str): The file path to the prompts JSON.
    - max_retries (int): The maximum number of retries in case of failure (default is 5).

    Returns:
    - str: The email opening generated by the AI, or None if the request fails.
    """
    # Construct the user input prompt
    user_prompt = f"Agent Name: {agent_name}\nAgent Email: {agent_email}\nListing Address: {address}\nListing Description:\"{description}\"\n\nGenerate an email opening."
    
    # Call the generic AI request function
    return generate_ai_request(prompts_file, user_prompt, max_retries)

# Main Processing Loop
count = 0

try:
    # Process rows that haven't been customized yet
    for index, row in df[df['video_line'].isnull()].head(N).iterrows():
        print(f"Processing row {count+1} of {N} (Row {index+1})")

        # Extract details for the current row
        address = df.at[index, 'Address Line 1']
        description = df.at[index, 'Description']
        agent_name = df.at[index, 'Agent Name']
        agent_email = df.at[index, 'Agent Email']
        video_tour_link = df.at[index, 'Video Tour Link']
        matterport_link = df.at[index, 'Matterport Link']
        video_tour_exists = not pd.isna(video_tour_link)
        matterport_exists = not pd.isna(matterport_link)

        # Generate the customized email opening
        response = submit_request(address, agent_name, agent_email, description, prompts_file)
        
        if response:
            try:
                response_json = json.loads(response)
                
                # Update the dataframe with the AI-generated content
                df.at[index, 'Agent Email'] = response_json.get("email", "")
                df.at[index, 'salutation'] = response_json.get("salutation", "")
                df.at[index, 'email_opening'] = response_json.get("opening", "")
                
                logging.info(f"Email: {response_json.get('email', '')}")
                logging.info(f"Salutation: {response_json.get('salutation', '')}")
                logging.info(f"Opening: {response_json.get('opening', '')}\n")

            except json.JSONDecodeError:
                logging.error("AI Model did not return its response in JSON")
                print("Error: AI Model did not return its response in JSON")
        else:
            logging.error("No email opening generated.")
            print("Error: No email opening generated.")

        # Create a customized video line based on the links available
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
    print(f"Critical Error Encountered: {e}")
    
finally:
    # Save the updated DataFrame to the new CSV file
    df.to_csv(csv_file, index=False)
    non_empty_count = df['video_line'].notnull().sum()
    total_count = len(df)

    # Print Status
    print(f"\nUpdated {count} rows with customization values.")
    print(f"{non_empty_count} of {total_count} rows have been completed.\n")
    logging.info(f"{non_empty_count} of {total_count} rows have been completed.\n")
