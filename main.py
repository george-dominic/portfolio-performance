import pandas as pd
from kiteconnect import KiteConnect
import yfinance as yf
import webbrowser
from config import KITE_API_KEY, KITE_API_SECRET
from auth_handler import setup_auth_server
from token_manager import save_token, get_token, is_token_valid
import warnings
import os
warnings.filterwarnings('ignore')



def authenticate_kite():
    # Initialize KiteConnect with API key from environment variables
    kite = KiteConnect(api_key=KITE_API_KEY)

    # Check if we have a valid token for today
    if is_token_valid():
        print("Using existing token for today...") 
        kite.set_access_token(get_token())
    else:
        print("No valid token found. Starting new authentication...")
        # Set up the authentication server
        server = setup_auth_server()

        # Get login URL and open it in browser
        login_url = kite.login_url()
        webbrowser.open(login_url)

        print("Waiting for login...")

        # Keep server running until we get the request token
        while not server.stop:
            server.handle_request()

        # Generate session using the captured request token
        try:
            data = kite.generate_session(
                server.request_token, api_secret=KITE_API_SECRET
            )
            access_token = data["access_token"]
            kite.set_access_token(access_token)
            save_token(access_token)  # Save the new token
            print("Login successful! Access token generated and saved.")
        except Exception as e:
            print(f"Login failed: {str(e)}")
    return kite


def get_portfolio():
    # Get holdings
    holdings = authenticate_kite().holdings()
    holdings = pd.DataFrame(holdings)
    holdings = holdings[
        [
            "tradingsymbol",
            "isin",
            "quantity",
            "average_price",
        ]
    ]
    holdings.to_csv('holdings.csv',index=False)
    return holdings

def get_yf_data(holdings):
    # Create empty lists to store data
    close_prices = []
    day_changes = []
    mtd_returns = []
    day_changes_pct = []
    
    # Iterate through each trading symbol
    for symbol in holdings['tradingsymbol']:
        try:
            # Add .NS for NSE stocks
            ticker = yf.Ticker(f"{symbol}.NS")
            # Get 2 days of data for day change and month-to-date data
            hist = ticker.history(period="1mo")  # Get 1 month of data
            
            if len(hist) >= 2:
                # Get close price and calculate day change
                close_price = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
                day_change = close_price - prev_close
                day_change_pct = day_change / prev_close
                
                # Calculate month-to-date return
                month_start_price = hist['Close'].iloc[0]
                mtd_return = (close_price - month_start_price) / month_start_price
                
                close_prices.append(close_price)
                day_changes.append(day_change)
                day_changes_pct.append(day_change_pct)
                mtd_returns.append(mtd_return)
            else:
                close_prices.append(None)
                day_changes.append(None)
                day_changes_pct.append(None)
                mtd_returns.append(None)
                
        except Exception as e:
            print(f"Error getting data for {symbol}: {str(e)}")
            close_prices.append(None)
            day_changes.append(None)
            mtd_returns.append(None)
            day_changes_pct.append(None)
    
    # Add the data to holdings dataframe
    holdings['close_price'] = close_prices
    holdings['day_change'] = day_changes
    holdings['mtd_return'] = mtd_returns
    holdings['day_change_pct'] = day_changes_pct
    
    return holdings




def calculate_portfolio_return(holdings):
    # Get holdings

    holdings["prev_close"] = holdings["close_price"] - holdings["day_change"]

    # Calculate 1D return %
    holdings["daily_return"] = holdings["day_change"] / holdings["prev_close"]

    # Contribution to portfolio
    holdings["prev_value"] = holdings["quantity"] * holdings["prev_close"]
    holdings["change_value"] = holdings["quantity"] * holdings["day_change"]

    total_prev_value = holdings["prev_value"].sum()
    # portfolio_return = holdings['change_value'].sum() / total_prev_value

    holdings["portfolio_contribution"] = holdings["change_value"] / total_prev_value

    # Return vs Weight Delta
    holdings["weight"] = holdings["prev_value"] / total_prev_value
    holdings["impact_factor"] = holdings["portfolio_contribution"] / holdings["weight"]

    # holdings.reset_index(inplace=True,drop=True)

    # print(holdings[['tradingsymbol', 'daily_return', 'change_value']])
    # print(holdings[['tradingsymbol', 'portfolio_contribution']].sort_values('portfolio_contribution', ascending=False))
    # print(holdings[['tradingsymbol','impact_factor']])
    # print(f"\n📦 Portfolio 1-Day Return: {portfolio_return:.2%}")

    return holdings


def get_sector_return(holdings):
    # Get sectors for each symbol
    sectors = {}
    for symbol in holdings["tradingsymbol"]:
        try:
            # Add .NS for NSE stocks
            ticker = yf.Ticker(f"{symbol}.NS")
            info = ticker.info
            sectors[symbol] = info.get("sector", "Unknown")
        except Exception as e:
            print(f"Error getting sector for {symbol}: {str(e)}")
            sectors[symbol] = "Unknown"

    # Add sectors to holdings dataframe
    holdings["sector"] = holdings["tradingsymbol"].map(sectors)

    # Group by sector and calculate sector-wise returns
    sector_returns = holdings.groupby("sector").agg(
        {"change_value": "sum", "prev_value": "sum"}
    )
    sector_returns["sector_return"] = (
        sector_returns["change_value"] / sector_returns["prev_value"]
    )
    sector_returns = sector_returns.reset_index()
    sector_returns = sector_returns.sort_values("sector_return", ascending=False)
    sector_returns = sector_returns[['sector','sector_return']]
    # print("\n📊 Sector-wise Performance:")
    # print(sector_returns[['sector_return']].sort_values('sector_return', ascending=False))

    return holdings, sector_returns




def benchmarking(holdings):
    # Nifty index comparison for the day
    nifty_ticker = yf.Ticker("^NSEI")  # Nifty index symbol
    nifty_data = nifty_ticker.history(period="1d")
    nifty_return = (nifty_data["Close"][0] - nifty_data["Open"][0]) / nifty_data[
        "Open"
    ][0]

    total_prev_value = holdings["prev_value"].sum()
    portfolio_return = holdings["change_value"].sum() / total_prev_value

    # if portfolio_return > nifty_return:
    #     print("You beat NIFTY today")
    # else:
    #     print("You lost to NIFTY today")

    # print(f"Portfolio 1D Return: {portfolio_return:.2%}")
    # print(f"Nifty 1D Return: {nifty_return:.2%}")

    return portfolio_return, nifty_return



def run_snapshot():
    if os.path.exists('holdings.csv'):
        holdings = pd.read_csv('holdings.csv')
    else:
        holdings = get_portfolio()
    holdings = get_yf_data(holdings)
    holdings = calculate_portfolio_return(holdings)
    holdings, sector_returns = get_sector_return(holdings)
    portfolio_return, nifty_return = benchmarking(holdings)

    return holdings, sector_returns, portfolio_return, nifty_return

run_snapshot()