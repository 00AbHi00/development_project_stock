import os
import datetime as dt
import csv
import streamlit as st
import pandas as pd

DATE_FILE = "data/currentDate.txt"

def convertToDate(dateString:str):
    tmpDate=dateString.split('-')
    return dt.date(int(tmpDate[0]),int(tmpDate[1]),int(tmpDate[2]))

def convertToString(date_obj: dt.date) -> str:
    return date_obj.strftime("%Y-%m-%d")

def differenceOfDates(fromDate, toDate, durationInDays=10):
    if not isinstance(fromDate, dt.date) or not isinstance(toDate, dt.date):
        return "Error"
    
    delta = toDate-fromDate
    
    if (delta.days <0):
        return False #assuming the day has already passed so no use of putting information
    
    if(delta.days<=durationInDays):
        return True
    return False

def get_current_date():
    with open('data\\currentDate.txt','r') as f:
        return convertToDate(f.read())


def addDays(days=1):
    current_date = get_current_date()
    new_date = current_date + dt.timedelta(days=days)
    with open('data\\currentDate.txt','w') as f:
        f.write(new_date.strftime('%Y-%m-%d'))  
        
        
def check_if_news():
    # Whenever the day is changed, this function should be triggered
    with open('data\\merged_data_normalized_final.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        current_date=get_current_date()
        for row in reader:
            approva_date=convertToDate(row["Final Approval Date"])    
            # st.write(approva_date) 
            merger_columns = ['Merger 1', 'Merger 2', 'Merger 3', 'Merger 4', 'Merger 5']

            # Build merger_companies string, skipping empty or NaN entries
            merger_companies = ' + '.join([str(row[col]) for col in merger_columns if pd.notna(row[col]) and row[col] != ''])

            # Check if the joint transaction is active (based on date difference)
            if differenceOfDates(current_date, convertToDate(row['Joint Transaction Date']), 0):
                text = f"{row['Final Merged']} is now active after joining {merger_companies} in the ratio {row['Swap Ratio']}"
                st.write(text)
            
            if(differenceOfDates(get_current_date(),approva_date,100)):
                st.write('New news of merger')
                # st.write(row)         
                return True
            
