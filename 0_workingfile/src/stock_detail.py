import streamlit as st
from modules.user import User
from modules.stock import Stock
from modules.show_stock import plot_stock
from modules import utils

u1 = User(uid=1, name="Abhishek Silwal")

if "selected_stock" not in st.session_state:
    st.write("No stock selected. Go back to main page.")
else:
    stock_name = st.session_state["selected_stock"]
    st.title(f"Stock Details: {stock_name}")

    stock_data = Stock.get_stock_by_name(stock_name)
    st.write(stock_data)

    plot_stock(stock_name)

    # Buy shares
    qty = st.number_input("Quantity to buy:", min_value=1, value=1)
    if st.button("Buy"):
        u1.buy(stock_data, qty)
        st.success(f"Bought {qty} shares of {stock_name}")

    # Sell shares
    if stock_name in u1.portfolio:
        sell_qty = st.number_input("Quantity to sell:", min_value=1, value=1, key="sell_qty")
        if st.button("Sell"):
            u1.sell(stock_data, sell_qty)
            st.success(f"Sold {sell_qty} shares of {stock_name}")

    if st.button("Back to Main"):
        st.session_state.pop("selected_stock")
        st.rerun()
