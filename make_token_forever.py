import requests

def extend_token(app_id, app_secret, short_token):
    print("⏳ Tokenni umrbod qilish jarayoni boshlandi...\n")
    
    # 1. Short-lived User Token ni Long-Lived User Token ga almashtirish (60 kunlik)
    url_long_lived = f"https://graph.facebook.com/v19.0/oauth/access_token?grant_type=fb_exchange_token&client_id={app_id}&client_secret={app_secret}&fb_exchange_token={short_token}"
    res1 = requests.get(url_long_lived).json()
    
    if "access_token" not in res1:
        print("❌ Xatolik yuz berdi (1-bosqich):")
        print(res1)
        return
        
    long_lived_user_token = res1["access_token"]
    
    # 2. Long-Lived User Token orqali Never-Expiring Page Token (Umrbod) ni olish
    url_page = f"https://graph.facebook.com/v19.0/me/accounts?access_token={long_lived_user_token}"
    res2 = requests.get(url_page).json()
    
    if "data" not in res2 or len(res2["data"]) == 0:
        print("❌ Xatolik yuz berdi (2-bosqich - Sahifalar topilmadi):")
        print(res2)
        return
        
    print("✅ MUVAFFAQIYATLI! Mana sizning HECH QACHON O'CHMAYDIGAN (Umrbod) tokeningiz:\n")
    print("="*60)
    # Birinchi sahifaning tokenini olamiz (odatda bitta bo'ladi)
    print(res2["data"][0]["access_token"])
    print("="*60)
    print("\nShu uzun tokenni nusxalab, Githubdagi IG_ACCESS_TOKEN va FB_PAGE_ACCESS_TOKEN sirlarining ichiga joylasangiz umrbod qutulasiz!")

if __name__ == "__main__":
    APP_ID = input("App ID ni kiriting: ").strip()
    APP_SECRET = input("App Secret ni kiriting: ").strip()
    SHORT_TOKEN = input("Hozirgina olingan Tokenni kiriting: ").strip()
    
    if APP_ID and APP_SECRET and SHORT_TOKEN:
        extend_token(APP_ID, APP_SECRET, SHORT_TOKEN)
    else:
        print("Barcha ma'lumotlarni kiritish shart!")
