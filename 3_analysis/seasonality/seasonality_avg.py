import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv('nepse_index_history_all_sector.csv')

# Convert Date column to datetime
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Remove commas from numeric columns (like 'Close') and convert to float
df['Close'] = df['Close'].astype(str).str.replace(',', '').astype(float)

# Optional: Remove or handle any rows where Close conversion failed (NaN)
df = df.dropna(subset=['Close', 'Date', 'Category'])

# Extract Year and Month
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month

# Now groupby with cleaned numeric column
df_grouped = df.groupby(['Year', 'Month', 'Category'])['Close'].mean().reset_index()

for (i, row) in df_grouped.iterrows():
    df_grouped['Price_increase'] = df_grouped['Close'].pct_change() * 100
df_grouped.dropna(subset=['Price_increase'], inplace=True)
print(df_grouped.head())

# plotting on 12 months stacking months per category
plt.figure(figsize=(12, 6))
categories = df_grouped['Category'].unique()
for category in categories:
    cat_data = df_grouped[df_grouped['Category'] == category]
    # Differentiate months by color
    
    
    plt.plot(cat_data['Month'], cat_data['Price_increase'], marker='o', label=category)
    plt.title('Average Monthly Price Increase by Category')
    plt.xlabel('Month')
    plt.ylabel('Average Price Increase (%)')
    
    plt.xticks(range(1, 13))
    plt.legend()
    plt.grid()
    plt.show()

