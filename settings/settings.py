import os
from dotenv import load_dotenv

load_dotenv()

BREEZE_API_KEY = os.getenv("BREEZE_API_KEY")
BREEZE_SECRET_KEY = os.getenv("BREEZE_SECRET_KEY")
API_SESSION = os.getenv("API_SESSION")