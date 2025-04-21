from main import run_snapshot
import resend
import datetime as dt
from config import RESEND_API_KEY
from news import get_news
from bs4 import BeautifulSoup
from ai_summary import summarize
import traceback


def prepare_email_data():
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
            
            <div class="summary-box">
                <h2>Portfolio Summary</h2>
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

    if portfolio_return > nifty_return:
        subject = f"💃 You beat NIFTY today - {dt.date.today().strftime('%d-%m-%Y')}"
    else:
        subject = f"🥲 You lost to NIFTY today - {dt.date.today().strftime('%d-%m-%Y')}"

    summary = get_ai_summary(draft_email, news)
    summary = summary.strip('"')
    # print(summary)
    # print("Done")

    email_content = f"""
    <html>
        <head>
            <style>
                @media (prefers-color-scheme: dark) {{
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #1a1a1a;
                        color: #e0e0e0;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 800px;
                        margin: 0 auto;
                        background-color: #2d2d2d;
                        padding: 20px;
                        border-radius: 10px;
                    }}
                    h1, h2, h3 {{
                        color: #ffffff;
                    }}
                    .summary-box {{
                        background-color: #3d3d3d;
                        padding: 15px;
                        border-radius: 5px;
                        margin-bottom: 20px;
                    }}
                    .table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-bottom: 20px;
                        color: #e0e0e0;
                    }}
                    .table th, .table td {{
                        padding: 10px;
                        text-align: left;
                        border-bottom: 1px solid #444;
                    }}
                    .table th {{
                        background-color: #1a1a1a;
                        color: #ffffff;
                    }}
                    .table tr:nth-child(even) {{
                        background-color: #333;
                    }}
                    .table tr:hover {{
                        background-color: #444;
                    }}
                    .positive {{
                        color: #4CAF50;
                    }}
                    .negative {{
                        color: #f44336;
                    }}
                }}

                @media (prefers-color-scheme: light) {{
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f5f5f5;
                        color: #333333;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 800px;
                        margin: 0 auto;
                        background-color: #ffffff;
                        padding: 20px;
                        border-radius: 10px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    h1, h2, h3 {{
                        color: #222222;
                    }}
                    .summary-box {{
                        background-color: #f8f9fa;
                        padding: 15px;
                        border-radius: 5px;
                        margin-bottom: 20px;
                        border: 1px solid #e0e0e0;
                    }}
                    .table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-bottom: 20px;
                        color: #333333;
                    }}
                    .table th, .table td {{
                        padding: 10px;
                        text-align: left;
                        border-bottom: 1px solid #e0e0e0;
                    }}
                    .table th {{
                        background-color: #f8f9fa;
                        color: #333333;
                    }}
                    .table tr:nth-child(even) {{
                        background-color: #f8f9fa;
                    }}
                    .table tr:hover {{
                        background-color: #f0f0f0;
                    }}
                    .positive {{
                        color: #2e7d32;
                    }}
                    .negative {{
                        color: #c62828;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📂 Portfolio Snapshot</h1>
                <hr>
                <div class="ai-summary-box">
                    <h2>✨ AI summary</h2>
                    <p>{summary}</p>
                </div>
                <div class="overview-box">
                    <h2>🥊 Overview</h2>
                    <p>Portfolio 1-Day Return: <span class="{"positive" if portfolio_return >= 0 else "negative"}">{portfolio_return:.2%}</span></p>
                    <p>Nifty 1-Day Return: <span class="{"positive" if nifty_return >= 0 else "negative"}">{nifty_return:.2%}</span></p>
                    <p>Total Value Change: ₹{holdings["change_value"].sum():,.2f}</p>
                </div>
                
                <div style="display: flex; gap: 20px;">
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
                </div>

                <div style="display: flex; gap: 20px;">
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
                </div>

                <div style="display: flex; gap: 20px;">   
                    <div class="table-container">
                        <h2>🙂‍↕️ Month-to-Date winners</h2>
                        <div class="table-wrapper">
                            {top_mtd_returns.to_html(classes="table", float_format=lambda x: f"{x:.2%}", index=False)}
                        </div>
                    </div>
                    
                    <div class="table-container">
                        <h2>🫣 Month-to-Date losers</h2>
                        <div class="table-wrapper">
                            {bottom_mtd_returns.to_html(classes="table", float_format=lambda x: f"{x:.2%}", index=False)}
                        </div>
                    </div>
                </div>    

                <div style="display: flex; gap: 20px;">    
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

    return email_content, subject


def get_ai_summary(draft_email, news):
    soup = BeautifulSoup(draft_email, "html.parser")
    text = soup.get_text()
    text = text + "\n\nLatest News:\n" + news
    return summarize(text)


def run_email():
    email_content, subject = prepare_email_data()
    # Send email using Resend
    resend.api_key = RESEND_API_KEY

    resend.Emails.send(
        {
            "from": "portfolio@georgedominic.com",
            "to": "georgedominicv@gmail.com",
            "subject": subject,
            "html": email_content,
        }
    )


if __name__ == "__main__":
    try:
        run_email()
    except Exception as e:
        print("Exception occurred:",e)
        traceback.print_exc()