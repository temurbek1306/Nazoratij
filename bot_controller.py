import os
import glob
import requests
import github_runner

def send_telegram_msg(text, reply_markup=None):
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    tg_admin = os.getenv("TELEGRAM_ADMIN_ID")
    if tg_token and tg_admin:
        try:
            data = {
                "chat_id": tg_admin,
                "text": text,
                "parse_mode": "HTML"
            }
            if reply_markup:
                data["reply_markup"] = reply_markup
            requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", data=data)
        except Exception as e:
            print(f"Telegram xatosi: {e}")

def handle_list():
    import datetime
    os.makedirs("videos/pending", exist_ok=True)
    files = [f for f in os.listdir("videos/pending") if f.endswith(('.mp4', '.mov'))]
    def extract_run_id(f):
        import re
        match = re.search(r'_(\d+)\.(mp4|mov)$', f, re.IGNORECASE)
        return int(match.group(1)) if match else 0
        
    files.sort(key=extract_run_id) # Ensure they are shown in processing order (github run_ids)
    if not files:
        send_telegram_msg("📭 Oddiy navbatda hech qanday video yo'q.")
        return
    
    interval_str = os.getenv("TELEGRAM_INTERVAL", "2")
    if not interval_str.strip():
        interval_str = "2"
    interval_hours = int(interval_str)
    
    last_run_str = os.getenv("TELEGRAM_LAST_RUN", "0")
    if not last_run_str.strip():
        last_run_str = "0"
    last_run_timestamp = float(last_run_str)
    
    msg = f"📋 <b>Oddiy navbatdagi videolar ({len(files)} ta):</b>\n\n"
    
    # Calculate base time. If last_run is 0 or too old, the next post is practically 'now' + interval.
    # But wait, cron.php posts if current_time >= last_run + interval.
    # So the *next* post will be at max(current_time, last_run + interval).
    # Then subsequent posts add interval.
    # Since we need to show Uzbekistan time (UTC+5), we will convert everything to UTC+5.
    now_utc = datetime.datetime.utcnow()
    current_time_ts = now_utc.timestamp()
    
    interval_seconds = interval_hours * 3600
    next_post_ts = last_run_timestamp + interval_seconds
    if next_post_ts < current_time_ts:
        # If interval already passed, it will post on the next cron run (which is essentially 'now')
        next_post_ts = current_time_ts
        
    for i, f in enumerate(files, 0):
        estimated_ts = next_post_ts + (i * interval_seconds)
        estimated_time = datetime.datetime.utcfromtimestamp(estimated_ts) + datetime.timedelta(hours=5)
        time_str = estimated_time.strftime("%d.%m.%Y %H:%M")
        msg += f"{i+1}. {f} <i>(~{time_str} da)</i>\n"
        
    import json
    keyboard_buttons = []
    row = []
    for i, f in enumerate(files, 1):
        # We use a short callback data to avoid limits (64 bytes max)
        # Using base filename instead of full name if it's too long
        cb_data = f"del_{f[:50]}"
        row.append({"text": f"🗑 {i}", "callback_data": cb_data})
        if len(row) == 5:
            keyboard_buttons.append(row)
            row = []
    if row:
        keyboard_buttons.append(row)
        
    reply_markup = json.dumps({"inline_keyboard": keyboard_buttons}) if keyboard_buttons else None
    
    send_telegram_msg(msg, reply_markup=reply_markup)

def handle_clear():
    count = 0
    
    # Delete pending
    pending_files = glob.glob("videos/pending/*")
    for f in pending_files:
        if f.endswith(('.mp4', '.mov', '.txt', '.json')):
            os.remove(f)
            count += 1
            
    # Delete posted
    posted_files = glob.glob("videos/posted/*")
    for f in posted_files:
        if f.endswith(('.mp4', '.mov', '.txt', '.json')):
            os.remove(f)
            count += 1
            
    send_telegram_msg(f"🧹 <b>Navbat va Eski videolar tozalandi!</b>\n\nJami {count} ta fayl o'chirib tashlandi.")

