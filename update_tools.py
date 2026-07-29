import os

def insert_telegram_function(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    telegram_code = """
def post_to_telegram(video_path: str, caption: str) -> bool:
    import requests
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    tg_channel = os.getenv("TELEGRAM_CHANNEL_ID")
    
    if not tg_token or not tg_channel:
        print("[Tools] Telegram token yoki kanal ID si yo'q.")
        return False
        
    try:
        url = f"https://api.telegram.org/bot{tg_token}/sendVideo"
        with open(video_path, 'rb') as video:
            files = {'video': video}
            data = {'chat_id': tg_channel, 'caption': caption[:1024]}
            res = requests.post(url, files=files, data=data)
            if res.status_code == 200:
                print("✅ Telegram kanalga muvaffaqiyatli joylandi!")
                return True
            else:
                print(f"[Tools] Telegram Xatosi: {res.text}")
                return False
    except Exception as e:
        print(f"[Tools] Telegramga joylashda xatolik: {e}")
        return False
"""
    if "def post_to_telegram" not in content:
        content += telegram_code
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Function added.")
    else:
        print("Function already exists.")

insert_telegram_function("agent_tools.py")
