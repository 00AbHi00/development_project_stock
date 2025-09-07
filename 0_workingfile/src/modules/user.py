# src/modules/user.py
import os
import json
import datetime as dt
import streamlit as st

USERFILES_DIR = "userfiles"

class User:
    def __init__(self, uid, name, money=100000):
        self.uid = uid
        self.username = name  # store username
        self.filepath = os.path.join(USERFILES_DIR, f"user_{uid}.json")

        # Load existing user data if file exists
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                data = json.load(f)
                self.username = data.get("username", name)
                self.money = data.get("money", money)
                self.portfolio = data.get("portfolio", {})
                self.transactions = data.get("transactions", [])
        else:
            self.money = money
            self.portfolio = {}
            self.transactions = []
            self.save_user_data()  # create file for first time

    def save_user_data(self):
        os.makedirs(USERFILES_DIR, exist_ok=True)
        data = {
            "uid": self.uid,
            "username": self.username,
            "money": self.money,
            "portfolio": self.portfolio,
            "transactions": [
                {
                    "type": t["type"],
                    "symbol": t["symbol"],
                    "quantity": t["quantity"],
                    "price": t["price"],
                    "total_cost": t.get("total_cost", t.get("total_proceeds", 0)),
                    "time": t["time"] if isinstance(t["time"], str) else t["time"].isoformat()
                } for t in self.transactions
            ]
        }
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=4)

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

    # Buy shares
    def buy(self, stock_row, quantity):
        if quantity < 10:
            st.warning("You must buy at least 10 shares.")
            return False
        
        total_cost = self.total_buy_cost(stock_row['Average Price'], quantity)

        if total_cost > self.money:
            st.error(f"Not enough money. Required: Rs. {total_cost:.2f}, Available: Rs. {self.money:.2f}")
            return False

        self.money -= total_cost

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

        self.transactions.append({
            'type': 'buy',
            'symbol': symbol,
            'quantity': quantity,
            'price': stock_row['Average Price'],
            'total_cost': total_cost,
            'time': dt.datetime.now()
        })

        self.save_user_data()
        return True

    def update_json(self):
        """Persist user portfolio and money to JSON file."""
        os.makedirs(USERFILES_DIR, exist_ok=True)
        with open(os.path.join(USERFILES_DIR, f"user_{self.uid}.json"), "w") as f:
            json.dump({
                "username": self.username,
                "portfolio": self.portfolio,
                "money": self.money
            }, f, indent=4)
            
    # Sell shares
    def sell(self, stock_obj, quantity):
        if quantity < 10:
            st.warning("You must sell at least 10 shares.")
            return False

        symbol = stock_obj.symbol
        if symbol not in self.portfolio or self.portfolio[symbol]['quantity'] < quantity:
            st.warning("Not enough shares to sell")
            return False

        avg_price = self.portfolio[symbol]['avg_price']
        total_proceeds = self.total_sell_proceeds(avg_price, stock_obj.getPrice(), quantity)

        self.portfolio[symbol]['quantity'] -= quantity
        if self.portfolio[symbol]['quantity'] == 0:
            del self.portfolio[symbol]

        self.money += total_proceeds
        stock_obj.quantity += quantity

        self.transactions.append({
            'type': 'sell',
            'symbol': symbol,
            'quantity': quantity,
            'price': stock_obj.getPrice(),
            'total_proceeds': total_proceeds,
            'time': dt.datetime.now()
        })

        self.save_user_data()
        st.success(f"Sold {quantity} shares of {symbol}. New balance: Rs. {self.money:.2f}")
        return True
