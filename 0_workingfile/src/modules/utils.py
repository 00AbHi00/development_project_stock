# src/modules/utils.py
import datetime as dt
import pandas as pd
import streamlit as st
import os
from modules import history


USERFILES_DIR = "../userfiles"
DATE_FILE = "data/currentDate.txt"

def convertToDate(dateString: str) -> dt.date:
    dateString = dateString.strip()  # remove trailing newline or spaces
    try:
        year, month, day = map(int, dateString.split('-'))
        return dt.date(year, month, day)
    except ValueError:
        raise ValueError(f"Invalid date format in {DATE_FILE}: '{dateString}'. Expected YYYY-MM-DD.")


def convertToString(date_obj: dt.date) -> str:
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


def process_corporate_actions(u1, current_date):
    """
    Check mergers, dividends, and right shares for the given date and update user's portfolio/money.
    """
    st.subheader("Corporate Actions Debug")
    st.write(f"{u1.username}'s Portfolio before actions: {u1.portfolio}")
    

    # --- MERGERS ---
    try:
        mergers = pd.read_csv("C:\CSIT\Abhi Semester 7\project\\0 Program\\0_workingfile\src\data\merged_data_normalized_final.csv")
        # st.write("Mergers file loaded", mergers.shape)

        # Normalize date strings for comparison
        today_mergers = mergers[
            mergers['Joint Transaction Date'].astype(str).str.strip() == current_date.strftime("%Y-%m-%d")
        ]
        # st.write(f"Checking mergers for: {current_date}")
        # st.write("Today’s mergers:", today_mergers)

        for _, row in today_mergers.iterrows():
            final_symbol = row['Final Merged']
            swap_ratio = row['Swap Ratio']  # e.g., "1:01:2"
            swap_parts = list(map(int, swap_ratio.split(":")))  # [1,1,2,...]

            total_qty = 0
            weighted_price_sum = 0
            updated = False

            # Loop over merger components
            for i in range(1, 6):
                merger_company = row.get(f'Merger {i}')
                # st.write(f"Checking merger component: {merger_company}")

                if merger_company and merger_company in u1.portfolio:
                    qty_old = u1.portfolio[merger_company]['quantity']
                    avg_price_old = u1.portfolio[merger_company]['avg_price']

                    swap_num = swap_parts[i-1] if i-1 < len(swap_parts) else 1
                    new_qty = qty_old * swap_num

                    total_qty += new_qty
                    weighted_price_sum += new_qty * avg_price_old

                    # st.write(f"Found in portfolio: {merger_company} | Old Qty={qty_old}, Swap={swap_num}, New Qty={new_qty}")

                    # Remove old company
                    del u1.portfolio[merger_company]
                    updated = True

            if updated and total_qty > 0:
                u1.portfolio[final_symbol] = {
                    'quantity': total_qty,
                    'avg_price': weighted_price_sum / total_qty
                }
                u1.update_json()
                # Log to history
                history.log_action(
                    u1.username,
                    "merger",
                    final_symbol,
                    {
                        "date": current_date.strftime("%Y-%m-%d"),
                        "merged_from": [row.get(f'Merger {i}') for i in range(1,6) if row.get(f'Merger {i}')],
                        "swap_ratio": swap_ratio,
                        "quantity": total_qty
                    }
                )
                # st.success(f"Merger applied: Portfolio updated with {final_symbol} → Qty={total_qty}")
            # else:
            #     st.warning(f"No matching portfolio companies found for merger into {final_symbol}")

    except FileNotFoundError:
        st.error("Merger data file not found.")

    # --- DIVIDENDS ---
    try:
        dividends = pd.read_csv("C:\CSIT\Abhi Semester 7\project\\0 Program\\0_workingfile\src\data\dividend.csv")
        today_dividends = dividends[dividends['Book Close'].astype(str).str.strip() == current_date.strftime("%Y-%m-%d")]
 
        for _, row in today_dividends.iterrows():
            company = row['Normalized name']
            st.write(company, row['Bonus %'], row['Cash %'])
            if company in u1.portfolio:
                qty = u1.portfolio[company]['quantity']
                bonus_pct = float(str(row['Bonus %']).replace('%','')) / 100
                cash_pct = float(str(row['Cash %']).replace('%','')) / 100
                bonus_qty = int(qty * bonus_pct)
                u1.portfolio[company]['quantity'] += bonus_qty
                cash_received = u1.portfolio[company]['avg_price'] * qty * cash_pct
                u1.money += cash_received
                u1.update_json()
                st.success(f"Dividend applied: {company}, Bonus={bonus_qty} shares, Cash={cash_received:.2f}")
                
                # Log dividend to history
                history.log_action(
                    u1.username,
                    "dividend",
                    company,
                    {
                        "date": current_date.strftime("%Y-%m-%d"),
                        "bonus_qty": bonus_qty,
                        "cash_received": cash_received
                    }
                )
    except FileNotFoundError:
        st.error("Dividend data file not found.")

    # --- RIGHT SHARE ---
    try:
        rights = pd.read_csv("C:\CSIT\Abhi Semester 7\project\\0 Program\\0_workingfile\src\data\\right_share.csv")
        # st.dataframe(rights)
        today_rights = rights[rights['Book Closure Date'] == current_date.strftime("%Y-%m-%d")]
        # st.write("Today’s right shares:", today_rights)

        for _, row in today_rights.iterrows():
            company = row['Name']
            if company in u1.portfolio:
                st.info(f" Right Share Available: {company}, Ratio={row['Ratio']}, Units={row['Units']}")
    except FileNotFoundError:
        st.error(" Right share data file not found.")
