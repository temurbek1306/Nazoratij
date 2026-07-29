import requests

app_id = "1547281183512475"
app_secret = "6ad3692a1f84c8cd4a1a2d038a0d6fac"
short_token = "EAAVZCPnlPl5sBSEh6hIkjB9KnAgvcQK3qWRImBStIHelIB3lgqyfQZBWZALP0kzPOjsYONBdzQkh4ZAXkirzKwZB6PamZCaAPS67RxzdjJBFIpDnY4oQOMqpCdCj96mZBVIP8KMxaBDZAfZBht3etXfCfc9aZBKUOVK6juC4IKpLAuWWa1q5R7ua9Tdrm0pn10wSrDNuh1u0JgzZB1sBihNt3lZBCDtGEtT1JhklJZAEGehgZD"

print("⏳ Tokenni umrbod qilish jarayoni boshlandi...\n")

url_long_lived = f"https://graph.facebook.com/v19.0/oauth/access_token?grant_type=fb_exchange_token&client_id={app_id}&client_secret={app_secret}&fb_exchange_token={short_token}"
res1 = requests.get(url_long_lived).json()

if "access_token" not in res1:
    print("❌ Xatolik yuz berdi (1-bosqich):")
    print(res1)
else:
    long_lived_user_token = res1["access_token"]
    url_page = f"https://graph.facebook.com/v19.0/me/accounts?access_token={long_lived_user_token}"
    res2 = requests.get(url_page).json()
    
    if "data" not in res2 or len(res2["data"]) == 0:
        print("❌ Xatolik yuz berdi (2-bosqich - Sahifalar topilmadi):")
        print(res2)
    else:
        print("✅ MUVAFFAQIYATLI! Mana sizning HECH QACHON O'CHMAYDIGAN (Umrbod) tokeningiz:\n")
        print("="*60)
        print(res2["data"][0]["access_token"])
        print("="*60)
