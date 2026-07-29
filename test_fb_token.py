import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("IG_ACCESS_TOKEN")

if not token:
    print("❌ IG_ACCESS_TOKEN topilmadi.")
    exit(1)

# Debug token
url = f"https://graph.facebook.com/debug_token?input_token={token}&access_token={token}"
res = requests.get(url).json()

if 'data' in res:
    data = res['data']
    scopes = data.get('scopes', [])
    print(f"Token ruxsatlari (Scopes): {', '.join(scopes)}")
    
    needed = ['pages_manage_posts', 'publish_video']
    missing = [s for s in needed if s not in scopes]
    
    if not missing:
        print("✅ Bu token Facebook uchun ham to'liq ishlashi kerak!")
    else:
        print(f"❌ Bu tokenda yetishmayotgan ruxsatlar: {', '.join(missing)}")
else:
    print(f"❌ Token ma'lumotlarini olishda xato: {res}")
