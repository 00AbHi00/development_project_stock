import os
import datetime as dt

DATE_FILE = "currentDate.txt"
_last_loaded_date = None

def convertToDate(dateString:str):
    tmpDate=dateString.split('-')
    return dt.date(int(tmpDate[0]),int(tmpDate[1]),int(tmpDate[2]))

def convertToString(date_obj: dt.date) -> str:
    return date_obj.strftime("%Y-%m-%d")

def differenceOfDates(fromDate, toDate, durationInDays):
    if not isinstance(fromDate, dt.date) or not isinstance(toDate, dt.date):
        return "Error"
    
    delta = toDate-fromDate
    
    if (delta.days <0):
        return False #assuming the day has already passed so no use of putting information
    
    if(delta.days<=durationInDays):
        return True
    return False

def get_current_date():
    with open('currentDate.txt','r') as f:
        return convertToDate(f.read())


def addDays(days=1):
    current_date = get_current_date()
    new_date = current_date + dt.timedelta(days=days)
    with open('currentDate.txt','w') as f:
        f.write(new_date.strftime('%Y-%m-%d'))  