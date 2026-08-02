import requests
import os
import time

class FacebookReelsAPI:
    def __init__(self, page_id, access_token):
        self.page_id = page_id
        self.access_token = access_token
        self.graph_url = "https://graph.facebook.com/v19.0"

    def upload_reel(self, video_path: str, description: str) -> bool:
        if not self.page_id or not self.access_token:
            print("❌ FB_PAGE_ID yoki FB_PAGE_ACCESS_TOKEN kiritilmagan.")
            return False

        print(f"📘 Facebook Reels yuklash boshlanmoqda: {video_path}")
        
        try:
            # 1. Start Upload Session
            start_payload = {
                'upload_phase': 'start',
                'access_token': self.access_token
            }
            start_res = requests.post(f"{self.graph_url}/{self.page_id}/video_reels", data=start_payload).json()
            
            if 'video_id' not in start_res:
                print(f"❌ Start bosqichida xatolik: {start_res}")
                return False
                
            video_id = start_res['video_id']
            print(f"✅ Upload session ochildi. Video ID: {video_id}")

            # 2. Upload Video Bytes
            file_size = os.path.getsize(video_path)
            
            upload_headers = {
                'Authorization': f'OAuth {self.access_token}',
                'offset': '0',
                'file_size': str(file_size)
            }
            
            upload_url = f"https://rupload.facebook.com/video-upload/v19.0/{video_id}"
            with open(video_path, 'rb') as f:
                upload_res = requests.post(upload_url, headers=upload_headers, data=f)
            
            if upload_res.status_code != 200:
                print(f"❌ Faylni yuklashda xatolik: {upload_res.text}")
                return False
                
            print("✅ Fayl serverga muvaffaqiyatli yuklandi. Facebook protsessingini kutyapmiz (15 soniya)...")
            time.sleep(15)

            # 3. Publish Reel
            finish_payload = {
                'upload_phase': 'finish',
                'video_id': video_id,
                'video_state': 'PUBLISHED',
                'description': description,
                'access_token': self.access_token
            }
            
            finish_res = requests.post(f"{self.graph_url}/{self.page_id}/video_reels", data=finish_payload).json()
            
            if 'success' in finish_res and finish_res['success']:
                print("✅ Facebook Reels muvaffaqiyatli e'lon qilindi!")
                return True
            else:
                print(f"❌ Finish bosqichida xatolik: {finish_res}")
                return False
                
        except Exception as e:
            print(f"❌ Facebook API Xatolik: {e}")
            return False
