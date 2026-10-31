import os
import requests
import time

class InstagramAPI:
    def __init__(self, access_token: str, account_id: str):
        self.access_token = access_token
        self.account_id = account_id
        self.base_url = "https://graph.facebook.com/v19.0"

    def upload_reel(self, video_url: str, caption: str = "", is_trial: bool = False, graduation_strategy: str = "MANUAL", cover_url: str = "") -> str:
        """Videoni Instagram serveriga yuklaydi (Container yaratadi). is_trial=True bo'lsa Trial Reel rejimida yuklanadi. cover_url - muqova rasmi (thumbnail) URL manzili."""
        import json as _json
        url = f"{self.base_url}/{self.account_id}/media"
        payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": self.access_token
        }
        
        if cover_url:
            payload["cover_url"] = cover_url
            print(f"[API] 🖼 Custom cover (thumbnail) biriktirilmoqda: {cover_url[:60]}...")
        
        if is_trial:
            # Trial Reel: faqat non-followers ko'radi, lentaga tushmaydi
            payload["trial_params"] = _json.dumps({"graduation_strategy": graduation_strategy})
            print(f"[API] 🧪 Video TRIAL REEL (Sinov) rejimida yuklanmoqda (Faqat non-followers ko'radi)...")
        else:
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
            comment_id = data["id"]
            print(f"[API] Izoh Muvaffaqiyatli qoldirildi! (Comment ID: {comment_id})")
            # Instagram Graph API orqali pin (qadash) qilishga urinish
            try:
                pin_url = f"{self.base_url}/{comment_id}"
                pin_res = requests.post(pin_url, data={"pinned": "true", "access_token": self.access_token}, timeout=5)
                if pin_res.status_code == 200:
                    print(f"[API] 📌 Izoh muvaffaqiyatli qadaldi (pinned)!")
            except Exception:
                pass
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
        """Berilgan postning barcha izohlarini olib keladi (replies bilan birga)"""
        url = f"{self.base_url}/{media_id}/comments?fields=id,text,timestamp,username,from,replies{{id,text,timestamp,username,from}}&access_token={self.access_token}"
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

    def _get(self, path: str, **params) -> dict:
        params["access_token"] = self.access_token
        return requests.get(f"{self.base_url}/{path}", params=params, timeout=60).json()

    def _post(self, path: str, **payload) -> dict:
        payload["access_token"] = self.access_token
        return requests.post(f"{self.base_url}/{path}", data=payload, timeout=60).json()

    def _delete(self, path: str) -> dict:
        return requests.delete(f"{self.base_url}/{path}", params={"access_token": self.access_token}, timeout=60).json()

    def _publish_container(self, payload: dict):
        """Container yaratadi, tayyor bo'lishini kutadi va e'lon qiladi. Media ID qaytaradi."""
        data = self._post(f"{self.account_id}/media", **payload)
        if "id" not in data:
            raise Exception(f"[API] Container xatosi: {data}")
        if not self.check_status(data["id"]):
            raise Exception("[API] Media qayta ishlanmadi")
        media_id = self.publish_reel(data["id"])
        if not media_id:
            raise Exception("[API] E'lon qilinmadi")
        return media_id

    def publish_story(self, media_url: str, is_video: bool = False):
        """Rasm yoki videoni Story sifatida joylaydi."""
        key = "video_url" if is_video else "image_url"
        return self._publish_container({"media_type": "STORIES", key: media_url})

    def publish_photo(self, image_url: str, caption: str = ""):
        """Bitta rasmni post qiladi."""
        return self._publish_container({"image_url": image_url, "caption": caption})

    def publish_carousel(self, image_urls: list, caption: str = ""):
        """2-10 ta rasmni karusel qilib joylaydi."""
        children = []
        for image_url in image_urls:
            data = self._post(f"{self.account_id}/media", image_url=image_url, is_carousel_item="true")
            if "id" not in data:
                raise Exception(f"[API] Karusel elementi xatosi: {data}")
            children.append(data["id"])
        return self._publish_container({"media_type": "CAROUSEL", "children": ",".join(children), "caption": caption})

    def get_media_list(self, limit: int = 5) -> list:
        fields = "id,caption,media_type,timestamp,permalink,like_count,comments_count,comments_enabled"
        return self._get(f"{self.account_id}/media", fields=fields, limit=limit).get("data", [])

    def get_media_insights(self, media_id: str) -> dict:
        """Post statistikasi. Media turi qo'llamaydigan metrikalar tashlab ketiladi."""
        result = {}
        for metric in ["reach", "views", "likes", "comments", "shares", "saved"]:
            for item in self._get(f"{media_id}/insights", metric=metric).get("data", []):
                result[item["name"]] = item["values"][0]["value"]
        return result

    def get_account_insights(self) -> dict:
        """Akkauntning oxirgi 1 kunlik statistikasi."""
        result = {}
        for item in self._get(f"{self.account_id}/insights", metric="reach,follower_count", period="day").get("data", []):
            result[item["name"]] = item["values"][-1]["value"]
        data = self._get(f"{self.account_id}/insights", metric="profile_views,accounts_engaged,total_interactions", period="day", metric_type="total_value")
        for item in data.get("data", []):
            result[item["name"]] = item.get("total_value", {}).get("value", 0)
        return result

    def delete_comment(self, comment_id: str) -> dict:
        return self._delete(comment_id)

    def hide_comment(self, comment_id: str, hide: bool = True) -> dict:
        return self._post(comment_id, hide="true" if hide else "false")

    def set_comments_enabled(self, media_id: str, enabled: bool) -> dict:
        return self._post(media_id, comment_enabled="true" if enabled else "false")

    def delete_media(self, media_id: str) -> dict:
        return self._delete(media_id)

    def get_tagged_media(self, limit: int = 5) -> list:
        return self._get(f"{self.account_id}/tags", fields="id,username,caption,permalink,timestamp", limit=limit).get("data", [])

    def search_hashtag(self, tag: str, limit: int = 5) -> list:
        found = self._get("ig_hashtag_search", user_id=self.account_id, q=tag.lstrip("#")).get("data", [])
        if not found:
            return []
        return self._get(f"{found[0]['id']}/recent_media", user_id=self.account_id, fields="caption,permalink,like_count,comments_count", limit=limit).get("data", [])

