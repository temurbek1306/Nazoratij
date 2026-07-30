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
        self.scopes = [
            "https://www.googleapis.com/auth/youtube",
            "https://www.googleapis.com/auth/youtube.force-ssl"
        ]
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

    def post_comment(self, video_id: str, comment_text: str):
        """YouTube Shorts videoga izoh yozish"""
        try:
            body = {
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": comment_text
                        }
                    }
                }
            }
            request = self.youtube.commentThreads().insert(
                part="snippet",
                body=body
            )
            response = request.execute()
            print(f"💬 YouTube izoh qoldirildi!")
            return True
        except Exception as e:
            print(f"⚠️ YouTube izoh qoldirishda xatolik (Balki scope yetishmas): {e}")
            return False

    def get_recent_videos(self, limit: int = 5):
        """Oxirgi yuklangan videolarni olib keladi"""
        try:
            # Kanal uploads playlist id sini olamiz
            channels_response = self.youtube.channels().list(mine=True, part="contentDetails").execute()
            if "items" not in channels_response or not channels_response["items"]:
                return []
            uploads_playlist_id = channels_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
            
            # Playlistdagi videolarni olamiz
            playlist_response = self.youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_playlist_id,
                maxResults=limit
            ).execute()
            
            videos = []
            if "items" in playlist_response:
                for item in playlist_response["items"]:
                    videos.append({
                        "id": item["snippet"]["resourceId"]["videoId"],
                        "title": item["snippet"]["title"],
                        "timestamp": item["snippet"]["publishedAt"]
                    })
            return videos
        except Exception as e:
            print(f"⚠️ YouTube videolarni olishda xato: {e}")
            return []

    def get_comments(self, video_id: str):
        """Berilgan videodagi izohlarni olib keladi"""
        try:
            response = self.youtube.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                maxResults=50,
                textFormat="plainText"
            ).execute()
            
            comments = []
            if "items" in response:
                for item in response["items"]:
                    top_comment = item["snippet"]["topLevelComment"]["snippet"]
                    comments.append({
                        "id": item["id"],
                        "text": top_comment["textDisplay"],
                        "author": top_comment["authorDisplayName"],
                        "timestamp": top_comment["publishedAt"],
                        "has_replies": item["snippet"]["totalReplyCount"] > 0
                    })
            return comments
        except Exception as e:
            # Ehtimol comments o'chirilgan bo'lishi mumkin
            print(f"⚠️ YouTube izohlarni olishda xato ({video_id}): {e}")
            return []

    def reply_to_comment(self, comment_id: str, message: str) -> bool:
        """Berilgan YouTube izohiga javob yozish (Reply)"""
        try:
            body = {
                "snippet": {
                    "parentId": comment_id,
                    "textOriginal": message
                }
            }
            request = self.youtube.comments().insert(
                part="snippet",
                body=body
            )
            response = request.execute()
            print(f"💬 YouTube izohiga javob qaytarildi!")
            return True
        except Exception as e:
            print(f"⚠️ YouTube izohiga javob yozishda xatolik: {e}")
            return False

