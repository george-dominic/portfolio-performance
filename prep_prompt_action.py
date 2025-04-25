from main import run_snapshot
import resend
import datetime as dt
from news import get_news
from bs4 import BeautifulSoup
from ai_summary import summarize
import traceback

def prepare_prompt_data():
    holdings, sector_returns, portfolio_return, nifty_return = run_snapshot()
    news = get_news()

    top_gainers = holdings[["tradingsymbol", "day_change_pct"]].nlargest(
        3, "day_change_pct"
    )

    top_losers = holdings[["tradingsymbol", "day_change_pct"]].nsmallest(
        3, "day_change_pct"
    )

    top_gainers_money = holdings[["tradingsymbol", "change_value"]].nlargest(
        3, "change_value"
    )
    top_losers_money = holdings[["tradingsymbol", "change_value"]].nsmallest(
        3, "change_value"
    )

    top_contributors = holdings[["tradingsymbol", "portfolio_contribution"]].nlargest(
        3, "portfolio_contribution"
    )

    top_impact_factor = holdings[["tradingsymbol", "impact_factor"]].nlargest(
        3, "impact_factor"
    )

    top_mtd_returns = holdings[["tradingsymbol", "mtd_return"]].nlargest(
        3, "mtd_return"
    )

    bottom_mtd_returns = holdings[["tradingsymbol", "mtd_return"]].nsmallest(
        3, "mtd_return"
    )

    # Format the email content
    draft_email = f"""
    <html>
    <head>
    </head>
    <body>
        <div class="container">
            <h1>📂 Portfolio Snapshot</h1>
            
            <div class="overview-box">
                <h2>🥊 Overview</h2>
                <p>Portfolio 1-Day Return: <span class="{"positive" if portfolio_return >= 0 else "negative"}">{portfolio_return:.2%}</span></p>
                <p>Nifty 1-Day Return: <span class="{"positive" if nifty_return >= 0 else "negative"}">{nifty_return:.2%}</span></p>
                <p>Total Value Change: ₹{holdings["change_value"].sum():,.2f}</p>
            </div>
            
            <div class="table-container">
                <h2>🌤️ Top Gainers</h2>
                <div class="table-wrapper">
                    {top_gainers.to_html(classes="table", float_format=lambda x: f"{x:.2%}", index=False)}
                </div>
            </div>
            
            <div class="table-container">
                <h2>⛈️ Top Losers</h2>
                <div class="table-wrapper">
                    {top_losers.to_html(classes="table", float_format=lambda x: f"{x:.2%}", index=False)}
                </div>
            </div>

            <div class="table-container">
                <h2>💰 Made me money</h2>
                <div class="table-wrapper">
                    {top_gainers_money.to_html(classes="table", float_format=lambda x: f"₹{x:.2f}", index=False)}
                </div>
            </div>
            
            <div class="table-container">
                <h2>📉 Lost me money</h2>
                <div class="table-wrapper">
                    {top_losers_money.to_html(classes="table", float_format=lambda x: f"₹{x:.2f}", index=False)}
                </div>
            </div>

            <div class="table-container">
                <h2>🙂‍↕️ Month-to-Date winners</h2>
                <div class="table-wrapper">
                    {top_mtd_returns.to_html(classes="table", float_format=lambda x: f"{x:.2%}", index=False)}
                </div>
            </div>
            
            <div class="table-container">
                <h2>🫣 Month-to-Date losers</h2>
                <div class="table-wrapper">
                    {top_mtd_returns.to_html(classes="table", float_format=lambda x: f"{x:.2%}", index=False)}
                </div>
            </div>
            
            <div class="table-container">
                <h2>💪 Heavy hitters</h2>
                <div class="table-wrapper">
                    {top_contributors.to_html(classes="table", float_format=lambda x: f"{x:.2%}", index=False)}
                </div>
            </div>
            
            <div class="table-container">
                <h2>⚡ Top Impact Factors</h2>
                <div class="table-wrapper">
                    {top_impact_factor.to_html(classes="table", float_format=lambda x: f"{x:.2f}x", index=False)}
                </div>
            </div>
            
            <div class="table-container">
                <h2>🏭 Top Sectors</h2>
                <div class="table-wrapper">
                    {sector_returns.to_html(classes="table", float_format=lambda x: f"{x:.2%}" if isinstance(x, float) else x, index=False)}
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    prompt = get_ai_prompt(draft_email,news)

    with open('prompt.txt', 'w') as f:
        f.write(prompt)

    return None

def get_ai_prompt(draft_email, news):
    soup = BeautifulSoup(draft_email, "html.parser")
    text = soup.get_text()
    text = text + "\n\nLatest News:\n" + news
    return text

if __name__ == "__main__":
    prepare_prompt_data()
