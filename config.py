import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
KITE_API_KEY = os.getenv('KITE_API_KEY')
KITE_API_SECRET = os.getenv('KITE_API_SECRET')
RESEND_API_KEY = os.getenv('RESEND_API_KEY')
MARKETAUX_API_KEY = os.getenv('MARKETAUX_API_KEY')
FROM_EMAIL = os.getenv('FROM_EMAIL')
TO_EMAIL = os.getenv('TO_EMAIL')