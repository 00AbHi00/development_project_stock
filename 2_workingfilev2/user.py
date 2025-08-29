import datetime as dt
import csv
import os
import streamlit as st
import utils 
class User:
    date= utils.get_current_date()
    def __init__(self, name):
        self.name = name  # Instance attribute
        self.__portfolio={}
        self.__money= 10000
    
    def get_portfolio(self):
        return self.__portfolio
        
    def sell(self, stock, quantity):
        symbol = stock.symbol
        if symbol not in self.__portfolio or self.__portfolio[symbol]['quantity'] < quantity:
            print(f"You don't own enough shares of {symbol} to sell.")
            return

        # Sell at current stock price
        sell_price = stock.getPrice()
        total_sale = sell_price * quantity

        # Update portfolio
        self.__portfolio[symbol]['quantity'] -= quantity
        if self.__portfolio[symbol]['quantity'] == 0:
            del self.__portfolio[symbol]

        # Add money from sale
        self.__money += total_sale
        stock.quantity += quantity  # Add back to market

        # Record transaction
        self.__history.append({
            'type': 'sell',
            'symbol': symbol,
            'quantity': quantity,
            'price': sell_price,
            'time': dt.datetime.now()
        })

        
        print(f"Sold {quantity} of {symbol} at {sell_price} each.")
    
    
    def buy(self, stock, quantity):
        if int(quantity) > int(stock.quantity):
            print('There is no enough shares in the market')
            return 0

        total_cost = quantity * stock.getPrice()
        if total_cost > self.__money:
            print(f'Required Price= {total_cost}')
            print('You dont have enough money')
            return 0

        try:
            symbol = stock.symbol
            if symbol in self.__portfolio:
                existing = self.__portfolio[symbol]
                total_quantity = existing['quantity'] + quantity
                new_avg_price = ((existing['avg_price'] * existing['quantity']) + (stock.getPrice() * quantity)) / total_quantity
                self.__portfolio[symbol]['quantity'] = total_quantity
                self.__portfolio[symbol]['avg_price'] = new_avg_price
            else:
                self.__portfolio[symbol] = {
                    'quantity': quantity,
                    'avg_price': stock.getPrice()
                }

            # Deduct money and reduce stock quantity accordingly
            self.__money -= total_cost
            stock.quantity -= quantity

            print(f"Bought {quantity} of {symbol} at {stock.getPrice()} each.")

        except Exception as e:
            print('An error occured:', e)
            return 0
  
        
    
    def getinfo(self):
        c1= st.container(border=True)
        with c1:
            st.write(f'Name: {self.name}')
            st.write(f'Total money in account: {self.__money}')
            if(len(self.__portfolio)==0):
               st.write('Portfolio is empty') 
            else:
                st.write("Portfolio:")
                st.write(self.__portfolio)


        
        
    def get_history(self):
        for txn in self.__history:
            time_str = txn['time'].strftime("%Y-%m-%d %H:%M:%S")
            print(f"{txn['type'].upper()}: {txn['quantity']} of {txn['symbol']} at {txn['price']} on {time_str}")
        
    # def applyForIPO(self,stock, quantity):
    #     blockedAmount=quantity*100
    #     print(f'Waiting for IPO results, Rs. {blockedAmount} is blocked')


    # Calculate the total fees
    
    # 1. Broker Comission
    # Up to Rs. 50,000	0.36% (0.0036)
    # Rs. 50,001 – Rs. 5,00,000	0.33% (0.0033)
    # Rs. 5,00,001 – Rs. 20,00,000	0.31% (0.0031)
    # Rs. 20,00,001 – Rs. 1,00,00,000	0.27% (0.0027)
    # Above Rs. 1,00,00,000	0.24% (0.0024)
    
    # 2. SEBON Fee 0.015% (0.00015)
    
    # 3. DP Charge: Rs. 25 (flat)
    def totalCostBuy(share_price, number_of_shares):
        calculated_total= share_price * number_of_shares

        # Initialization
        dpCharge=25        
        sebonFeePercent=0.00015
        
        if(calculated_total<=50000):
            brokerFeePercent=0.0036
        elif(calculated_total>50000 and calculated_total<=500000):
            brokerFeePercent=0.0033
        elif(calculated_total>500000 and calculated_total<=2000000):
            brokerFeePercent=0.0031
        elif(calculated_total>2000000 and calculated_total<=10000000):
            brokerFeePercent=0.0027
        else:
            brokerFeePercent=0.0024    

        sebonFee= calculated_total * sebonFeePercent
        brokerFee= calculated_total * brokerFeePercent

        total_price=calculated_total + sebonFee+brokerFee+dpCharge
        
        # Calculate the percentage based on calulated percentage
    
    
    #same principle here as well, but if there is capital gain then capital gains tax is applied which is 5%
    
    def totalSellCost(weightedAvgOfPrice, share_price, number_of_shares):
        
        calculated_selling_total= share_price * number_of_shares
        calculated_buying_total= weightedAvgOfPrice * number_of_shares
        
        #capital gains only if profit 
        if (calculated_selling_total > calculated_buying_total):
            capital_gains_tax= 0.05 
        else:
            capital_gains_tax=0
        # capital_gains_tax= 0.05 if calculated_selling_total > calculated_buying_total else 0
                
        dpCharge=25        
        sebonFeePercent=0.00015
        if(calculated_selling_total<=50000):
            brokerFeePercent=0.0036
        elif(calculated_selling_total>50000 and calculated_selling_total<=500000):
            brokerFeePercent=0.0033
        elif(calculated_selling_total>500000 and calculated_selling_total<=2000000):
            brokerFeePercent=0.0031
        elif(calculated_selling_total>2000000 and calculated_selling_total<=10000000):
            brokerFeePercent=0.0027
        elif(calculated_selling_total> 10000000):
            brokerFeePercent=0.0024    

        sebonFee= calculated_selling_total * sebonFeePercent
        brokerFee= calculated_selling_total * brokerFeePercent
        profit_tax= capital_gains_tax * (calculated_selling_total - calculated_buying_total)

        total = calculated_selling_total - (sebonFee + brokerFee + profit_tax + dpCharge)
