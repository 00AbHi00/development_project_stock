import streamlit as st
import datetime as dt
import json


st.set_page_config(layout='wide')
# Current date
date=dt.date(2010,4,15)
filePath="date\\" + str(date) +'.json'
user="Ram"

r1,r2,r3=st.columns([3,4,4])
r1.subheader('Todays Date: '+ str(date), divider='blue')
r2.subheader(f'Welcome {user}',divider='red' )
r3.subheader('Todays Date: '+ str(date), divider='green')

try:
    with open(filePath,mode='r') as f:
        data=json.load(f)
        preety_data=json.dumps(data,indent=4)
        print(preety_data)
              
except(FileNotFoundError):
    st.header('Today is a holiday')
