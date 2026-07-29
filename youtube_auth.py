import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

# YouTube Data API uchun to'liq (full access) ruxsat
SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

def main():
    print("="*50)
    print("🎥 YouTube API OAuth2 Avtorizatsiya skripti")
    print("="*50)
    print("\nAgar sizda allaqachon 'client_secret.json' fayli bo'lsa, uni shu papkaga tashlang.")
    print("Aks holda Client ID va Client Secret ni qo'lda kiritishingiz mumkin.\n")
    
    if os.path.exists('client_secret.json'):
        print("✅ 'client_secret.json' fayli topildi.")
        client_config_path = 'client_secret.json'
    else:
        print("❌ 'client_secret.json' topilmadi. Ma'lumotlarni qo'lda kiriting:\n")
        client_id = input("Client ID ni kiriting: ").strip()
        client_secret = input("Client Secret ni kiriting: ").strip()
        
        if not client_id or not client_secret:
            print("Xato: Client ID va Secret kiritilishi shart!")
            return
            
        client_config = {
            "installed": {
                "client_id": client_id,
                "project_id": "youtube-autoreels-bot",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": client_secret,
                "redirect_uris": ["http://localhost"]
            }
        }
        
        with open('client_secret.json', 'w') as f:
            json.dump(client_config, f)
        print("✅ 'client_secret.json' yaratildi.")
        client_config_path = 'client_secret.json'

    print("\n🌐 Brauzer ochilmoqda... Iltimos Google profilingizga kirib ruxsat bering.")
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(client_config_path, SCOPES)
        # Barcha brauzerlarda to'g'ri ishlashi uchun portni ko'rsatamiz
        credentials = flow.run_local_server(port=0)
        
        print("\n" + "="*50)
        print("🎉 MUVAFFAQIYATLI! Sizning API sirlaringiz tayyor.")
        print("="*50)
        print("\nQuyidagi ma'lumotlarni GitHub Secrets'ga nusxalab qo'ying:\n")
        print(f"1. YOUTUBE_CLIENT_ID:\n{credentials.client_id}\n")
        print(f"2. YOUTUBE_CLIENT_SECRET:\n{credentials.client_secret}\n")
        print(f"3. YOUTUBE_REFRESH_TOKEN:\n{credentials.refresh_token}\n")
        print("="*50)
        print("ESLATMA: Bu ma'lumotlarni hech kimga bermang!\n")
        
    except Exception as e:
        print(f"\n❌ Xatolik yuz berdi: {e}")

if __name__ == "__main__":
    main()
