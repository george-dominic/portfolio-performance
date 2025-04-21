# Python 3
import http.client
import urllib.parse
import pandas as pd
import json
from config import MARKETAUX_API_KEY

def get_news():
    conn = http.client.HTTPSConnection('api.marketaux.com')

    params = urllib.parse.urlencode({
        'api_token': MARKETAUX_API_KEY,
        'symbols': '^NSEI',
        'limit': 3,
    })

    conn.request('GET', '/v1/news/all?{}'.format(params))

    res = conn.getresponse()
    data = res.read()
    data = data.decode('utf-8')

    # Parse the JSON response
    json_data = json.loads(data)

    # Check if the response contains news data
    if 'data' in json_data:
        # Create a DataFrame from the news data
        df = pd.DataFrame(json_data['data'])
        news_string = ""
        # Select and display relevant columns
        if not df.empty:
            for idx, row in df.iterrows():
                news_string += f"\n{idx + 1}. {row['title']}\n"
                news_string += f"   Description: {row['description']}\n"
                news_string += f"   Source: {row['source']}\n"
                news_string += f"   Published: {row['published_at']}\n"
        else:
            print("No news articles found.")
    else:
        print("Error in API response:", json_data.get('error', 'Unknown error'))

    return news_string
