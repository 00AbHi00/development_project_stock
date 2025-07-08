import streamlit as st
import random
from datetime import datetime, time, timedelta

# Simulated JSON input (simplified)
json_data = {
    "metadata": {
        "totalAmt": 140973249,
        "totalQty": 405900,
        "totalTrans": 1827
    },
    "data": [
        {
            "company": {"name": "Api Finance Limited", "code": None, "cat": None},
            "price": {"max": 247, "min": 240, "close": 240, "prevClose": 243, "diff": -3},
            "numTrans": 46,
            "tradedShares": 1520,
            "amount": 375070
        },
        {
            "company": {"code": "AHPC", "name": "Arun Valley Hydropower Development Co. Ltd.", "cat": "Hydro Power"},
            "price": {"max": 400, "min": 390, "close": 395, "prevClose": 398, "diff": -3},
            "numTrans": 100,
            "tradedShares": 5000,
            "amount": 1975000
        }
    ]
}

# Define 5 time zones (hourly snapshots)
time_slots = [time(10, 0), time(11, 0), time(12, 0), time(13, 0), time(14, 0)]

def get_available_time_slots():
    now = time(10,0,0)
    available = []
    for t in time_slots:
        slot_dt = now.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
        if slot_dt >= now:
            available.append(t.strftime("%H:%M"))
    return available if available else [time_slots[-1].strftime("%H:%M")]  # if none left, show last slot

def simulate_market(data, time_slot):
    random.seed(hash(time_slot))
    stocks = []
    for stock in data["data"]:
        min_price = stock["price"]["min"]
        max_price = stock["price"]["max"]
        live_price = round(random.uniform(min_price, max_price), 2)

        stocks.append({
            "company": stock["company"]["name"],
            "code": stock["company"].get("code"),
            "category": stock["company"].get("cat"),
            "price": live_price,
            "min": min_price,
            "max": max_price
        })
    return stocks

# Timer logic: time until next slot or market close
def time_until_next_slot():
    now = datetime.now()
    future_slots = []
    for t in time_slots:
        slot_dt = now.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
        if slot_dt > now:
            future_slots.append(slot_dt)
    if future_slots:
        next_slot = min(future_slots)
    else:
        # If market closed, next is tomorrow first slot
        next_slot = (now + timedelta(days=1)).replace(hour=time_slots[0].hour, minute=0, second=0, microsecond=0)
    return next_slot - now

# Initialize portfolio in session state
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {}

st.title("📈 Simulated Stock Market")

available_slots = get_available_time_slots()
selected_time = st.selectbox("Select Time Slot (cannot go back in time)", available_slots)

# Show countdown timer
delta = time_until_next_slot()
minutes, seconds = divmod(int(delta.total_seconds()), 60)
st.markdown(f"⏳ Time until next market update: **{minutes:02d}:{seconds:02d}**")

stocks = simulate_market(json_data, selected_time)
st.subheader(f"Market at {selected_time}")

for idx, stock in enumerate(stocks):
    col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
    col1.write(f"**{stock['company']}** ({stock['code'] or 'N/A'})")
    col2.write(f"Price: ${stock['price']}")
    col3.write(f"Range: {stock['min']}–{stock['max']}")
    
    shares_to_buy = col4.number_input(f"Buy shares", min_value=0, step=1, key=f"buy_{idx}")
    
    if col4.button("Buy", key=f"btn_{idx}"):
        if shares_to_buy > 0:
            if stock['company'] not in st.session_state.portfolio:
                st.session_state.portfolio[stock['company']] = {"shares": 0, "avg_price": 0.0}
            
            entry = st.session_state.portfolio[stock['company']]
            total_shares = entry["shares"] + shares_to_buy
            total_cost = entry["avg_price"] * entry["shares"] + stock["price"] * shares_to_buy
            avg_price = total_cost / total_shares
            
            st.session_state.portfolio[stock['company']] = {
                "shares": total_shares,
                "avg_price": avg_price
            }
            st.success(f"Bought {shares_to_buy} shares of {stock['company']} at ${stock['price']} each.")

st.subheader("👜 Your Portfolio")
if st.session_state.portfolio:
    for company, details in st.session_state.portfolio.items():
        st.write(f"{company}: {details['shares']} shares @ avg. price ${details['avg_price']:.2f}")
else:
    st.write("You haven't bought any shares yet.")
