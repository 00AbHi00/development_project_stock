#Unit test file for utils
# Run this
# PS C:\CSIT\Abhi Semester 7\project\0 Program\2_workingfilev2> pytest unit_tests/test_utils.py
import sys
import os
from utils import convertToDate, differenceOfDates
import datetime as dt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_convertToDate():
    assert convertToDate('2012-01-01')==dt.date(2012,1,1)
    

def test_differenceOfDates():
    assert differenceOfDates(dt.date(2020,1,30),dt.date(2020,1,31),1 )== True ,"Test 1 fail"
    assert differenceOfDates(2020-1-30,dt.date(2020,1,31),1 )== "Error" , "Test 2 fail"
    # the day has passed
    assert differenceOfDates(dt.date(2020,1,31),dt.date(2020,1,30),1 )== False, "Test 3 fail"

    assert differenceOfDates(dt.date(2020,1,31),dt.date(2020,1,31),0 )== True, "Test 4 fail"
