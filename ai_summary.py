import ollama


def summarize(text):
    client = ollama.Client()

    model = "llama3.2"

    prompt = f"""Analyze this portfolio snapshot and provide a concise summary highlighting key points:
    {text}
    
    Focus on:
    1. Highlight and summarise notable news
    2. Overall portfolio performance vs NIFTY
    3. Key contributors to gains/losses
    4. Notable sector performance
    5. Any significant impact factors
    
    Keep the summary under 120 words and maintain a casual, witty tone. Just respond with summary and nothing else"""

    response = client.chat(model=model, messages=[{"role": "user", "content": prompt}])

    return response["message"]["content"]
