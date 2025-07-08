import pandas as pd
import json
import datetime as dt
import re
import os

# Set the start and end dates
start_date = dt.date(2010, 4, 15)
end_date = dt.date(2018, 3, 10)

# Initialize an empty DataFrame to collect results
final_df = pd.DataFrame()

# Loop through all dates
current_date = start_date
while current_date <= end_date:
    try:
        # Construct the file path
        file_path = "date\\" + str(current_date) + ".json"
        print(file_path)
        # Read the JSON file
        with open(file_path, mode='r') as f:
            data = json.load(f)

            # Normalize the JSON structure into a DataFrame
            df = pd.json_normalize(data['data'])

            # Drop duplicates based on unique company
            df.drop_duplicates(subset=['company.name', 'company.code'], inplace=True)

            # Add the date column
            df['date'] = str(current_date)

            # Append to final DataFrame
            final_df = pd.concat([final_df, df], ignore_index=True)

    except FileNotFoundError:
        print(f"{current_date}: File not found (likely a holiday)")

#     # Move to next date
    current_date += dt.timedelta(days=1)

# # Save final DataFrame to CSV
final_df.to_csv('unique_shares_count.csv', index=False)

print("Saved successfully to 'unique_shares_count.csv'")
