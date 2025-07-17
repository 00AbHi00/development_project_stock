import pandas as pd
import json
import datetime as dt
import os

# Set the start and end dates
start_date = dt.date(2010, 4, 15)
end_date = dt.date(2025, 7, 10)

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

            # Check if both columns exist before dropping duplicates
            if 'company.name' in df.columns and 'company.code' in df.columns:
                df.drop_duplicates(subset=['company.name', 'company.code'], inplace=True)
            else:
                print(f"{current_date}: Missing expected company fields.")
                current_date += dt.timedelta(days=1)
                continue

            # Add the date column
            df['date'] = str(current_date)

            # Append to final DataFrame
            final_df = pd.concat([final_df, df], ignore_index=True)

    except FileNotFoundError:
        print(f"{current_date}: File not found (likely a holiday)")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"{current_date}: Error reading or parsing JSON: {e}")

    # Move to next date
    current_date += dt.timedelta(days=1)

# Save final DataFrame to CSV
os.makedirs('clean_outputs', exist_ok=True)
final_df.to_csv('clean_outputs/output2_unique_shares.csv', index=False)

print("Saved successfully to 'clean_outputs/output2_unique_shares.csv'")
