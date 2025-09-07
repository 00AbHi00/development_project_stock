# src/modules/user.py
from modules import utils, stock
from db.connection import get_connection
import streamlit as st
import datetime as dt

class User:
    def __init__(self, uid, name, money=100000):
        self.uid = uid
        self.name = name
        self.money = money
        self.portfolio = {}  # symbol -> {'quantity', 'avg_price'}
        self.transactions = []

    # Calculate total cost including fees for buying
    def total_buy_cost(self, share_price, quantity):
        calculated_total = share_price * quantity
        dpCharge = 25
        sebonFeePercent = 0.00015
        
        if calculated_total <= 50000:
            brokerFeePercent = 0.0036
        elif calculated_total <= 500000:
            brokerFeePercent = 0.0033
        elif calculated_total <= 2000000:
            brokerFeePercent = 0.0031
        elif calculated_total <= 10000000:
            brokerFeePercent = 0.0027
        else:
            brokerFeePercent = 0.0024
        
        sebonFee = calculated_total * sebonFeePercent
        brokerFee = calculated_total * brokerFeePercent
        total_price = calculated_total + sebonFee + brokerFee + dpCharge
        return total_price

    # Calculate total proceeds for selling including capital gains tax
    def total_sell_proceeds(self, avg_price, share_price, quantity):
        selling_total = share_price * quantity
        buying_total = avg_price * quantity

        capital_gains_tax = 0.05 * max(selling_total - buying_total, 0)
        dpCharge = 25
        sebonFeePercent = 0.00015
        
        if selling_total <= 50000:
            brokerFeePercent = 0.0036
        elif selling_total <= 500000:
            brokerFeePercent = 0.0033
        elif selling_total <= 2000000:
            brokerFeePercent = 0.0031
        elif selling_total <= 10000000:
            brokerFeePercent = 0.0027
        else:
            brokerFeePercent = 0.0024
        
        sebonFee = selling_total * sebonFeePercent
        brokerFee = selling_total * brokerFeePercent
        total = selling_total - (sebonFee + brokerFee + capital_gains_tax + dpCharge)
        return total

    # Buy shares with confirmation and minimum 10 shares
    def buy(self, stock_row, quantity):
        # Do NOT put st.button() here
        if quantity < 10:
            st.warning("You must buy at least 10 shares.")
            return False

        total_cost = self.total_buy_cost(stock_row['Average Price'], quantity)

        if total_cost > self.money:
            st.error(f"Not enough money. Required: Rs. {total_cost:.2f}, Available: Rs. {self.money:.2f}")
            return False

        self.money -= total_cost

        # Update portfolio
        symbol = stock_row['company.name']
        if symbol in self.portfolio:
            existing = self.portfolio[symbol]
            total_quantity = existing['quantity'] + quantity
            new_avg_price = ((existing['avg_price'] * existing['quantity']) + (stock_row['Average Price'] * quantity)) / total_quantity
            self.portfolio[symbol]['quantity'] = total_quantity
            self.portfolio[symbol]['avg_price'] = new_avg_price
        else:
            self.portfolio[symbol] = {
                'quantity': quantity,
                'avg_price': stock_row['Average Price']
            }
            
        # Record transaction
        self.transactions.append({
            'type': 'buy',
            'symbol': symbol,
            'quantity': quantity,
            'price': stock_row['Average Price'],
            'total_cost': total_cost,
            'time': dt.datetime.now()
        })
        # self.update_db(symbol)
        return True  

    
    # Sell shares with confirmation and minimum 10 shares
    def sell(self, stock_obj, quantity):
        if quantity < 10:
            st.warning("You must sell at least 10 shares.")
            return False

        if stock_obj.symbol not in self.portfolio or self.portfolio[stock_obj.symbol]['quantity'] < quantity:
            st.warning("Not enough shares to sell")
            return False

        avg_price = self.portfolio[stock_obj.symbol]['avg_price']
        total_proceeds = self.total_sell_proceeds(avg_price, stock_obj.getPrice(), quantity)
        st.info(f" You will receive Rs. {total_proceeds:.2f} for selling {quantity} shares (after fees and capital gains tax)")

        if st.button(f"Confirm Sell {quantity} shares of {stock_obj.symbol}"):
            self.portfolio[stock_obj.symbol]['quantity'] -= quantity
            if self.portfolio[stock_obj.symbol]['quantity'] == 0:
                del self.portfolio[stock_obj.symbol]
            self.money += total_proceeds
            stock_obj.quantity += quantity
            self.transactions.append({
                'type':'sell',
                'symbol':stock_obj.symbol,
                'quantity':quantity,
                'price':stock_obj.getPrice(),
                'total_proceeds': total_proceeds,
                'time':dt.datetime.now()
            })
            st.success(f" Sold {quantity} shares of {stock_obj.symbol}. New balance: Rs. {self.money:.2f}")
            self.update_db(stock_obj.symbol)
            return True

    def update_db(self, symbol):
        conn = get_connection()
        cur = conn.cursor()
        # insert or update portfolio table
        cur.execute("""
            INSERT INTO public.portfolio(uid, symbol, quantity, avg_price)
            VALUES(%s,%s,%s,%s)
            ON CONFLICT(uid,symbol)
            DO UPDATE SET quantity=EXCLUDED.quantity, avg_price=EXCLUDED.avg_price
        """, (self.uid, symbol, self.portfolio[symbol]['quantity'], self.portfolio[symbol]['avg_price']))
        conn.commit()
        cur.close()
        conn.close()
