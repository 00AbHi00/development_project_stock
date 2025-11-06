import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import f_oneway
from statsmodels.tsa.seasonal import STL



# --- Load your data ---
@st.cache_data
def load_data():
    # Replace 'your_data.csv' with your actual CSV file path
    df = pd.read_csv('nepse_index_history_all_sector.csv')

    # Clean and preprocess
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Remove commas and convert to float for relevant columns
    numeric_cols = ['Open', 'High', 'Low', 'Close', 'Change', 'Percentage change', 'Turnover']
    for col in numeric_cols:
        df[col] = df[col].astype(str).str.replace(',', '').astype(float)
    
    df = df.dropna(subset=['Date', 'Close', 'Category'])
    return df

df = load_data()

# Add Month info for grouping
df['Month'] = df['Date'].dt.month
df['MonthName'] = df['Date'].dt.strftime('%b')
df['YearMonth'] = df['Date'].dt.to_period('M').dt.to_timestamp()

# Select category for analysis
categories = df['Category'].unique()
selected_cat = st.selectbox("Select Category", categories)

cat_data = df[df['Category'] == selected_cat]

st.write(f"### Analysis for Category: {selected_cat}")

# Aggregate monthly average close price
monthly_avg = cat_data.groupby('YearMonth')['Close'].mean().reset_index()
monthly_avg = monthly_avg.set_index('YearMonth').asfreq('MS')  # Monthly frequency
monthly_avg['Close'] = monthly_avg['Close'].interpolate()

# Plot monthly average Close price time series
st.line_chart(monthly_avg['Close'])

# Seasonal decomposition using STL
from statsmodels.tsa.seasonal import STL
stl = STL(monthly_avg['Close'], seasonal=13)
res = stl.fit()

st.write("#### STL Decomposition")
fig, axs = plt.subplots(4, 1, figsize=(12, 9), sharex=True)
axs[0].plot(res.observed)
axs[0].set_title('Observed')
axs[1].plot(res.trend)
axs[1].set_title('Trend')
axs[2].plot(res.seasonal)
axs[2].set_title('Seasonal')
axs[3].plot(res.resid)
axs[3].set_title('Residual')
plt.tight_layout()
st.pyplot(fig)

# Plot average Close price by month of year
monthly_by_month = cat_data.groupby('Month')['Close'].mean().reset_index()
monthly_by_month['MonthName'] = monthly_by_month['Month'].apply(lambda x: pd.Timestamp(month=x, day=1, year=2020).strftime('%b'))
monthly_by_month = monthly_by_month.sort_values('Month')

fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.barplot(x='MonthName', y='Close', data=monthly_by_month, ax=ax2, palette='mako')
ax2.set_title('Average Close Price by Month (Aggregated)')
ax2.set_xlabel('Month')
ax2.set_ylabel('Average Close Price')
st.pyplot(fig2)

# ANOVA test for monthly differences in Close price
groups = [group['Close'].values for _, group in cat_data.groupby('Month')]
f_stat, p_val = f_oneway(*groups)

st.write(f"**ANOVA test for monthly differences:**")
st.write(f"F-statistic = {f_stat:.3f}")
st.write(f"p-value = {p_val:.5f}")

if p_val < 0.05:
    st.success("Significant differences exist between months (p < 0.05).")
else:
    st.info("No significant differences between months detected (p >= 0.05).")
