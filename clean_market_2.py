import pandas as pd
import json
import datetime as dt
import re

try:
    date= "date\\" + str(dt.date(2010,4,15)) +'.json'
    print(date)
    with open(date,mode='r') as f:
        data=json.load(f)
        preety_data=json.dumps(data,indent=4)
        # print(preety_data)
        
        df=pd.json_normalize(data['data'])
        df.drop_duplicates(subset=['company.name','company.code'],inplace=True)
        # Extract the date using regex
        date_match = re.search(r'\d{4}-\d{2}-\d{2}', date)
        if date_match:
            clean_date = date_match.group(0)
            date=clean_date  # Output: 2010-04-15
            
        df[date]=date
        df.reindex()
        df.to_csv('path.csv')
        
except FileNotFoundError:
    print('Today is a holiday')