import os
from dotenv import load_dotenv
import urllib.request
import json

load_dotenv()
TOKEN = os.getenv("IG_ACCESS_TOKEN")

URL = f"https://graph.facebook.com/v20.0/me/permissions?access_token={TOKEN}"
try:
    req = urllib.request.Request(URL)
    res = urllib.request.urlopen(req)
    data = json.loads(res.read().decode('utf-8'))
    print("PERMISSIONS:", data)
except Exception as e:
    print("ERROR:", e)
