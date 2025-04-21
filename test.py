import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date
from pandas.tseries.offsets import BDay

# Dynamic date range
end_date = date.today()
start_date = end_date - BDay(5)

# List of tickers
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

# Download historical data
data = yf.download(tickers, start=start_date, end=end_date)

# Extract Adjusted Close and Volume
adj_close = data['Close']
volume = data['Volume']

# Calculate daily returns
daily_returns = adj_close.pct_change()

# 1D volatility (latest day's return std)
volatility_1d = daily_returns.tail(1).T.squeeze()

# 5-day rolling volatility
volatility_5d = daily_returns.rolling(window=5).std()
volatility_5d_latest = volatility_5d.tail(1).T.squeeze()

# % change in volatility
volatility_change_pct = ((volatility_1d - volatility_5d_latest) / volatility_5d_latest) * 100

# 5-day average volume
avg_volume_5d = volume.rolling(window=5).mean()
latest_volume = volume.tail(1).T.squeeze()
avg_volume_latest = avg_volume_5d.tail(1).T.squeeze()

# Volume ratio
volume_ratio = ((latest_volume - avg_volume_latest) / avg_volume_latest) * 100

# Combine into DataFrame
heatmap_df = pd.DataFrame({
    'Volume Ratio': volume_ratio,
    'Volatility Change (%)': volatility_change_pct
})

# Plot
plt.figure(figsize=(10, 7))
sns.scatterplot(
    data=heatmap_df,
    x='Volume Ratio',
    y='Volatility Change (%)',
    hue=heatmap_df.index,
    s=200,
    palette='viridis'
)
plt.axhline(0, color='gray', linestyle='--')
plt.axvline(1, color='gray', linestyle='--')
plt.title('Volume Ratio vs. Volatility Change (%)')
plt.xlabel('Volume Ratio (Today / 5D Avg)')
plt.ylabel('Volatility Change (%)')
plt.grid(True)
plt.legend(title='Ticker')
plt.tight_layout()
plt.show()