import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("INDSTOCKS_API_TOKEN")

headers = {
    "Authorization": token
}

url = "https://api.indstocks.com/market/quotes/full"

params = {
    "scrip-codes": "NFO_44616"
}

response = requests.get(
    url,
    headers=headers,
    params=params
)

print("Status:", response.status_code)
print(response.text)