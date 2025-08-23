import pandas as pd

# Load original metadata
df = pd.read_csv("clean1.csv")      # Contains: sn, Name, Symbol, Category
df2 = pd.read_csv("companies.csv")  # Transactional data (~600k rows)

print(df2)

# Ensure 'date' column is datetime
df2['date'] = pd.to_datetime(df2['date'])

# --- Step 1: First & Last Appearance Dates ---
date_stats = df2.groupby('company.name')['date'].agg(
    first_appear_date='min',
    last_appear_date='max'
).reset_index()

# --- Step 2: Monthly Average Closing Price ---
df2['month'] = df2['date'].dt.to_period('M').astype(str)  # e.g., '2021-05'

monthly_avg = df2.groupby(['company.name', 'month'])['price.close'].mean().reset_index()
monthly_avg = monthly_avg.pivot(index='company.name', columns='month', values='price.close')
monthly_avg.columns = [f"avg_close_{col}" for col in monthly_avg.columns]  # Rename columns
monthly_avg.reset_index(inplace=True)

# --- Step 3: Merge all together ---
# Start with df
enriched = df.merge(date_stats, left_on='Name', right_on='company.name', how='left')
enriched = enriched.merge(monthly_avg, left_on='Name', right_on='company.name', how='left')

# Drop duplicate join key columns
enriched = enriched.drop(columns=['company.name'], errors='ignore')


# --- Step 4: Save final enriched file ---
enriched.to_csv("clean1_enriched.csv", index=False)