def handle_stats():
    send_telegram_msg("⏳ Statistika yig'ilmoqda va AI tahlil qilmoqda... (Biroz kuting)")
    
    os.makedirs("videos/pending", exist_ok=True)
    pending_files = [f for f in os.listdir("videos/pending") if f.endswith(('.mp4', '.mov'))]
    
    yt_stats = None
    ig_stats = None
    
    # YouTube stats
    yt_client_id = os.getenv("YOUTUBE_CLIENT_ID")
    yt_client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
    yt_refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")
    if yt_client_id and yt_client_secret and yt_refresh_token:
        try:
            from youtube_api import YouTubeAPI
            yt_api = YouTubeAPI(yt_client_id, yt_client_secret, yt_refresh_token)
            yt_stats = yt_api.get_channel_stats()
        except: pass
            
    # IG stats
    ig_token = os.getenv("IG_ACCESS_TOKEN")
    ig_account_id = os.getenv("IG_ACCOUNT_ID")
    if ig_token and ig_account_id:
        try:
            from instagram_api import InstagramAPI
            ig_api = InstagramAPI(ig_token, ig_account_id)
            ig_stats = ig_api.get_profile_stats()
        except: pass

    # History Logic
    import json
    from datetime import datetime, timedelta
    
    history_file = "stats_history.json"
    history = {}
    if os.path.exists(history_file):
        try:
            with open(history_file, "r") as f:
                history = json.load(f)
        except: pass
        
    today_str = datetime.now().strftime("%Y-%m-%d")
    yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    last_week_str = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    last_month_str = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    current_data = {"yt": yt_stats or {}, "ig": ig_stats or {}}
    history[today_str] = current_data
    
    # Eskirgan ma'lumotlarni tozalash (45 kundan eskisini o'chirish)
    keys_to_delete = []
    for k_date_str in history:
        try:
            k_date = datetime.strptime(k_date_str, "%Y-%m-%d")
            if (datetime.now() - k_date).days > 45:
                keys_to_delete.append(k_date_str)
        except:
            keys_to_delete.append(k_date_str) # Noto'g'ri formatlarni ham o'chiramiz
            
    for k in keys_to_delete:
        del history[k]
    
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)
        
    def get_closest_past_data(target_date_str):
        if target_date_str in history: return history[target_date_str]
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
        closest_date = None
        min_diff = 9999
        for k in history:
            try:
                dt = datetime.strptime(k, "%Y-%m-%d")
                diff = abs((target_date - dt).days)
                if diff < min_diff and dt < datetime.now():
                    min_diff = diff
                    closest_date = k
            except: pass
        if closest_date and min_diff <= 3:
            return history[closest_date]
        return None

    stats_payload = {
        "current": current_data,
        "yesterday": get_closest_past_data(yesterday_str),
        "last_week": get_closest_past_data(last_week_str),
        "last_month": get_closest_past_data(last_month_str)
    }
    
    from ai_assistant import generate_stats_analysis
    ai_report = generate_stats_analysis(stats_payload)
    
    final_msg = f"⏳ <b>Kutilayotgan videolar (Navbatda): {len(pending_files)} ta</b>\n\n"
    final_msg += ai_report
    
    send_telegram_msg(final_msg)

