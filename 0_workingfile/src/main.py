import streamlit as st
from modules.user import User
from modules.stock import Stock
from modules.show_stock import plot_stock
from modules import utils

u1 = User(uid=1, name="Abhishek Silwal")

st.title("Stock Market Simulation")

st.subheader("Current Date:")
st.write(utils.get_current_date())

if st.button("Next Day"):
    utils.add_days(1)
    st.rerun()

st.subheader("Portfolio Info:")
st.write(u1.portfolio)

st.subheader("Stocks")

# Load stocks for current date
df = Stock.load_all_stocks()

# Search by name
search_name = st.text_input("Search by company name:")

# Filter by category
categories = df['company.cat'].dropna().unique().tolist()
selected_category = st.selectbox("Filter by category:", ["All"] + categories)

# Apply search/filter
if selected_category != "All":
    df = Stock.filter_stocks(df, name=search_name, category=selected_category)
else:
    df = Stock.filter_stocks(df, name=search_name)

st.dataframe(df)
