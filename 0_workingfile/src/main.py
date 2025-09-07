# src/main.py
import streamlit as st
from modules.user import User
from modules.stock import Stock
from modules.show_stock import plot_stock
from modules import utils, notifications
import datetime as dt 

# -----------------------------
# Initialize / Load User
# -----------------------------
if 'user' not in st.session_state:
    st.session_state['user'] = User(uid=1, name="Abhishek Silwal")
u1 = st.session_state['user']

# Current Date
current_date = utils.get_current_date()
st.subheader("Current Date:")
st.write(current_date)

# Next Day button
if st.button("Next Day"):
    utils.add_days(1)
    st.rerun()

# Stock selection state
if 'selected_stock' not in st.session_state:
    st.session_state['selected_stock'] = None

# -----------------------------
# Stock List View
# -----------------------------
if st.session_state['selected_stock'] is None:
    st.title("Stock Market Simulation")

    # Show Portfolio
    st.subheader("Portfolio Info:")
    st.write(u1.portfolio)

    # Load today's stocks
    df_stocks = Stock.load_current_stocks()

    # Search / filter section
    st.subheader("Filter Stocks")
    search_name = st.text_input("Search by Name")
    categories = ["All"] + sorted(df_stocks['Category'].dropna().unique())
    selected_category = st.selectbox("Filter by Category", categories)

    filtered_stocks = Stock.filter_stocks(df_stocks, name=search_name, category=selected_category)
    st.write(f"Showing {len(filtered_stocks)} stocks for {current_date}")

    # Display stocks with "View & Buy" button
    for idx, row in filtered_stocks.iterrows():
        col1, col2 = st.columns([3,1])
        with col1:
            st.write(f"**{row['Name']}** | Category: {row['Category']} | Price: {row['Average Price']} | Available: {row['tradedShares']}")
        with col2:
            if st.button("View & Buy", key=f"view_{idx}"):
                st.session_state['selected_stock'] = row['Name']
                st.rerun()

# -----------------------------
# Stock Detail / Buy View
# -----------------------------
else:
    stock_name = st.session_state['selected_stock']
    st.title(f"Stock Details: {stock_name}")

    # Load stock info
    stock_row = Stock.get_stock_by_name(stock_name)
    if stock_row is None:
        st.error("Stock data not found.")
    else:
        # Show current price and availability
        st.write(f"Price: {stock_row['Average Price']}")
        st.write(f"Available Shares: {stock_row['tradedShares']}")

        # Show historical OHLC chart
        st.subheader("Historical Data")
        plot_stock(stock_name)

        # Buy section
        max_qty = int(stock_row['tradedShares'])
        quantity = st.number_input("Quantity to buy", min_value=10, max_value=max_qty, value=10)

        # Calculate total cost including fees
        total_cost = u1.total_buy_cost(stock_row['Average Price'], quantity)
        st.info(f"💰 Total cost for {quantity} shares: Rs. {total_cost:.2f} (including broker commission, SEBON fee, DP charge)")

        # Confirmation before buy
        if st.button(f"Confirm Buy {quantity} shares of {stock_name}"):
            success = u1.buy(stock_row, quantity)
            if success:
                st.success(f" Bought {quantity} shares of {stock_name}. Remaining money: Rs. {u1.money:.2f}")
                st.rerun()  # Refresh portfolio display


        # Back button
        if st.button("Back to Stock List"):
            st.session_state['selected_stock'] = None
            st.rerun()

# -----------------------------
st.subheader("Sell Stocks from Portfolio")

import datetime as dt

if u1.portfolio:
    for symbol, info in u1.portfolio.items():
        col1, col2 = st.columns([3,1])
        with col1:
            st.write(f"**{symbol}** | Quantity: {info['quantity']} | Avg Price: {info['avg_price']}")
        with col2:
            sell_qty = st.number_input(f"Quantity to sell ({symbol})", min_value=10, max_value=info['quantity'], value=10, key=f"sell_{symbol}")

            # Load stock info as Series
            stock_row = Stock.get_stock_by_name(symbol)
            if stock_row is not None and not stock_row.empty:
                # Temporary Stock-like object
                stock_obj = type('StockObj', (), {})()
                stock_obj.symbol = symbol
                stock_obj.getPrice = lambda: stock_row['Average Price']
                stock_obj.quantity = stock_row['tradedShares']

                total_proceeds = u1.total_sell_proceeds(info['avg_price'], stock_obj.getPrice(), sell_qty)
                st.info(f"💰 You will receive Rs. {total_proceeds:.2f} for selling {sell_qty} shares (after fees & capital gains tax)")

                # Confirm button in main.py
                if st.button(f"Confirm Sell {sell_qty} shares of {symbol}", key=f"confirm_sell_{symbol}"):
                    # Call sell logic after confirmation
                    u1.sell(stock_obj, sell_qty)
                    st.rerun()
else:
    st.write("Your portfolio is empty.")
