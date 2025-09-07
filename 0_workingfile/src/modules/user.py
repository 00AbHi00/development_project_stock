# src/modules/user.py
from modules import utils, stock
from db.connection import get_connection
import streamlit as st
import datetime as dt

class User:
    def __init__(self, uid, name, money=10000):
        self.uid = uid
        self.name = name
        self.money = money
        self.portfolio = {}  # symbol -> {'quantity', 'avg_price'}
        self.transactions = []

    def buy(self, stock_obj, quantity):
        price = stock_obj.getPrice()
        total = price * quantity
        if total > self.money:
            st.warning("Not enough money")
            return False
        if quantity > stock_obj.quantity:
            st.warning("Not enough shares in market")
            return False

        # Update portfolio
        if stock_obj.symbol in self.portfolio:
            existing = self.portfolio[stock_obj.symbol]
            avg_price = ((existing['avg_price']*existing['quantity']) + (price*quantity)) / (existing['quantity']+quantity)
            self.portfolio[stock_obj.symbol] = {'quantity': existing['quantity']+quantity, 'avg_price': avg_price}
        else:
            self.portfolio[stock_obj.symbol] = {'quantity': quantity, 'avg_price': price}

        self.money -= total
        stock_obj.quantity -= quantity
        self.transactions.append({'type':'buy','symbol':stock_obj.symbol,'quantity':quantity,'price':price,'time':dt.datetime.now()})
        self.update_db(stock_obj.symbol)
        st.success(f"Bought {quantity} shares of {stock_obj.name} at {price}")
        return True

    def sell(self, stock_obj, quantity):
        if stock_obj.symbol not in self.portfolio or self.portfolio[stock_obj.symbol]['quantity'] < quantity:
            st.warning("Not enough shares to sell")
            return False
        price = stock_obj.getPrice()
        total = price * quantity
        self.portfolio[stock_obj.symbol]['quantity'] -= quantity
        if self.portfolio[stock_obj.symbol]['quantity'] == 0:
            del self.portfolio[stock_obj.symbol]
        self.money += total
        stock_obj.quantity += quantity
        self.transactions.append({'type':'sell','symbol':stock_obj.symbol,'quantity':quantity,'price':price,'time':dt.datetime.now()})
        self.update_db(stock_obj.symbol)
        st.success(f"Sold {quantity} shares of {stock_obj.name} at {price}")
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
        """,(self.uid,symbol,self.portfolio[symbol]['quantity'],self.portfolio[symbol]['avg_price']))
        conn.commit()
        cur.close()
        conn.close()
