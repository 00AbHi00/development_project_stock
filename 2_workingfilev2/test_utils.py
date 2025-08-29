#Unit test file for utils
import pytest as pt
from utils import convertToDate, differenceOfDates
import datetime as dt

def test_convertToDate():
    assert convertToDate('2012-01-01')==dt.date(2012,1,1)
    

def test_differenceOfDates():
    assert differenceOfDates(dt.date(2020,1,30),dt.date(2020,1,31),1 )== True ,"Test 1 fail"
    assert differenceOfDates(2020-1-30,dt.date(2020,1,31),1 )== "Error" , "Test 2 fail"
    # the day has passed
    assert differenceOfDates(dt.date(2020,1,31),dt.date(2020,1,30),1 )== False, "Test 3 fail"

    assert differenceOfDates(dt.date(2020,1,31),dt.date(2020,1,31),0 )== True, "Test 4 fail"
