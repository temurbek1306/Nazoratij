from video_manager import VideoManager
from instagram_api import InstagramAPI
from server import LocalVideoServer
import os
from dotenv import load_dotenv

load_dotenv()
IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
IG_ACCOUNT_ID = os.getenv("IG_ACCOUNT_ID")
NGROK_AUTHTOKEN = os.getenv("NGROK_AUTHTOKEN")

manager = VideoManager("videos")
server = None

def get_pending_video() -> str:
    """Returns the filename of the next pending video to be posted. Returns an empty string if there are no videos."""
    video = manager.get_next_video()
    return video if video else ""

def expose_video_url(filename: str) -> str:
    """Starts the local server and ngrok tunnel (or uguu.se) to expose the video file to the internet. Returns the public URL."""
    import requests
    filepath = f"videos/pending/{filename}"
    print(f"[{filename}] uguu.se orqali ochiq URL olinmoqda...")
    try:
        with open(filepath, 'rb') as f:
            files = {'files[]': f}
            res = requests.post('https://uguu.se/upload', files=files, timeout=30)
        data = res.json()
        if data.get('success') and data.get('files'):
            url = data['files'][0]['url']
            if url.startswith("http"):
                return url
    except Exception as e:
        print(f"uguu.se orqali URL olishda xatolik: {e}, ngrok'ga o'tilmoqda...")
        
    global server
    if not server:
        server = LocalVideoServer(port=8000, directory="videos/pending")
        server.start(authtoken=NGROK_AUTHTOKEN)
    
    import time
    time.sleep(2) # Server to'liq yoqilishi uchun biroz kutamiz
    
    return f"{server.public_url}/{filename}"

def post_to_instagram(video_url: str, caption: str, filename: str, is_trial: bool = False) -> str:
    """Uploads the video from video_url to Instagram Reels with the given caption. Marks the video as posted and stops the local server."""
    global server
    
    if not IG_ACCESS_TOKEN or not IG_ACCOUNT_ID:
        return False
        
    try:
        api = InstagramAPI(access_token=IG_ACCESS_TOKEN, account_id=IG_ACCOUNT_ID)
        container_id = api.upload_reel(video_url=video_url, caption=caption, is_trial=is_trial)
        
        is_ready = api.check_status(container_id)
        if is_ready:
            media_id = api.publish_reel(container_id)
            if media_id:
                # We do NOT mark as posted here because YouTube still needs the file!
                return media_id
        return None
    except Exception as e:
        print(f"[Tools] Xatolik yuz berdi: {str(e)}")
        return False
    finally:
        if server:
            server.stop()
            server = None

def post_ig_comment(media_id: str, message: str) -> bool:
    """Instagram videoga izoh qoldiradi"""
    if not IG_ACCESS_TOKEN or not IG_ACCOUNT_ID:
        return False
        
    try:
        api = InstagramAPI(access_token=IG_ACCESS_TOKEN, account_id=IG_ACCOUNT_ID)
        return api.post_comment(media_id, message)
    except Exception as e:
        print(f"[Tools] Izoh qoldirishda xatolik: {str(e)}")
        return False

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
