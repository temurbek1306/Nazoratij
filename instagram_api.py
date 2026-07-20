import os
import requests
import time

class InstagramAPI:
    def __init__(self, access_token: str, account_id: str):
        self.access_token = access_token
        self.account_id = account_id
        self.base_url = "https://graph.facebook.com/v19.0"

    def upload_reel(self, video_url: str, caption: str = "") -> str:
        """Videoni Instagram serveriga yuklaydi (Container yaratadi)"""
        url = f"{self.base_url}/{self.account_id}/media"
        payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "share_to_feed": "true",
            "access_token": self.access_token
        }
        print(f"[API] Video yuklanmoqda... Kuting.")
        response = requests.post(url, data=payload)
        data = response.json()
        
        if "id" not in data:
            raise Exception(f"[API] Yuklashda xatolik: {data}")
            
        container_id = data["id"]
        print(f"[API] Container ID olindi: {container_id}")
        return container_id

    def check_status(self, container_id: str) -> bool:
        """Video tayyor bo'lganini tekshiradi"""
        url = f"{self.base_url}/{container_id}"
        params = {
            "fields": "status_code",
            "access_token": self.access_token
        }
        
        # Instagram videoni qayta ishlashi uchun vaqt kerak
        max_attempts = 10
        for i in range(max_attempts):
            response = requests.get(url, params=params)
            data = response.json()
            
            status = data.get("status_code", "ERROR")
            print(f"[API] Status: {status} ({i+1}/{max_attempts})")
            
            if status == "FINISHED":
                return True
            elif status == "ERROR":
                print(f"[API] Video qayta ishlashda xato yuz berdi: {data}")
                return False
                
            time.sleep(10) # 10 soniya kutib yana tekshiramiz
            
        return False

    def publish_reel(self, container_id: str) -> bool:
        """Tayyor videoni tarmoqqa e'lon qiladi"""
        url = f"{self.base_url}/{self.account_id}/media_publish"
        payload = {
            "creation_id": container_id,
            "access_token": self.access_token
        }
        print(f"[API] Tarmoqqa e'lon qilinmoqda...")
        response = requests.post(url, data=payload)
        data = response.json()
        
        if "id" in data:
            print(f"[API] MUVAFFAQIYATLI! Reel ID: {data['id']}")
            return True
        else:
            print(f"[API] E'lon qilishda xatolik: {data}")
            return False