def run():
    command_raw = os.getenv("TELEGRAM_COMMAND", "").strip()
    command = command_raw.lower()
    prompt = os.getenv("TELEGRAM_PROMPT", "").strip()
    
    if not command:
        print("Hech qanday komanda berilmadi.")
        return
        
    print(f"Qabul qilingan komanda: {command_raw}")
    
    if command == "list":
        handle_list()
    elif command == "clear":
        handle_clear()
    elif command == "stats":
        handle_stats()
    elif command == "post_now":
        send_telegram_msg("🚀 AI'lar jangi boshlanmoqda! (30-40 soniya...)")
        github_runner.run()
    elif command.startswith("post_a_") or command.startswith("post_b_") or command.startswith("post_c_") or command.startswith("cancel_"):
        send_telegram_msg("🚀 Tasdiqlandi! Yakuniy post jarayoni boshlandi...")
        import github_runner_approved
        github_runner_approved.run()
    elif command == "generate_video":
        text = payload.get("prompt", "")
        parts = text.split("|||", 1)
        if len(parts) == 2:
            ratio, prompt_text = parts
        else:
            ratio = "16:9"
            prompt_text = text
            
        import video_generator
        video_generator.generate(prompt_text, ratio)
    elif command == "strategy":
        try:
            import ai_assistant
            import requests
            send_telegram_msg("🧠 AI Profilingizni analiz qilmoqda... (Kuting)")
            
            ig_token = os.getenv("IG_ACCESS_TOKEN")
            ig_account_id = os.getenv("IG_ACCOUNT_ID")
            
            profile_data = "Ayni paytda Instagram hisobi ulanmagan yoki postlar yo'q."
            trend_data = "Ayni paytda trendlarni o'qib bo'lmadi."
            
            if ig_token and ig_account_id:
                try:
                    url = f"https://graph.facebook.com/v18.0/{ig_account_id}/media?fields=caption,like_count,comments_count,media_type&limit=15&access_token={ig_token}"
                    res = requests.get(url).json()
                    if "data" in res and len(res["data"]) > 0:
                        posts = res["data"]
                        sorted_posts = sorted(posts, key=lambda x: x.get('like_count', 0), reverse=True)
                        top_posts = sorted_posts[:3]
                        profile_data = "Foydalanuvchining Instagramdagi eng omadli (Top 3) postlari:\n"
                        for i, p in enumerate(top_posts):
                            cpt = p.get('caption', 'Sarlavha yoq')[:150].replace('\n', ' ')
                            lks = p.get('like_count', 0)
                            cms = p.get('comments_count', 0)
                            profile_data += f"{i+1}-post. Layklar: {lks}, Kommentlar: {cms}. Sarlavhasi: '{cpt}'\n"
                except Exception as e:
                    print("IG Profile fetch error:", e)
                    
                try:
                    trend_data = "Butun Instagramdagi ayni damdagi (IT va AI bo'yicha) eng ommabop begona postlar (Trendlar):\n"
                    for hashtag in ["dasturlash", "sunniyintellekt"]:
                        h_url = f"https://graph.facebook.com/v18.0/ig_hashtag_search?user_id={ig_account_id}&q={hashtag}&access_token={ig_token}"
                        h_res = requests.get(h_url).json()
                        if "data" in h_res and len(h_res["data"]) > 0:
                            h_id = h_res["data"][0]["id"]
                            top_url = f"https://graph.facebook.com/v18.0/{h_id}/top_media?user_id={ig_account_id}&fields=caption,like_count&limit=5&access_token={ig_token}"
                            top_res = requests.get(top_url).json()
                            if "data" in top_res:
                                for idx, p in enumerate(top_res["data"]):
                                    cpt = p.get('caption', 'Sarlavha yoq')[:150].replace('\n', ' ')
                                    lks = p.get('like_count', 0)
                                    trend_data += f"- #{hashtag} bo'yicha Top-{idx+1}: Layklar: {lks}, Sarlavhasi: '{cpt}'\n"
                except Exception as e:
                    print("IG Trend fetch error:", e)
            
            ai_response = ai_assistant.generate_data_driven_strategy(profile_data, trend_data)
            if not ai_response: ai_response = "Kechirasiz, Groq ishlamadi."
            send_telegram_msg("📊 <b>Analiz Yakunlandi! 30 Kunlik Kontent Rejangiz:</b>\n\n" + ai_response)
        except Exception as e:
            send_telegram_msg(f"⚠️ Xatolik: {e}")
    elif command == "brainstorm":
        if prompt.startswith("http"):
            send_telegram_msg("📥 Bu linkka o'xshaydi. Link orqali yuklab olish funksiyasi tez kunda (Keyingi qadamda) qo'shiladi!")
        else:
            try:
                import ai_assistant
                ai_response = ai_assistant.brainstorm_idea(prompt)
                send_telegram_msg(ai_response)
            except Exception as e:
                send_telegram_msg("⚠️ Xatolik yuz berdi: " + str(e))
    elif command.startswith("del_"):
        video_name_prefix = command_raw.split("_", 1)[1]
        # Barcha pending videolarni qidiramiz
        files = [f for f in os.listdir("videos/pending") if f.startswith(video_name_prefix) and f.endswith(('.mp4', '.mov'))]
        if files:
            video_to_delete = files[0]
            os.remove(f"videos/pending/{video_to_delete}")
            json_file = f"videos/pending/{os.path.splitext(video_to_delete)[0]}.json"
            if os.path.exists(json_file):
                os.remove(json_file)
            txt_file = f"videos/pending/{os.path.splitext(video_to_delete)[0]}.txt"
            if os.path.exists(txt_file):
                os.remove(txt_file)
                
            send_telegram_msg(f"🗑 <b>{video_to_delete}</b> muvaffaqiyatli navbatdan o'chirildi!")
            handle_list()
        else:
            send_telegram_msg("⚠️ O'chirish uchun fayl topilmadi. U allaqachon o'chirilgan bo'lishi mumkin.")
    else:
        send_telegram_msg("❓ Noma'lum komanda.")

if __name__ == "__main__":
    run()
