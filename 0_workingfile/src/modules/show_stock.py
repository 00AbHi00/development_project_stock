# src/modules/show_stock.py
import streamlit as st
import plotly.graph_objects as go
from modules.stock import Stock
from modules import utils

def plot_stock(stock_name):
    s = Stock(stock_name, "", "")
    df = s.get_OHLC()
    fig = go.Figure(data=[go.Candlestick(
        x=df['date'],
        open=df['price.prevClose'],
        high=df['price.max'],
        low=df['price.min'],
        close=df['price.close']
    )])
    st.plotly_chart(fig)
