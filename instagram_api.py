import os
import json
import requests
import time

class InstagramAPI:
    def __init__(self, access_token: str, account_id: str):
        self.access_token = access_token
        self.account_id = account_id
        self.base_url = "https://graph.facebook.com/v19.0"

    def upload_reel(self, video_url: str, caption: str = "", is_trial: bool = False, graduation_strategy: str = "MANUAL") -> str:
        """Videoni Instagram serveriga yuklaydi (Container yaratadi)"""
        url = f"{self.base_url}/{self.account_id}/media"
        payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": self.access_token
        }
        
        if is_trial:
            print(f"[API] 🧪 Video TRIAL REEL (Sinov) rejimida yuklanmoqda (Faqat non-followers ko'radi)...")
            payload["trial_params"] = json.dumps({"graduation_strategy": graduation_strategy})
        else:
            payload["share_to_feed"] = "true"
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
        max_attempts = 60
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
            return data['id']  # ID ni qaytarish (oldin True qaytarardi)
        else:
            print(f"[API] E'lon qilishda xatolik: {data}")
            return None

    def post_comment(self, media_id: str, message: str) -> bool:
        """Tayyor bo'lgan videoga izoh yozish"""
        url = f"{self.base_url}/{media_id}/comments"
        payload = {
            "message": message,
            "access_token": self.access_token
        }
        print(f"[API] Izoh yozilmoqda...")
        response = requests.post(url, data=payload)
        data = response.json()
        
        if "id" in data:
            print(f"[API] Izoh Muvaffaqiyatli qoldirildi!")
            return True
        else:
            print(f"[API] Izoh yozishda xatolik: {data}")
            return False

    def get_profile_stats(self):
        """Kanal statistikasini (Followers, Media count) olib beradi"""
        url = f"{self.base_url}/{self.account_id}?fields=followers_count,media_count,name&access_token={self.access_token}"
        try:
            response = requests.get(url)
            data = response.json()
            if "followers_count" in data:
                return {
                    "followers": data.get("followers_count", 0),
                    "media": data.get("media_count", 0),
                    "name": data.get("name", "Unknown")
                }
            else:
                print(f"[API] Statistika olishda xato: {data}")
                return None
        except Exception as e:
            print(f"[API] Statistika API xatosi: {e}")
            return None

    def get_recent_media(self, limit: int = 5):
        """Oxirgi postlarni (media) olib keladi"""
        url = f"{self.base_url}/{self.account_id}/media?fields=id,caption,media_type,timestamp&limit={limit}&access_token={self.access_token}"
        try:
            response = requests.get(url)
            data = response.json()
            if "data" in data:
                return data["data"]
            return []
        except Exception as e:
            print(f"[API] Oxirgi media xatosi: {e}")
            return []

    def get_comments(self, media_id: str):
        """Berilgan postning barcha izohlarini olib keladi"""
        url = f"{self.base_url}/{media_id}/comments?fields=id,text,timestamp,username,from,replies{{from,id,text}}&access_token={self.access_token}"
        try:
            response = requests.get(url)
            data = response.json()
            if "data" in data:
                return data["data"]
            return []
        except Exception as e:
            print(f"[API] Kommentlarni olishda xato: {e}")
            return []

    def reply_to_comment(self, comment_id: str, message: str) -> bool:
        """Berilgan izohga javob qaytaradi (Thread yaratadi)"""
        url = f"{self.base_url}/{comment_id}/replies"
        payload = {
            "message": message,
            "access_token": self.access_token
        }
        print(f"[API] Kommentga javob yozilmoqda...")
        response = requests.post(url, data=payload)
        data = response.json()
        
        if "id" in data:
            print(f"[API] Javob Muvaffaqiyatli qoldirildi!")
            return True
        else:
            print(f"[API] Javob yozishda xatolik: {data}")
            return False

