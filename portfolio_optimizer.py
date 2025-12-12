import pandas as pd
import yfinance as yf
from datetime import timedelta, date

def get_user_input():
    user_inp = input("Enter portfolio stock tickers separated by commas: ")
    # split stock tickers
    user_inp = [t.strip().upper() for t in user_inp.split(",")]

    return user_inp

# grab basic stock data
def grab_ticker_data(ticker, days):
    print("Downloading:", ticker)

    df = yf.download(
        tickers=ticker,
        period=f"{days}d",
        auto_adjust=False,
        progress=False
    )

    # if multi-index (two-level columns), flatten it
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]

    return df



# calculate returns
def returns(x, days_range: int):
    data = grab_ticker_data(x, days_range)

    # If data is empty or missing Adj Close → return None
    if data.empty or "Adj Close" not in data.columns:
        print(f"WARNING: No price data found for {x}")
        return None

    start_close = data["Adj Close"].iloc[0]
    end_close = data["Adj Close"].iloc[-1]
    return (end_close - start_close) / start_close


# calculate volatility (daily std)
def get_volatility(ticker, days):
    df = grab_ticker_data(ticker, days)

    if df.empty or "Adj Close" not in df.columns:
        print(f"WARNING: No volatility data for {ticker}")
        return None

    daily_returns = df["Adj Close"].pct_change().dropna()
    return daily_returns.std()


# correct Sharpe ratio
def get_sharpe(ticker, days, rf=0.02):
    df = grab_ticker_data(ticker, days)

    if df.empty or "Adj Close" not in df.columns:
        print(f"WARNING: No Sharpe data for {ticker}")
        return None

    daily_returns = df["Adj Close"].pct_change().dropna()

    avg_daily = daily_returns.mean()
    vol = daily_returns.std()
    if vol == 0:
        return None

    return (avg_daily - rf/365) / vol


def analyze_portfolio(tickers):
    ranges = {
        "6m": 180,
        "1y": 365,
        "5y": 1825
    }

    results = []

    for t in tickers:
        stock_row = {"Ticker": t}
        for label, days in ranges.items():
            stock_row[f"Return {label}"] = returns(t, days)
            stock_row[f"Volatility {label}"] = get_volatility(t, days)
            stock_row[f"Sharpe {label}"] = get_sharpe(t, days)
        results.append(stock_row)

    return pd.DataFrame(results)

def allocation(df, investment, horizon="1y", vol_cap_factor=2.0):
    sharpe_col = f"Sharpe {horizon}"
    vol_col = f"Volatility {horizon}"

    data = df.copy()
    data["Sharpe_Positive"] = data[sharpe_col].apply(lambda x: max(x, 0))

    if data["Sharpe_Positive"].sum() == 0:
        data["Weight"] = 1 / len(data)
    else:
        # normalize Sharpe values into weights
        total_sharpe = data["Sharpe_Positive"].sum()
        data["Weight"] = data["Sharpe_Positive"] / total_sharpe

    avg_vol = data[vol_col].mean()
    for i in data.index:
        vol = data.loc[i, vol_col]
        if vol > vol_cap_factor * avg_vol:
            data.loc[i, "Weight"] = min(data.loc[i, "Weight"], 0.15)

    weight_sum = data["Weight"].sum()
    data["Weight"] = data["Weight"] / weight_sum

    data["Allocation ($)"] = data["Weight"] * investment

    return data[["Ticker", sharpe_col, vol_col, "Weight", "Allocation ($)"]]


def main():
    tickers = get_user_input()
    invest_amt = float(input("Enter investment amount: "))

    df = analyze_portfolio(tickers)
    print("\n===== Portfolio Analysis =====\n")
    print(df.round(4))

    # Compute and print portfolio allocation
    spread = allocation(df, invest_amt, horizon="1y")
    print("\n===== Optimized Allocation (1-Year Sharpe) =====\n")
    print(spread.round(4))

main()

