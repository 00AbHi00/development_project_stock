import streamlit as st
import csv 
import user as U
import datetime as dt
import utils
import time
import pandas as pd

@st.cache_data(show_spinner=False)
def load_data():
    return pd.read_csv('output4_fullFinal.csv')
df = load_data()

u1=U.User("Abhishek Silwal")
u1.getinfo()

st.write(utils.get_current_date())


#2012-3-12 Nepal Bangladesh Bank and Nepal Sri-Lanka Bank 
date=utils.get_current_date()

if (st.button("Click me")):
    utils.addDays(1)
    if(utils.check_if_news()):
        st.write('New news on chances of merger')

# Let user filter
filtered_df = df[df['date'].apply(utils.convertToDate) == utils.get_current_date()]
st.dataframe(filtered_df.head(10))


# st.dataframe(df[df['date']==utils.get_current_date()])

# selected_sector = st.selectbox("Select Sector", sorted(df['company.cat'].dropna().unique()))
# filtered_df = df[df['company.cat'] == selected_sector]

# st.dataframe(filtered_df.head(1000))