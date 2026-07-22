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
    """Starts the local server and ngrok tunnel to expose the video file to the internet. Returns the public URL."""
    global server
    if not server:
        server = LocalVideoServer(port=8000, directory="videos/pending")
        server.start(authtoken=NGROK_AUTHTOKEN)
    
    import time
    time.sleep(2) # Server to'liq yoqilishi uchun biroz kutamiz
    
    return f"{server.public_url}/{filename}"

def post_to_instagram(video_url: str, caption: str, filename: str) -> bool:
    """Uploads the video from video_url to Instagram Reels with the given caption. Marks the video as posted and stops the local server."""
    global server
    
    if not IG_ACCESS_TOKEN or not IG_ACCOUNT_ID:
        return False
        
    try:
        api = InstagramAPI(access_token=IG_ACCESS_TOKEN, account_id=IG_ACCOUNT_ID)
        container_id = api.upload_reel(video_url=video_url, caption=caption)
        
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
