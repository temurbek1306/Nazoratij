import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

class YouTubeAPI:
    def __init__(self, client_id, client_secret, refresh_token):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.scopes = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly"]
        self.youtube = self._get_authenticated_service()

    def _get_authenticated_service(self):
        print("🔗 YouTube API'ga ulanilmoqda...")
        credentials = Credentials(
            token=None,
            refresh_token=self.refresh_token,
            client_id=self.client_id,
            client_secret=self.client_secret,
            token_uri="https://oauth2.googleapis.com/token",
            scopes=self.scopes
        )
        
        if not credentials.valid:
            if credentials.refresh_token:
                credentials.refresh(Request())
            else:
                raise Exception("API kalitlar noto'g'ri. YouTube'ga ulanib bo'lmadi.")
                
        return build('youtube', 'v3', credentials=credentials)

    def upload_shorts(self, video_path: str, title: str, description: str, tags: list = None) -> str:
        """
        Videoni YouTube Shorts sifatida yuklaydi.
        Sarlavha yoki tavsifda #shorts bo'lishi Shorts ekanligini bildiradi.
        """
        if tags is None:
            tags = ["shorts", "programming", "uzbekistan", "dasturlash"]
            
        print(f"🎬 YouTube Shorts'ga yuklanmoqda: {video_path}")
        
        body = {
            'snippet': {
                'title': title,
                'description': description + "\n\n#shorts #dasturlash #ituz #temurbekdev",
                'tags': tags,
                'categoryId': '27' # Education
            },
            'status': {
                'privacyStatus': 'public', # 'private' yoki 'unlisted' qilish mumkin sinov uchun
                'selfDeclaredMadeForKids': False
            }
        }

        insert_request = self.youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
        )

        response = insert_request.execute()
        
        video_id = response.get('id')
        if video_id:
            print(f"✅ MUVAFFAQIYATLI! YouTube Shorts ID: {video_id}")
            print(f"🔗 Link: https://youtube.com/shorts/{video_id}")
            return video_id
        else:
            raise Exception("YouTube'ga yuklashda kutilmagan xato yuz berdi.")

    def get_channel_stats(self):
        """YouTube kanal statistikasini olib beradi"""
        try:
            request = self.youtube.channels().list(part="statistics", mine=True)
            response = request.execute()
            if "items" in response and len(response["items"]) > 0:
                stats = response["items"][0]["statistics"]
                return {
                    "subscribers": stats.get("subscriberCount", "Noma'lum"),
                    "views": stats.get("viewCount", "Noma'lum"),
                    "videos": stats.get("videoCount", "Noma'lum")
                }
        except Exception as e:
            print(f"YouTube Stats API xatosi (Scope muammosi bo'lishi mumkin): {e}")
        return None
