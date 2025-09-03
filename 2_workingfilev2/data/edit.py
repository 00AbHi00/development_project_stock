import pandas as pd

# Load both files
company_list = pd.read_csv("clean1_updated_8_28_25.csv")
trade_data = pd.read_csv("output4_fullFinal.csv")

# Ensure date column is in datetime format
trade_data['date'] = pd.to_datetime(trade_data['date'], errors='coerce')
trade_data = trade_data.dropna(subset=['date'])  # Drop rows with invalid dates

# Normalize names for matching
trade_data['company.name'] = trade_data['company.name'].str.strip().str.lower()
company_list['Name_clean'] = company_list['Name'].str.strip().str.lower()  # Keep original 'Name' intact

# Create a list to store rows with additional info
results = []

for _, row in company_list.iterrows():
    name = row['Name_clean']
    
    # Get the matching trades
    matched = trade_data[trade_data['company.name'] == name]

    # Prepare output row with all original company data
    output_row = row.drop('Name_clean').to_dict()  # Drop helper column

    if matched.empty:
        output_row.update({
            'First Traded Price': None,
            'First Traded Date': None,
            'Last Traded Price': None,
            'Last Traded Date': None,
            'Note': 'No matching data'
        })
    else:
        matched = matched.sort_values(by='date')
        first = matched.iloc[0]
        last = matched.iloc[-1]
        
        output_row.update({
            'First Traded Price': first['price.close'],
            'First Traded Date': first['date'].date(),
            'Last Traded Price': last['price.close'],
            'Last Traded Date': last['date'].date()
        })
    
    results.append(output_row)

# Convert to DataFrame and save
final_df = pd.DataFrame(results)
final_df.to_csv("final_comp_info.csv", index=False)

print("Done! File saved as 'company_with_first_last_trade_data.csv'")
