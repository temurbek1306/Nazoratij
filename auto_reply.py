import os
import json
import time
from dotenv import load_dotenv

# API sınıflarını yuklash
from instagram_api import InstagramAPI
from youtube_api import YouTubeAPI
import ai_assistant

load_dotenv()

REPLIED_COMMENTS_FILE = "replied_comments.json"

def load_replied_comments():
    if os.path.exists(REPLIED_COMMENTS_FILE):
        try:
            with open(REPLIED_COMMENTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"instagram": [], "youtube": []}
    return {"instagram": [], "youtube": []}

def save_replied_comments(data):
    # Har bir tarmoq uchun faqat oxirgi 1000 ta izohni saqlaymiz (xotira to'lib ketmasligi uchun)
    data["instagram"] = data.get("instagram", [])[-1000:]
    data["youtube"] = data.get("youtube", [])[-1000:]
    with open(REPLIED_COMMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def check_and_reply_instagram(replied_data):
    ig_token = os.getenv("IG_ACCESS_TOKEN")
    ig_account_id = os.getenv("IG_ACCOUNT_ID")
    
    if not ig_token or not ig_account_id:
        print("[AutoReply] Instagram kalitlari topilmadi.")
        return

    print("--- Instagram izohlari tekshirilmoqda ---")
    ig = InstagramAPI(ig_token, ig_account_id)
    recent_media = ig.get_recent_media(limit=5)
    
    for media in recent_media:
        media_id = media["id"]
        comments = ig.get_comments(media_id)
        
        for comment in comments:
            comment_id = comment["id"]
            
            # Agar o'zimiz yozgan bo'lsak yoki allaqachon javob bergan bo'lsak, o'tkazib yuboramiz
            if comment_id in replied_data["instagram"]:
                continue
                
            # 'from' obyekti ba'zan bo'lmasligi mumkin
            username = comment.get("username", "Foydalanuvchi")
            if comment.get("from") and comment["from"].get("id") == ig_account_id:
                # O'zimizning izohimiz
                replied_data["instagram"].append(comment_id)
                continue
                
            bot_replied = False
            if "replies" in comment and "data" in comment["replies"]:
                for reply in comment["replies"]["data"]:
                    if reply.get("from") and reply["from"].get("id") == ig_account_id:
                        bot_replied = True
                        break
                        
            if bot_replied:
                if comment_id not in replied_data["instagram"]:
                    replied_data["instagram"].append(comment_id)
                continue
                
            text = comment.get("text", "")
            if not text:
                continue
                
            print(f"[IG] Yangi izoh ({username}): {text}")
            
            # AI dan javob olish
            if "+" in text:
                reply_text = "Xizmatimizdan foydalanish uchun telegramdan yozing @Temurbek_Gulboyev"
            else:
                reply_text = ai_assistant.generate_comment_reply(text, "Instagram", username)
            print(f"[AI Javobi]: {reply_text}")
            
            # Javobni yuborish
            success = ig.reply_to_comment(comment_id, reply_text)
            if success:
                replied_data["instagram"].append(comment_id)
                save_replied_comments(replied_data)
                
            time.sleep(2) # API limitlaridan qochish uchun

def check_and_reply_youtube(replied_data):
    client_id = os.getenv("YOUTUBE_CLIENT_ID")
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")
    
    if not all([client_id, client_secret, refresh_token]):
        print("[AutoReply] YouTube kalitlari to'liq emas.")
        return

    print("--- YouTube izohlari tekshirilmoqda ---")
    try:
        yt = YouTubeAPI(client_id, client_secret, refresh_token)
    except Exception as e:
        print(f"[AutoReply] YouTube'ga ulanib bo'lmadi: {e}")
        return
        
    recent_videos = yt.get_recent_videos(limit=5)
    
    for video in recent_videos:
        video_id = video["id"]
        comments = yt.get_comments(video_id)
        
        for comment in comments:
            comment_id = comment["id"]
            
            if comment_id in replied_data["youtube"]:
                continue
                
            # O'zimizning kanal nomimiz bilan solishtirish uchun ID ni bilsak yaxshi,
            # Lekin YouTube API 'authorChannelId' ni 'textFormat' orqali olish biroz murakkab
            # Hozircha hamma izohlarga AI javob beradi (agar oldin javob yozilmagan bo'lsa)
            if comment.get("has_replies"):
                # Agar allaqachon javob (reply) bo'lsa, javob bermaymiz deb hisoblaymiz
                replied_data["youtube"].append(comment_id)
                continue
                
            text = comment.get("text", "")
            username = comment.get("author", "Tomoshabin")
            
            print(f"[YT] Yangi izoh ({username}): {text}")
            
            if "+" in text:
                reply_text = "Xizmatimizdan foydalanish uchun telegramdan yozing @Temurbek_Gulboyev"
            else:
                reply_text = ai_assistant.generate_comment_reply(text, "YouTube", username)
            print(f"[AI Javobi]: {reply_text}")
            
            success = yt.reply_to_comment(comment_id, reply_text)
            if success:
                replied_data["youtube"].append(comment_id)
                save_replied_comments(replied_data)
                
            time.sleep(2)

def main():
    print("🤖 AI Avtomatik Izoh Javobgari ishga tushdi...")
    replied_data = load_replied_comments()
    
    check_and_reply_instagram(replied_data)
    check_and_reply_youtube(replied_data)
    
    print("✅ Barcha tekshiruvlar tugadi!")

if __name__ == "__main__":
    main()
