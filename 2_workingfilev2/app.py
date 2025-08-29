import streamlit as st
import csv 
import user as U
import datetime as dt
import utils
import time


u1=U.User("Abhishek Silwal")
u1.getinfo()


#2012-3-12 Nepal Bangladesh Bank and Nepal Sri-Lanka Bank 
with open('currentDate.txt','r') as f:
    date=utils.convertToDate(f.read())



utils.addDays(10)
    
