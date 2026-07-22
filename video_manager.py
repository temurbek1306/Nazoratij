import os
import shutil

class VideoManager:
    def __init__(self, base_dir="videos"):
        self.base_dir = base_dir
        self.pending_dir = os.path.join(self.base_dir, "pending")
        self.posted_dir = os.path.join(self.base_dir, "posted")
        
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Kerakli papkalarni yaratish"""
        for d in [self.base_dir, self.pending_dir, self.posted_dir]:
            if not os.path.exists(d):
                os.makedirs(d)
                
    def get_next_video(self) -> str:
        """Navbatdagi videoni olib beradi"""
        files = os.listdir(self.pending_dir)
        video_files = [f for f in files if f.lower().endswith(('.mp4', '.mov'))]
        
        if not video_files:
            return None
            
        # Alifbo tartibida yoki vaqt bo'yicha eng birinchisini oladi
        video_files.sort()
        return video_files[0]
        
    def mark_as_posted(self, filename: str):
        """Qo'yilgan videoni butunlay o'chirib yuboradi (Musur yig'ilmasligi uchun)"""
        source = os.path.join(self.pending_dir, filename)
        
        if os.path.exists(source):
            os.remove(source)
            print(f"[VideoManager] '{filename}' joylangandan so'ng butunlay o'chirildi (Xotira tozalandi).")
            
    def get_caption_for_video(self, filename: str) -> str:
        """Agar video bilan bir xil nomdagi .txt fayl bo'lsa, uni caption qilib o'qiydi"""
        base_name = os.path.splitext(filename)[0]
        txt_file = os.path.join(self.pending_dir, f"{base_name}.txt")
        
        if os.path.exists(txt_file):
            with open(txt_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
                
        # Agar maxsus caption bo'lmasa, standart caption qaytaradi
        return "Avtomatik joylangan Reel! 🚀\n#reels #auto #python"
