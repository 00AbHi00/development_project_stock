import json
import os
import datetime

#Cleaning the dataset required for simulation: This is only run once:
wk_days=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
# First Available date in the dataset
year=2010
month=4
day=15

dt=datetime.datetime(year,month,day)
count=0
while dt.year <2026:
    try:
        formattedDate=dt.strftime('%Y-%m-%d')
        fileName='date/'+formattedDate+'.json' 
        with open(fileName, 'r') as file:
            data = json.load(file)

        if(len(data['data'])>=1):
            print(formattedDate + wk_days[int(dt.weekday())])
            print(data)
        
        # Removing files with empty dataset
        if(len(data['data'])==0):
            os.remove(fileName)
        
        
        # Limit the number of loops in count
        if(len(data['data']) !=0):
            count=count+1


    except FileNotFoundError:
        print (f"{formattedDate} file not found")
    except json.JSONDecodeError:
        print(f'Invalid JSON in file: {fileName}')
    except Exception as e:
        print(f'Unexpected error with file {fileName}: {e}')
    dt=dt+ datetime.timedelta(days=1)
    
    print(dt.year==2025 and dt.month>6)
    if(dt.year==2025 and dt.month>6):
        break
    
    if (count>10):
        break
        

print(count)
# Total days of Data= 3414    
    
