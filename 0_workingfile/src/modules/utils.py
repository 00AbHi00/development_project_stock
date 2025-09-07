# src/modules/utils.py
import datetime as dt
import pandas as pd
import streamlit as st
import os
import csv

DATE_FILE = "data/currentDate.txt"

def convertToDate(dateString: str):
    year, month, day = map(int, dateString.split('-'))
    return dt.date(year, month, day)

def convertToString(date_obj: dt.date):
    return date_obj.strftime("%Y-%m-%d")

def get_current_date():
    if not os.path.exists(DATE_FILE):
        with open(DATE_FILE, 'w') as f:
            f.write("2010-04-15")
    with open(DATE_FILE, 'r') as f:
        return convertToDate(f.read().strip())

def add_days(days=1):
    current = get_current_date()
    new_date = current + dt.timedelta(days=days)
    with open(DATE_FILE, 'w') as f:
        f.write(convertToString(new_date))
    return new_date

def load_csv(filename,date):
    path = os.path.join("data", filename)
    
    if os.path.exists(path):
        df = pd.read_csv(f"data/{filename}")
        df['date'] = pd.to_datetime(df['date']).dt.date
        return df[df['date'] == date]
    else:
        st.warning(f"{filename} not found in data folder")
        return pd.DataFrame()

def difference_of_dates(fromDate, toDate):
    delta = toDate - fromDate
    return delta.days
