# src/modules/notifications.py
import pandas as pd
from modules import utils
from db.connection import get_connection
import datetime as dt

def check_merger_notifications(user_id):
    df = utils.load_csv("merged_data_normalized_final.csv")
    today = utils.get_current_date()
    conn = get_connection()
    cur = conn.cursor()

    for _, row in df.iterrows():
        joint_date = utils.convertToDate(row['Joint Transaction Date'])
        if (joint_date - today).days == 0:  # Today merger effective
            msg = f"{row['Final Merged']} merger effective today!"
            cur.execute("INSERT INTO public.notifications(uid, message, date) VALUES(%s,%s,%s)",(user_id,msg,today))
    conn.commit()
    cur.close()
    conn.close()
