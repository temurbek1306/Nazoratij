import os
import shutil

class VideoManager:
    def __init__(self, base_dir="videos"):
        self.base_dir = base_dir
        self.pending_dir = os.path.join(self.base_dir, "pending")
        
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Kerakli papkalarni yaratish"""
        for d in [self.base_dir, self.pending_dir]:
            if not os.path.exists(d):
                os.makedirs(d)
                
    def get_next_video(self, queue_type="regular") -> str:
        """Navbatdagi videoni olib beradi. queue_type 'regular' yoki 'trial' bo'lishi mumkin."""
        files = os.listdir(self.pending_dir)
        video_files = []
        
        for f in files:
            if f.lower().endswith(('.mp4', '.mov')):
                base_name = os.path.splitext(f)[0]
                is_trial = os.path.exists(os.path.join(self.pending_dir, f"{base_name}.trial.txt"))
                
                if queue_type == "trial" and is_trial:
                    video_files.append(f)
                elif queue_type == "regular" and not is_trial:
                    video_files.append(f)
        
        if not video_files:
            return None
            
        # Alifbo o'rniga fayl nomidagi run_id (tarix) bo'yicha tartiblash
        def extract_run_id(f):
            import re
            match = re.search(r'_(\d+)\.(mp4|mov)$', f, re.IGNORECASE)
            return int(match.group(1)) if match else 0
            
        video_files.sort(key=extract_run_id)
        return video_files[0]
        
    def mark_as_posted(self, filename: str):
        """Qo'yilgan videoni butunlay o'chirib yuboradi (Musur yig'ilmasligi uchun barcha qoldiq fayllari bilan)"""
        base_name = os.path.splitext(filename)[0]
        
        # O'chirilishi kerak bo'lgan barcha fayl turlari
        files_to_remove = [
            filename,
            f"{base_name}.txt",
            f"{base_name}.json",
            f"{base_name}.platform.txt",
            f"{base_name}.trial.txt"
        ]
        
        for f_name in files_to_remove:
            path = os.path.join(self.pending_dir, f_name)
            if os.path.exists(path):
                os.remove(path)
                
        print(f"[VideoManager] '{base_name}' nomli video va uning barcha qoldiq fayllari (txt, json, platform) butunlay o'chirildi (Xotira tozalandi).")
            
    def get_caption_for_video(self, filename: str) -> str:
        """Agar video bilan bir xil nomdagi .txt fayl bo'lsa, uni caption qilib o'qiydi"""
        base_name = os.path.splitext(filename)[0]
        txt_file = os.path.join(self.pending_dir, f"{base_name}.txt")
        
        if os.path.exists(txt_file):
            with open(txt_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
                
        # Agar maxsus caption bo'lmasa, standart caption qaytaradi
        return "Avtomatik joylangan Reel! 🚀\n#reels #auto #python"
