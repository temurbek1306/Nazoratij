import os
import requests
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import webbrowser

CLIENT_KEY = "sbawlqefr3te9sdiz3"
CLIENT_SECRET = "np0srpSfHcYa0GKbdFzqBOIvk8dZ2tsH"
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
            self.wfile.write(b"<html><head><meta charset='utf-8'></head><body><h1>Ruxsat olindi! \u2705</h1><p>Bu oynani yopishingiz mumkin. Endi Telegram/Terminalga qarang!</p></body></html>")
        else:
            self.wfile.write(b"<html><body><h1>Xatolik</h1><p>Code topilmadi.</p></body></html>")
            
    def log_message(self, format, *args):
        pass

def main():
    print("="*50)
    print("\U0001f3b5 TikTok API OAuth2 Sandbox Avtorizatsiya skripti")
    print("="*50)
    
    auth_url = f"https://www.tiktok.com/v2/auth/authorize/?client_key={CLIENT_KEY}&response_type=code&scope=video.publish,video.upload&redirect_uri={urllib.parse.quote(REDIRECT_URI)}&state=test"
    
    print("\n\U0001f310 Brauzer ochilmoqda... Iltimos TikTok profilingizga kirib 'Authorize' (Ruxsat berish) tugmasini bosing.")
    webbrowser.open(auth_url)
    
    server = HTTPServer(('localhost', 8080), AuthHandler)
    while not auth_code:
        server.handle_request()
        
    print("\n\u2705 Code olindi! Token olinmoqda...")
    
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
        print("\U0001f389 MUVAFFAQIYATLI! TikTok Refresh Token olindi!")
        print("="*50)
        print("\nQuyidagi ma'lumotni GitHub Secrets'ga nusxalab qo'ying:\n")
        print("TIKTOK_REFRESH_TOKEN:")
        print(token_data.get("refresh_token", "") + "\n")
        print("="*50)
    else:
        print("\n\u274c Xatolik yuz berdi:")
        print(token_data)

if __name__ == "__main__":
    main()
