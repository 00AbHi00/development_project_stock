import streamlit as st
import datetime as dt
import json
import os
import pandas as pd

st.set_page_config(layout='wide')

# Initialize session state
if 'date' not in st.session_state:
    st.session_state.date = dt.date(2010, 4, 15)

# File path
filePath = os.path.join("../date", f"{st.session_state.date}.json")
user = "Ram"

# Display headers
r1, r2, r3 = st.columns([3, 4, 4])
r1.subheader('Today\'s Date: ' + str(st.session_state.date), divider='blue')
r2.subheader(f'Welcome {user}', divider='red')
r3.subheader('Today\'s Date: ' + str(st.session_state.date), divider='green')

# Load and display JSON data
try:
    with open(filePath, mode='r') as f:
        json_data = json.load(f)
        json_pretty_data = json.dumps(json_data, indent=4)
         # Display Market Summary
    st.subheader("Market Summary")
    st.metric("Total Amount", json_data['metadata']['totalAmt'])
    st.metric("Total Quantity", json_data['metadata']['totalQty'])
    st.metric("Total Transactions", json_data['metadata']['totalTrans'])

    # Normalize and show data
    df = pd.json_normalize(json_data['data'])  # ONLY normalize the 'data' section

    # Optional: Rename for clarity
    df = df.rename(columns={
        'company.name': 'Company Name',
        'amount': 'Amount',
        'numTrans': 'Transactions',
        'price.close': 'Close Price',
        'price.diff': 'Price Change',
        'price.max': 'Max Price',
        'price.min': 'Min Price',
        'price.prevClose': 'Previous Close',
        'tradedShares': 'Shares Traded'
    })

    st.subheader("Trading Data")
    st.dataframe(df)

                
except FileNotFoundError:
    st.header('Today is a holiday')
    # st.header(filePath)

# Button to go to next day
if st.button("Go to Next day:"):
    st.session_state.date += dt.timedelta(days=1)
    st.experimental_set_query_params(date=st.session_state.date.isoformat())
    st.rerun()  # Force the app to rerun with updated date
