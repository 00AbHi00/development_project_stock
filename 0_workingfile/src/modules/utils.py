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

def load_csv(filename, filter_date=True):
    path = os.path.join("data", filename)

    if not os.path.exists(path):
        st.warning(f"{filename} not found in data folder")
        return pd.DataFrame()

    df = pd.read_csv(path)

    # Only filter by date if requested and if 'date' column exists
    if filter_date and 'date' in df.columns:
        current_date = get_current_date()
        df['date'] = pd.to_datetime(df['date']).dt.date
        df = df[df['date'] == current_date]

    return df


def difference_of_dates(fromDate, toDate):
    delta = toDate - fromDate
    return delta.days


def load_plot_csv(filename, filter_date=None):
    """
    Load CSV and return all rows up to the given date (inclusive).
    If filter_date is None, return entire CSV.
    """
    path = os.path.join("data", filename)
    if not os.path.exists(path):
        st.warning(f"{filename} not found in data folder")
        return pd.DataFrame()

    df = pd.read_csv(path)

    # Ensure 'date' column exists
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date']).dt.date
        if filter_date:
            df = df[df['date'] <= filter_date]
    else:
        st.warning(f"'date' column not found in {filename}")
    
    return df