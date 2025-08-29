import streamlit as st
import csv 
import user as U
import datetime as dt
import utils
import time


u1=U.User("Abhishek Silwal")

st.button("Item",on_click=u1.getinfo())


#2012-3-12 Nepal Bangladesh Bank and Nepal Sri-Lanka Bank 
with open('currentDate.txt','r') as f:
    date=utils.convertToDate(f.read())

# Whenever the day is changed, this function should be triggered
with open('merged_data_normalized_final.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        approva_date=utils.convertToDate(row["Final Approval Date"])    
        # st.write(row['Sno'])
        # st.write(approva_date) 
        if(utils.differenceOfDates(date,approva_date,10)):
            st.write("Time to show the particular news")

utils.addDays(10)
    
