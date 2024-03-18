from lumibot.brokers import Alpaca #Alpaca is the broker
from lumibot.backtesting import YahooDataBacktesting #YahooDataBacktesting is the framework for backtesting
from lumibot.strategies.strategy import Strategy #Strategy is the bot that performs the trading
from lumibot.traders import Trader #gives us the deployment strategy to make it live
from datetime import datetime
from alpaca_trade_api import REST #gets the news from the alpaca trade platform
from timedelta import Timedelta #makes it easier to calculate time between events
from finbert_utils import estimate_sentiment #Uses AI to calculate sentiment from the inputted data
import math
import ssl

API_KEY = "" 
API_SECRET = ""
BASE_URL = ""

ALPACA_CREDS = {
    "API_KEY": API_KEY,
    "API_SECRET": API_SECRET,
    "PAPER": True
}

#higher the number, the more cash per trade, lower the number, the less cash per trade.
#determines the amount of risk you want to work with
risk_factor = 0.5
#The trade symbol for the stock we are training and trading
trade_symbol = "SPY"

    
class MLTrader(Strategy):
    #Startup methods. Initialize runs once
    #symbol is the index we are trading on
    def initialize(self, symbol:str=trade_symbol, cash_at_risk:float=risk_factor):
        self.symbol = symbol
        #dictates how frequently trades occur
        self.sleeptime = "24h"
        self.last_trade = None
        self.cash_at_risk = cash_at_risk
        #used to access the Alpaca api
        self.api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)

    def position_sizing(self):
        cash = self.get_cash()
        stocks = self.get_position(self.symbol)
        if stocks is not None:
            stocks = stocks.quantity
        if stocks is None:
            stocks = 0
        print("\nNumber of stocks: ",stocks)
        last_price = self.get_last_price(self.symbol)
        #This formula guides how much of our cash balance we use per trade
        #cash_at_risk of 0.5 means that for each trade we're using 50% of our remaining cash balance
        quantity = math.floor(cash * self.cash_at_risk / last_price)
        return cash, last_price, quantity, stocks

    #all dates are in respect to the live training
    def get_dates(self):
        today = self.get_datetime()
        three_days_ago = today - Timedelta(days=3)
        return today.strftime('%Y-%m-%d'), three_days_ago.strftime('%Y-%m-%d')

    def get_sentiment(self):
        today, three_days_ago = self.get_dates()
        if today == '2020-03-10':
            print("That special day")
        print(today)
        news = self.api.get_news(symbol=self.symbol,
                             start=three_days_ago,
                             end=today)

        news = [article.headline for article in news]
        probability, sentiment = estimate_sentiment(news)
        return probability, sentiment

    #on_trading_iteration runs every time there is new data
    def on_trading_iteration(self):
        cash, last_price, quantity, stocks = self.position_sizing()
        probability, sentiment = self.get_sentiment()

        #if we have enough cash to fund our next action perform trade
        if cash > last_price:
            if sentiment == "positive" and probability > .999:
                if self.last_trade == "sell":
                    self.sell_all()
                order = self.create_order(
                    self.symbol,
                    #number of stocks to buy/sell at a time
                    quantity,
                    #type of order we want to perform
                    "buy",
                    #type of ordering process we want to perform e.g. market order, bracket order, limit order, etc.
                    #type="bracket",
                    take_profit_price=last_price*1.20,
                    stop_loss_price=last_price*.95
                )

                #starts and order
                self.submit_order(order)
                #changes last trade so we keep in mind what our last action was
                self.last_trade = "buy"

            if sentiment == "negative" and probability > .999 and stocks > 0:
                if self.last_trade == "buy":
                    self.sell_all()
                order = self.create_order(
                    self.symbol,
                    #number of stocks to buy/sell at a time
                    min(quantity, stocks),
                    #quantity,
                    #type of order we want to perform
                    "sell",
                    #type of ordering process we want to perform e.g. market order, bracket order, limit order, etc.
                    #type="bracket",
                    take_profit_price=last_price*.8,
                    stop_loss_price=last_price*1.05
                )

                #starts and order
                self.submit_order(order)
                #changes last trade so we keep in mind what our last action was
                self.last_trade = "sell"

#dates used for backtesting in YYYYMMDD
start_date = datetime(2020,1,1)
end_date = datetime(2023,12,31)

broker = Alpaca(ALPACA_CREDS)

strategy = MLTrader(name='mlstrat',
                    broker=broker,
                    parameters={"symbol":trade_symbol,
                                "cash_at_risk":risk_factor})

strategy.backtest(
    YahooDataBacktesting,
    start_date,
    end_date,
    parameters={"symbol":trade_symbol, "cash_at_risk":risk_factor}
)