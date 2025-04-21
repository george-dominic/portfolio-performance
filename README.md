# 📈 Daily Portfolio Insights

A lightweight, automated analytics pipeline to track and understand your equity portfolio (Zerodha/Kite) with performance metrics, attribution analysis, and smart summaries.

---

## 🔧 Features

- **1-Day Return**
  - Track daily return for your holdings.
- **MTD Metrics**
  - Return on MTD basis.
- **Top Gainers and Losers**
  - Stocks moving your portfolio.
- **Return contribution and Impact**
  - See which stocks are contributing most to your portfolio.
- **Sector Intelligence**
  - Sector based returns.
- **Benchmark Comparison**
  - Track daily alpha vs Nifty.
- **Email Digest**
  - Auto-generated daily report.
- **LLM-Powered Summaries**
  - Auto-summarize the entire report including latest news using locally hosted Llama 3.2 via Ollama.

---

## ⚙️ Stack

- 🪙 **Zerodha KiteConnect API** – Holdings
- 📊 **yFinance** – Prices + Sector Data
- 🧠 **Ollama (LLMs)** – Summarization - Llama 3.2
- 🐍 **Python** – The glue
- 📧 **Email Sender** – Resend

---

## 🚀 Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/portfolio-insights
   cd portfolio-insights