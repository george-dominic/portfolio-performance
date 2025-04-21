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
- 📰 **MarketAux** – Market News
- 🧠 **Ollama (LLMs)** – Summarization - Llama 3.2
- 🐍 **Python** – The glue
- 📧 **Resend** – Email sender from your domain

---

## ✅ Prerequisites

1. **Zerodha Kite Developer Account**  
   - Create a KiteConnect app at [https://developers.kite.trade](https://developers.kite.trade)  
   - Use `http://localhost:8000` as your **redirect URL**  
   - Note your **API key** and **API secret**

2. **Install Ollama**  
   - download from [https://ollama.com](https://ollama.com)

3. **Download an LLM (LLaMA 3.2)**  
     ```bash
     ollama run llama3.2
     ```

4. **Your Own Domain**  
   - Create Resend account and set up your domain.

## 🚀 Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/portfolio-performance
   cd portfolio-performance
   ```
2. Install dependencies:
    ```
    pip install -r requirements.txt
    ```
3. Create your `.env` file
    ```
    KITE_API_KEY=your_kite_key
    KITE_API_SECRET=your_kite_secret
    RESEND_API_KEY=you_resend_key
    MARKETAUX_API_KEY=you_marketaux_key
    FROM_EMAIL = your_from_email
    TO_EMAIL = your_to_email
    ```
4. Run
    ```
    python prep_email.py
    ```
 
