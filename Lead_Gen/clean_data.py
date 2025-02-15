import pandas as pd
import os

# Directory and file names
dir_path = r"C:\Users\reich\Documents\GIT\katie\Lead_Gen\CSV_files"
file_name = "Leads_2025_02_14.csv"

# Construct full file paths
file_path = os.path.join(dir_path, file_name)
output_path = os.path.join(dir_path, f"Cleaned_{file_name}")

def clean_leads_data(input_path, output_path):
    """
    This function loads a CSV file containing real estate leads, cleans the data by:
    1. Removing rows where the 'Agent Email' column is empty.
    2. Removing duplicate emails, keeping the first occurrence.
    
    The cleaned data is then saved to a new CSV file.

    Args:
    - input_path (str): Path to the input CSV file.
    - output_path (str): Path where the cleaned CSV file will be saved.
    """
    # Load the CSV file into a DataFrame
    df = pd.read_csv(input_path)

    # Count the number of rows before cleaning
    initial_row_count = len(df)

    # Remove rows where 'Agent Email' column is empty or NaN
    df_cleaned = df[df['Agent Email'].notna() & (df['Agent Email'] != '')]

    # Remove duplicate emails, keeping only the first occurrence
    df_cleaned = df_cleaned.drop_duplicates(subset=['Agent Email'], keep='first')

    # Count the number of rows deleted
    deleted_row_count = initial_row_count - len(df_cleaned)

    # Print the number of deleted rows
    print(f"Rows Deleted: {deleted_row_count}")

    # Save the cleaned DataFrame to a new CSV file
    df_cleaned.to_csv(output_path, index=False)

    # Output the total number of rows in the cleaned data
    print(f"Total Rows after cleaning: {len(df_cleaned)}")
    print(f"Cleaned file saved as {output_path}")

# Run the data cleaning function
clean_leads_data(file_path, output_path)