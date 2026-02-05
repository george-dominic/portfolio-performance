from main import run_snapshot
import resend
import datetime as dt
from config import RESEND_API_KEY, FROM_EMAIL, TO_EMAIL
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

    if portfolio_return > nifty_return:
        subject = f"You beat NIFTY today - {dt.date.today().strftime('%d-%m-%Y')}"
    else:
        subject = f"You lost to NIFTY today - {dt.date.today().strftime('%d-%m-%Y')}"

    email_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Portfolio Snapshot</title>
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #f8fafc; 
                padding: 20px; 
                color: #1e293b;
            }}
            @media (prefers-color-scheme: dark) {{
                body {{ background: #0f172a; color: #e2e8f0; }}
                .container {{ background: #1e293b; }}
                .stat-value {{ color: #f1f5f9; }}
                .stat-label {{ color: #94a3b8; }}
                th {{ color: #94a3b8; border-bottom-color: #334155; }}
                td {{ border-bottom-color: #334155; }}
                .section {{ border-bottom-color: #334155; }}
                .footer {{ color: #64748b; }}
            }}
            .container {{ 
                max-width: 500px; 
                margin: 0 auto; 
                background: white;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
                color: white;
                padding: 32px 24px;
                text-align: center;
            }}
            .header h1 {{ font-size: 28px; font-weight: 600; margin-bottom: 4px; }}
            .header p {{ opacity: 0.9; font-size: 14px; }}
            
            .ai-summary {{
                padding: 20px 24px;
                background: #f8fafc;
                border-bottom: 1px solid #f1f5f9;
            }}
            @media (prefers-color-scheme: dark) {{
                .ai-summary {{ background: #0f172a; border-bottom-color: #334155; }}
            }}
            .ai-summary h2 {{ font-size: 14px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }}
            .ai-summary p {{ font-size: 14px; line-height: 1.5; }}
            
            .overview {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 1px;
                background: #e2e8f0;
                border-bottom: 1px solid #e2e8f0;
            }}
            @media (prefers-color-scheme: dark) {{
                .overview {{ background: #334155; border-bottom-color: #334155; }}
            }}
            .stat {{ background: white; padding: 20px 12px; text-align: center; }}
            @media (prefers-color-scheme: dark) {{
                .stat {{ background: #1e293b; }}
            }}
            .stat-value {{ font-size: 22px; font-weight: 700; color: #1e293b; }}
            @media (prefers-color-scheme: dark) {{
                .stat-value {{ color: #f1f5f9; }}
            }}
            .stat-label {{ font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px; }}
            
            .section {{ padding: 20px 24px; border-bottom: 1px solid #f1f5f9; }}
            @media (prefers-color-scheme: dark) {{
                .section {{ border-bottom-color: #334155; }}
            }}
            .section h2 {{ font-size: 14px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; }}
            
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; padding: 8px 0; border-bottom: 2px solid #f1f5f9; }}
            @media (prefers-color-scheme: dark) {{
                th {{ border-bottom-color: #334155; }}
            }}
            td {{ padding: 10px 0; border-bottom: 1px solid #f1f5f9; font-size: 14px; }}
            @media (prefers-color-scheme: dark) {{
                td {{ border-bottom-color: #334155; }}
            }}
            tr:last-child td {{ border-bottom: none; }}
            
            .positive {{ color: #16a34a; }}
            .negative {{ color: #dc2626; }}
            
            .table-row {{ display: flex; gap: 20px; }}
            .table-row .section {{ flex: 1; padding: 16px; }}
            
            .footer {{ padding: 16px; text-align: center; color: #94a3b8; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Portfolio Snapshot</h1>
                <p>{dt.date.today().strftime('%d %B %Y')}</p>
            </div>
            
            <div class="ai-summary">
                <h2>AI Summary</h2>
                <p>Your portfolio { 'outperformed' if portfolio_return > nifty_return else 'underperformed'} NIFTY by {(portfolio_return - nifty_return)*100:.2f} basis points today.</p>
            </div>
            
            <div class="overview">
                <div class="stat">
                    <div class="stat-value {'positive' if portfolio_return >= 0 else 'negative'}">{portfolio_return:.2%}</div>
                    <div class="stat-label">Portfolio</div>
                </div>
                <div class="stat">
                    <div class="stat-value {'positive' if nifty_return >= 0 else 'negative'}">{nifty_return:.2%}</div>
                    <div class="stat-label">Nifty</div>
                </div>
                <div class="stat">
                    <div class="stat-value {'positive' if holdings["change_value"].sum() >= 0 else 'negative'}">₹{holdings["change_value"].sum():,.0f}</div>
                    <div class="stat-label">Change</div>
                </div>
            </div>
            
            <div class="table-row">
                <div class="section">
                    <h2>Top Gainers</h2>
                    <table>
                        {''.join([f'<tr><td style="text-align:left">{row["tradingsymbol"]}</td><td style="text-align:right" class="positive">{row["day_change_pct"]:.2%}</td></tr>' for _, row in top_gainers.iterrows()])}
                    </table>
                </div>
                <div class="section">
                    <h2>Top Losers</h2>
                    <table>
                        {''.join([f'<tr><td style="text-align:left">{row["tradingsymbol"]}</td><td style="text-align:right" class="negative">{row["day_change_pct"]:.2%}</td></tr>' for _, row in top_losers.iterrows()])}
                    </table>
                </div>
            </div>
            
            <div class="table-row">
                <div class="section">
                    <h2>Made Money</h2>
                    <table>
                        {''.join([f'<tr><td style="text-align:left">{row["tradingsymbol"]}</td><td style="text-align:right" class="positive">₹{row["change_value"]:,.2f}</td></tr>' for _, row in top_gainers_money.iterrows()])}
                    </table>
                </div>
                <div class="section">
                    <h2>Lost Money</h2>
                    <table>
                        {''.join([f'<tr><td style="text-align:left">{row["tradingsymbol"]}</td><td style="text-align:right" class="negative">₹{row["change_value"]:,.2f}</td></tr>' for _, row in top_losers_money.iterrows()])}
                    </table>
                </div>
            </div>
            
            <div class="table-row">
                <div class="section">
                    <h2>MTD Winners</h2>
                    <table>
                        {''.join([f'<tr><td style="text-align:left">{row["tradingsymbol"]}</td><td style="text-align:right" class="positive">{row["mtd_return"]:.2%}</td></tr>' for _, row in top_mtd_returns.iterrows()])}
                    </table>
                </div>
                <div class="section">
                    <h2>MTD Losers</h2>
                    <table>
                        {''.join([f'<tr><td style="text-align:left">{row["tradingsymbol"]}</td><td style="text-align:right" class="negative">{row["mtd_return"]:.2%}</td></tr>' for _, row in bottom_mtd_returns.iterrows()])}
                    </table>
                </div>
            </div>
            
            <div class="table-row">
                <div class="section">
                    <h2>Heavy Hitters</h2>
                    <table>
                        {''.join([f'<tr><td style="text-align:left">{row["tradingsymbol"]}</td><td style="text-align:right">{row["portfolio_contribution"]:.2%}</td></tr>' for _, row in top_contributors.iterrows()])}
                    </table>
                </div>
                <div class="section">
                    <h2>Impact Factors</h2>
                    <table>
                        {''.join([f'<tr><td style="text-align:left">{row["tradingsymbol"]}</td><td style="text-align:right">{row["impact_factor"]:.2f}x</td></tr>' for _, row in top_impact_factor.iterrows()])}
                    </table>
                </div>
            </div>
            
            <div class="section" style="border-bottom: none;">
                <h2>Top Sectors</h2>
                <table>
                    <tr><th style="text-align:left">Sector</th><th style="text-align:right">Return</th></tr>
                    {''.join([f'<tr><td style="text-align:left">{row[0]}</td><td style="text-align:right" class="{'positive' if row[1] >= 0 else 'negative'}">{row[1]:.2%}</td></tr>' for row in sector_returns.values]) if hasattr(sector_returns, 'values') else ''}
                </table>
            </div>
            
            <div class="footer">
                Generated {datetime.now().strftime('%d %b %Y')}
            </div>
        </div>
    </body>
    </html>
    """

    return email_content, subject


def run_email():
    email_content, subject = prepare_email_data()
    # Send email using Resend
    resend.api_key = RESEND_API_KEY

    try:
        resend.Emails.send(
            {
                "from": FROM_EMAIL,
                "to": TO_EMAIL,
                "subject": subject,
                "html": email_content,
            }
        )
    except Exception as e:
        print("Resend not working :",e)


if __name__ == "__main__":
    try:
        run_email()
    except Exception as e:
        print("Exception occurred:",e)
        traceback.print_exc()
