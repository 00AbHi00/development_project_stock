import plotly.graph_objects as go
from modules import utils
import streamlit as st

def plot_stock(stock_name):
    # Load historical data up to current date
    current_date = utils.get_current_date()
    df = utils.load_plot_csv("final_clean_data.csv", filter_date=current_date)

    # Filter for the specific stock
    df_stock = df[df['company.name'] == stock_name].sort_values('date')

    if df_stock.empty:
        st.warning("No data available for this stock")
        return

    # Limit to last 5 dates for range slider
    df_stock_last5 = df_stock.tail(10)

    fig = go.Figure(data=[go.Candlestick(
        x=df_stock['date'],
        open=df_stock['price.prevClose'],
        high=df_stock['price.max'],
        low=df_stock['price.min'],
        close=df_stock['price.close'],
        name=stock_name
    )])

    fig.update_layout(
        title=f"OHLC Chart: {stock_name}",
        xaxis_title="Date",
        yaxis_title="Price",
        yaxis=dict(range=[0, df_stock['price.max'].max() * 1.1]),  # start y-axis from 0
        xaxis_rangeslider_visible=True,  # keep slider visible
        xaxis_range=[df_stock_last5['date'].iloc[0], df_stock_last5['date'].iloc[-1]],  # only last 5 dates
        dragmode='pan'
    )

    st.plotly_chart(fig, use_container_width=True)
