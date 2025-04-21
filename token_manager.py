import os
import json
from datetime import datetime
import pytz

TOKEN_FILE = 'token_data.json'

def save_token(access_token):
    """Save the access token with current timestamp"""
    token_data = {
        'access_token': access_token,
        'timestamp': datetime.now(pytz.timezone('Asia/Kolkata')).isoformat()
    }
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f)

def get_token():
    """Get the stored token if it's still valid for the day"""
    if not os.path.exists(TOKEN_FILE):
        return None

    try:
        with open(TOKEN_FILE, 'r') as f:
            token_data = json.load(f)
        
        # Parse the stored timestamp
        stored_time = datetime.fromisoformat(token_data['timestamp'])
        current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
        
        # Check if the token is from today
        if stored_time.date() == current_time.date():
            return token_data['access_token']
        return None
    
    except (json.JSONDecodeError, KeyError, ValueError):
        return None

def is_token_valid():
    """Check if we have a valid token for today"""
    return get_token() is not None 