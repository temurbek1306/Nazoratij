import os
import requests
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import webbrowser

CLIENT_KEY = input("TikTok Client Key (App ID) ni kiriting: ").strip()
CLIENT_SECRET = input("TikTok Client Secret ni kiriting: ").strip()
REDIRECT_URI = "http://localhost:8080/"

auth_code = None

class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        if 'code' in params:
            auth_code = params['code'][0]
            self.wfile.write(b"<html><body><h1>Ruxsat olindi!</h1><p>Bu oynani yopib, terminalga qaytishingiz mumkin.</p></body></html>")
        else:
            self.wfile.write(b"<html><body><h1>Xatolik</h1><p>Code topilmadi.</p></body></html>")

def main():
    print("="*50)
    print("🎵 TikTok API OAuth2 Avtorizatsiya skripti")
    print("="*50)
    
    auth_url = f"https://www.tiktok.com/v2/auth/authorize/?client_key={CLIENT_KEY}&response_type=code&scope=video.publish,video.upload&redirect_uri={urllib.parse.quote(REDIRECT_URI)}&state=test"
    
    print("\n🌐 Brauzer ochilmoqda... Iltimos TikTok profilingizga kirib ruxsat bering.")
    webbrowser.open(auth_url)
    
    server = HTTPServer(('localhost', 8080), AuthHandler)
    while not auth_code:
        server.handle_request()
        
    print("\n✅ Code olindi! Token olinmoqda...")
    
    token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache"
    }
    data = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "code": auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }
    
    res = requests.post(token_url, headers=headers, data=data)
    token_data = res.json()
    
    if "access_token" in token_data:
        print("\n" + "="*50)
        print("🎉 MUVAFFAQIYATLI! Sizning API sirlaringiz tayyor.")
        print("="*50)
        print("\nQuyidagi ma'lumotlarni GitHub Secrets'ga nusxalab qo'ying:\n")
        print("1. TIKTOK_CLIENT_KEY:")
        print(CLIENT_KEY + "\n")
        print("2. TIKTOK_CLIENT_SECRET:")
        print(CLIENT_SECRET + "\n")
        print("3. TIKTOK_REFRESH_TOKEN:")
        print(token_data.get("refresh_token", "") + "\n")
        print("="*50)
    else:
        print("\n❌ Xatolik yuz berdi:")
        print(token_data)

if __name__ == "__main__":
    main()
