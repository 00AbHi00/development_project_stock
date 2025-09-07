# src/modules/stock.py
import pandas as pd
from modules import utils

class Stock:
    def __init__(self, name, symbol, category):
        self.name = name
        self.symbol = symbol
        self.category = category
        self.quantity = 0
        self.history = utils.load_csv("final_clean_data.csv")
    
    def getPrice(self):
        today = utils.get_current_date()
        df = self.history
        df['date'] = pd.to_datetime(df['date']).dt.date
        today_data = df[df['date'] == today]
        row = today_data[today_data['company.name'] == self.name]
        if not row.empty:
            return row.iloc[0]['price.close']
        return 0

    def get_OHLC(self):
        df = self.history[self.history['company.name'] == self.name]
        df['date'] = pd.to_datetime(df['date'])
        return df[['date', 'price.max', 'price.min', 'price.close', 'price.prevClose']]
    @staticmethod
    def load_all_stocks():
        df = utils.load_csv("final_clean_data.csv")
        return df

    @staticmethod
    def get_stock_by_name(name):
        df = utils.load_csv("final_clean_data.csv")
        row = df[df["company.name"]==name].iloc[0]
        return row
    
    def filter_stocks(df, name=None, category=None):
        filtered = df
        if name:
            filtered = filtered[filtered['company.name'].str.contains(name, case=False)]
        if category:
            filtered = filtered[filtered['company.cat'].str.lower() == category.lower()]
        return filtered