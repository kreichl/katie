import pandas as pd

# Replace with your actual file path
file_path = r'C:\Users\reich\Documents\GIT\katie\Lead_Gen\Leads_2025_02_14.csv'
output_path = r"C:\Users\reich\Documents\GIT\katie\Lead_Gen\Cleaned_Leads_2025_02_14.csv"

# Load the CSV file into a DataFrame
df = pd.read_csv(file_path)

# Count the number of rows before cleaning
initial_row_count = len(df)

# Remove rows where 'Agent Email' column is empty
df_cleaned = df[df['Agent Email'].notna() & (df['Agent Email'] != '')]

# Remove duplicate emails, keeping only the first occurrence
df_cleaned = df_cleaned.drop_duplicates(subset=['Agent Email'], keep='first')

# Count the number of rows deleted
deleted_row_count = initial_row_count - len(df_cleaned)

# Display the number of deleted rows
print(f"Rows Deleted:: {deleted_row_count}")

# Save the cleaned DataFrame to a new CSV file
df_cleaned.to_csv(output_path, index=False)

print(f"Total Rows: {len(df_cleaned)}")

print(f"Cleaned file saved as {output_path}")