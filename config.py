from dotenv import load_dotenv
import os

load_dotenv()

STOCK_API_KEY = os.getenv("API_KEY_STOCK")
CURRENCY_API_KEY = os.getenv("API_KEY_CURRENCY")