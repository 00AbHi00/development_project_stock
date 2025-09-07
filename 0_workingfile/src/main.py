# src/main.py
import streamlit as st
from modules.user import User, USERFILES_DIR
from modules.stock import Stock
from modules.show_stock import plot_stock
from modules import utils, notifications
import datetime as dt
import modules.history as history

# -----------------------------
# Enter / Load User
# -----------------------------
if 'user' not in st.session_state:
    username_input = st.text_input("Enter your username", value="Abhishek Silwal")
    if st.button("Load / Create User"):
        # uid can be simple hash or 1 for now
        st.session_state['user'] = User(uid=1, name=username_input)
        st.rerun()

if 'user' in st.session_state:
    u1 = st.session_state['user']

    # Current Date
    current_date = utils.get_current_date()
    st.subheader("Current Date:")
    st.write(current_date)

    # utils.process_corporate_actions(u1, current_date)
    # Next Day button
    if st.button("Next Day"):
        utils.add_days(1)  
        utils.process_corporate_actions(u1, current_date)
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
        st.subheader(f"{u1.username}'s Portfolio Info:")
        st.write(u1.portfolio)
        st.write(f" Remaining Money: Rs. {u1.money:.2f}")

        # Load today's stocks
        df_stocks = Stock.load_current_stocks()
        
        if df_stocks.empty:
            st.warning("No stock data available for today.")
            st.header("Market is closed today.")
            value=0
            st.stop()
        
        
        # Search / filter section
        st.subheader("Filter Stocks")
        search_name = st.text_input("Search by Name")
        categories = ["All"] + sorted(df_stocks['Category'].dropna().unique())
        selected_category = st.selectbox("Filter by Category", categories)

        filtered_stocks = Stock.filter_stocks(df_stocks, name=search_name, category=selected_category)
        st.write(f"Showing {len(filtered_stocks)} stocks for {current_date}")

        min_price, max_price = st.slider("Price Range", 0.0, float(df_stocks['Average Price'].max()), (0.0, float(df_stocks['Average Price'].max())))
        filtered_stocks = filtered_stocks[(filtered_stocks['Average Price'] >= min_price) & (filtered_stocks['Average Price'] <= max_price)]
        # st.write(f"After price filter: {len(filtered_stocks)} stocks")
            
        # Display stocks with "View & Buy" button
        for idx, row in filtered_stocks.iterrows():
            col1, col2 = st.columns([3,1])
            with col1:
                st.write(f"**{row['Name']}** | Category: {row['Category']} | Price: {row['Average Price']} ")
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
            st.write(f"Price: {stock_row['Average Price']}")
            st.write(f"Available Shares: {stock_row['tradedShares']}")

            st.subheader("Historical Data")
            plot_stock(stock_name)

            # Buy section
            max_qty = int(stock_row['tradedShares'])
            quantity = st.number_input("Quantity to buy", min_value=10, max_value=max_qty, value=10)
            total_cost = u1.total_buy_cost(stock_row['Average Price'], quantity)
            st.info(f"Total cost for {quantity} shares: Rs. {total_cost:.2f} (including fees)")

            if st.button(f"Confirm Buy {quantity} shares of {stock_name}"):
                success = u1.buy(stock_row, quantity)
                if success:
                    st.success(f" Bought {quantity} shares of {stock_name}. Remaining money: Rs. {u1.money:.2f}")
                    history.log_action(
                        username=u1.username,
                        action_type="buy",
                        company=stock_name,
                        details={
                            "date": current_date.strftime("%Y-%m-%d"),
                            "quantity": quantity,
                            "price_per_share": stock_row['Average Price'],
                            "total_cost": total_cost
                        }
                    )
                    st.rerun()

            if st.button("Back to Stock List"):
                st.session_state['selected_stock'] = None
                st.rerun()

    # -----------------------------
    # Sell from Portfolio
    # -----------------------------
    st.subheader("Sell Stocks from Portfolio")

    if u1.portfolio:
        for symbol, info in u1.portfolio.items():
            col1, col2 = st.columns([3,1])
            with col1:
                st.write(f"**{symbol}** | Quantity: {info['quantity']} | Avg Price: {info['avg_price']}")
            with col2:
                sell_qty = st.number_input(f"Quantity to sell ({symbol})", min_value=0, max_value=info['quantity'], value=min(10,info['quantity']), key=f"sell_{symbol}")

                stock_row = Stock.get_stock_by_name(symbol)
                if stock_row is not None and not stock_row.empty:
                    # Stock-like object for sell
                    stock_obj = type('StockObj', (), {})()
                    stock_obj.symbol = symbol
                    stock_obj.getPrice = lambda: stock_row['Average Price']
                    stock_obj.quantity = stock_row['tradedShares']

                    total_proceeds = u1.total_sell_proceeds(info['avg_price'], stock_obj.getPrice(), sell_qty)
                    st.info(f"💰 You will receive Rs. {total_proceeds:.2f} for selling {sell_qty} shares")

                    if st.button(f"Confirm Sell {sell_qty} shares of {symbol}", key=f"confirm_sell_{symbol}"):
                        u1.sell(stock_obj, sell_qty)
                        history.log_action(
                            username=u1.username,
                            action_type="sell",
                            company=symbol,
                            details={
                                "date": current_date.strftime("%Y-%m-%d"),
                                "quantity": sell_qty,
                                "price_per_share": stock_obj.getPrice(),
                                
                                "total_proceeds": total_proceeds
                            }
                        )
                        st.rerun()
    else:
        st.write("Your portfolio is empty.")


