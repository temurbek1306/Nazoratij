import requests
import json

def refresh_instagram_token(old_token: str):
    print("⏳ Instagram tokenini yangilash jarayoni boshlandi...")
    url = f"https://graph.facebook.com/v19.0/refresh_access_token"
    params = {
        "grant_type": "ig_refresh_token",
        "access_token": old_token
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if "access_token" in data:
        print("\n✅ MUVAFFAQIYATLI! Yangi 60 kunlik tokeningiz:\n")
        print("="*50)
        print(data["access_token"])
        print("="*50)
        print("\nShu tokenni nusxalab, GitHub Secrets dagi IG_ACCESS_TOKEN o'rniga joylang.")
    else:
        print("\n❌ Xatolik yuz berdi:")
        print(json.dumps(data, indent=2))

if __name__ == "__main__":
    # SHU YERGA HOZIRGI ESKI TOKENINGIZNI YOZASIZ (Qo'shtirnoq ichiga)
    ESKI_TOKEN = "ESKI_TOKEN_SHU_YERGA_YOZILADI"
    
    if ESKI_TOKEN == "ESKI_TOKEN_SHU_YERGA_YOZILADI":
        print("Iltimos, avval kod ichiga eski tokeningizni kiriting!")
    else:
        refresh_instagram_token(ESKI_TOKEN)
