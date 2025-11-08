# grab user portfolio & connecting stock data
import pandas as pd
import yfinance as yf
from datetime import timedelta, date

def get_user_input():
    user_inp = input("Enter portfolio stock tickers separated by commas: ")
    invest_amt = input("Enter total invesetment amount across portfolio: ")
    user_inp = user_inp.split(", ") 
    cleaned_inp = []
    for i in user_inp:
        cleaned_inp.append(i.strip().upper())

#grab basic stock data
def grab_ticker_data(x: str, y: int):
    current_date = date.today()
    time_period = current_date - timedelta(days = y)
    x = yf.download(x, start = time_period, end = current_date)
    return x

#caluclate returns
def returns(x):
    return x['Adj Close']

# calcualte volatility
def get_volatility(x):
    y = returns(x)
    return y.pct_change().std()


# calc VaR
# calc sharpe ratio

# calc alpha

# calc sortino ratio

def main(userinputlist: list[]):
    cleaned_inp = get_user_input()

    for i in cleaned_inp:
        sixm_input_data = grab_ticker_data(i, 180)
        oney_input_data = grab_ticker_data(i, 365)
        fivey_input_data = grab_ticker_data(i, 1826)
    

    # grab returns
    sixm_returns = returns(sixm_input_data)
    oney_returns = returns(oney_input_data)
    fivey_returns = returns(fivey_input_data)

    #grab volatility
    get_volatility(sixm_input_data)
    get_volatility(oney_input_data)
    get_volatility(fivey_input_data)
