import os
import requests
import time

class TikTokAPI:
    def __init__(self, client_key, client_secret, refresh_token):
        self.client_key = client_key
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = None
        self.open_id = None
        self._refresh_access_token()

    def _refresh_access_token(self):
        url = "https://open.tiktokapis.com/v2/oauth/token/"
        headers = {"Content-Type": "application/x-www-form-urlencoded", "Cache-Control": "no-cache"}
        data = {
            "client_key": self.client_key,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        res = requests.post(url, headers=headers, data=data).json()
        if "access_token" in res:
            self.access_token = res["access_token"]
            self.open_id = res["open_id"]
        else:
            raise Exception(f"TikTok tokenni yangilashda xato: {res}")

    def upload_video(self, video_path: str, caption: str) -> bool:
        if not self.access_token:
            return False

        print(f"🎵 TikTok'ga yuklash boshlanmoqda: {video_path}")
        
        file_size = os.path.getsize(video_path)
        
        # 1. Init Upload
        init_url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json; charset=UTF-8"
        }
        payload = {
            "post_info": {
                "title": caption[:150], # TikTok title limit
                "privacy_level": "PUBLIC_TO_EVERYONE",
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": file_size,
                "chunk_size": file_size,
                "total_chunk_count": 1
            }
        }
        
        init_res = requests.post(init_url, headers=headers, json=payload).json()
        
        if "data" not in init_res or "upload_url" not in init_res["data"]:
            print(f"❌ TikTok Init xatolik: {init_res}")
            return False
            
        upload_url = init_res["data"]["upload_url"]
        publish_id = init_res["data"]["publish_id"]
        
        # 2. Upload Bytes
        print("Yuklanmoqda...")
        with open(video_path, "rb") as f:
            video_data = f.read()
            
        headers_upload = {
            "Content-Range": f"bytes 0-{file_size-1}/{file_size}",
            "Content-Type": "video/mp4"
        }
        
        upload_res = requests.put(upload_url, headers=headers_upload, data=video_data)
        
        if upload_res.status_code not in [200, 201]:
            print(f"❌ TikTok Fayl yuklashda xatolik: {upload_res.status_code} - {upload_res.text}")
            return False
            
        print("✅ TikTok'ga muvaffaqiyatli jo'natildi! (Video tez orada akkauntingizda chiqadi)")
        return True
