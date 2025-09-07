# src/modules/stock.py
import pandas as pd
from modules import utils

class Stock:
    def __init__(self, name, symbol=None, category=None):
        self.name = name
        self.symbol = symbol
        self.category = category
        self.quantity = 0

    @staticmethod
    def load_current_stocks():
        """
        Load today's stocks with category info merged from company info.
        """
        # Load daily stock data (date column required)
        df_stocks = utils.load_csv("final_clean_data.csv", filter_date=True)

        # Load company info (no date column)
        df_comp = utils.load_csv("final_comp_info.csv", filter_date=False)

        # Merge to get category
        df_merged = df_stocks.merge(
            df_comp[['Name', 'Category']],
            left_on='company.name',
            right_on='Name',
            how='left'
        )

        # Only keep stocks of the current date
        current_date = utils.get_current_date()
        df_merged['date'] = pd.to_datetime(df_merged['date'])
        df_today = df_merged[df_merged['date'].dt.date == current_date]

        return df_today

    @staticmethod
    def get_stock_by_name(name):
        df = Stock.load_current_stocks()
        row = df[df["company.name"] == name]
        if not row.empty:
            return row.iloc[0]
        return None

    @staticmethod
    def filter_stocks(df, name=None, category=None):
        """
        Filter DataFrame by stock name or category
        """
        filtered = df
        if name:
            filtered = filtered[filtered['company.name'].str.contains(name, case=False)]
        if category and category.lower() != "all":
            filtered = filtered[filtered['Category'].str.lower() == category.lower()]
        return filtered

    @staticmethod
    def get_OHLC(stock_name):
        """
        Return past OHLC data for a given stock.
        """
        # Load entire stock history (all dates)
        df_stocks = utils.load_csv("final_clean_data.csv", filter_date=False)

        # Filter for the stock
        df_stock = df_stocks[df_stocks['company.name'] == stock_name].copy()
        if df_stock.empty:
            return pd.DataFrame()

        # Ensure datetime
        df_stock['date'] = pd.to_datetime(df_stock['date'])

        # Select relevant OHLC columns
        df_ohlc = df_stock[['date', 'price.max', 'price.min', 'price.close', 'price.prevClose']].sort_values('date')

        return df_ohlc
