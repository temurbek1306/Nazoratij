import os
import json
import random
import requests

class KeyManager:
    def __init__(self):
        keys_str = os.getenv("AI_KEYS_JSON")
        if keys_str:
            try:
                self.keys = json.loads(keys_str)
            except:
                self.keys = {"gemini": [], "groq": [], "openrouter": []}
        else:
            try:
                with open("ai_keys_secret.json", "r") as f:
                    self.keys = json.load(f)
            except:
                self.keys = {"gemini": [], "groq": [], "openrouter": []}
        
        try:
            with open("service_accounts.json", "r") as f:
                self.service_accounts = json.load(f)
        except:
            self.service_accounts = []
        
        self.current_groq_index = 0
        self.current_gemini_index = 0
        self.current_sa_index = 0
        self.current_or_index = 0
        
    def get_gemini_key(self):
        # Local .env dagi GEMINI_API_KEY ni birinchi navbatda tekshiramiz
        env_key = os.getenv("GEMINI_API_KEY")
        if env_key:
            return env_key
            
        # Oldin API kalitlarni tekshiramiz
        if self.keys.get("gemini") and len(self.keys["gemini"]) > 0:
            key = self.keys["gemini"][self.current_gemini_index]
            self.current_gemini_index = (self.current_gemini_index + 1) % len(self.keys["gemini"])
            return key
            
        # Agar API kalitlar bo'lmasa, Service Account orqali ulanish
        if self.service_accounts and len(self.service_accounts) > 0:
            sa = self.service_accounts[self.current_sa_index]
            self.current_sa_index = (self.current_sa_index + 1) % len(self.service_accounts)
            
            # Write the dynamically chosen SA to service_account.json
            with open("service_account.json", "w") as f:
                json.dump(sa, f, indent=2)
                
            return "SERVICE_ACCOUNT_AUTH"
        return None

    def get_groq_key(self):
        if self.keys.get("groq") and len(self.keys["groq"]) > 0:
            key = self.keys["groq"][self.current_groq_index]
            self.current_groq_index = (self.current_groq_index + 1) % len(self.keys["groq"])
            return key
        return None

    def get_openrouter_key(self):
        if self.keys.get("openrouter") and len(self.keys["openrouter"]) > 0:
            key = self.keys["openrouter"][self.current_or_index]
            self.current_or_index = (self.current_or_index + 1) % len(self.keys["openrouter"])
            return key
        return None

def brainstorm_idea(prompt):
    km = KeyManager()
    
    # AI Promptini kuchaytirish
    system_prompt = "Siz O'zbek tilida gaplashadigan professional SMM va Reels ekspertisiz. Javoblaringiz qisqa, aniq, kreativ va zamonaviy slanglar bilan yozilishi kerak."
    full_prompt = f"{system_prompt}\n\nMijoz savoli: {prompt}"
    
    # 1-Urinish: Gemini (Birinchi o'rinda)
    for _ in range(3):
        gemini_key = km.get_gemini_key()
        if not gemini_key:
            break
            
        try:
            import google.generativeai as genai
            if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
                del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-3.6-flash")
            response = model.generate_content(full_prompt)
            if response.text:
                return "✨ [Gemini AI]:\n\n" + response.text
        except Exception as e:
            continue

    # 2-Urinish: Groq (Llama-3) - Agar Gemini limitga tushsa
    for _ in range(3):
        groq_key = km.get_groq_key()
        if not groq_key:
            break
            
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama-3.3-70b-versatile", 
                "messages": [{"role": "user", "content": full_prompt}]
            }
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                return "⚡️ [Groq AI]:\n\n" + response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            continue
            
    # 3-Urinish: OpenRouter (Zaxira) - Agar Gemini va Groq ishlamasa
    for _ in range(3):
        or_key = km.get_openrouter_key()
        if not or_key:
            break
            
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {or_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "google/gemma-4-31b-it:free", 
                "messages": [{"role": "user", "content": full_prompt}]
            }
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                return "🌐 [OpenRouter AI]:\n\n" + response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            continue
            
    return "⚠️ Kechirasiz, barcha AI serverlari (Gemini, Groq, OpenRouter) hozircha band yoki API limitga tushdi."

def generate_caption_groq(summary):
    km = KeyManager()
    prompt = f"Sen O'zbekistondagi kreativ SMM ekpertsan. Quyida videoning chuqur tahlili (summary) berilgan. Buni diqqat bilan o'qi: \n\n{summary}\n\nVAZIFA: Aynan shu voqea, harakat va yozuvlarga 100% mos keladigan, videodan uzilib qolmagan Instagram post matnini (caption) yoz! Umumiy, hamma videoga tushadigan shablon gaplarni YOZMA. Kulgili, kinoyali yoki kreativ yondashuv qil. Oxirida odamlarni fikr bildirishga, LIKE bosishga va profilingizga OBUNA BO'LISHGA undovchi kreativ chaqiriq (Call to Action) qo'sh. DIQQAT: Hech qanday HASHTAG (#) ishlatma! Faqat toza matn yoz."
    
    for _ in range(3):
        groq_key = km.get_groq_key()
        if not groq_key: break
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
            payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]}
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
        except Exception:
            continue
    return None

def generate_caption_openrouter(summary):
    km = KeyManager()
    prompt = f"Sen O'zbekistondagi eng zo'r Reels muallifisan. Quyida videoning tahlili: \n\n{summary}\n\nVAZIFA: Ushbu videodagi har bir detal, yuz ifodasi yoki yozuvlarga moslab, o'quvchini qiziqtirib qo'yadigan qisqacha izoh (caption) yoz. Mutlaqo shablon va zerikarli gaplardan qoch. Oxirida obunachilarga LIKE bosish, KOMENTARIY yozish va albatta bizga OBUNA BO'LISHni (Follow) so'raydigan kreativ gap qo'sh. Hashtag umuman ishlatma! Faqat toza matn yoz."
    
    for _ in range(3):
        or_key = km.get_openrouter_key()
        if not or_key: break
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {or_key}", "Content-Type": "application/json"}
            payload = {"model": "google/gemma-4-31b-it:free", "messages": [{"role": "user", "content": prompt}]}
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"].strip()
        except Exception:
            continue
    return None

def generate_stats_analysis(stats_data: dict) -> str:
    """
    Statistika ma'lumotlarini qabul qilib, Gemini orqali tahlil yozib beradi.
    stats_data format:
    {
        "current": {"yt": {...}, "ig": {...}},
        "yesterday": {"yt": {...}, "ig": {...}},
        "last_week": {"yt": {...}, "ig": {...}},
        "last_month": {"yt": {...}, "ig": {...}}
    }
    """
    import json
    km = KeyManager()
    
    prompt = f"""Sen dunyodagi eng kuchli, 'Pro +++Max' darajadagi SMM strategi, psixolog va YouTube/Instagram ekspertisan.
Mijozingning YouTube va Instagram kanallari bo'yicha quyidagi JSON statistika keldi:
{json.dumps(stats_data, indent=2)}

DIQQAT - QAT'IY QOIDALAR (BU QOIDALARNI O'QIB, UNGA AMAL QIL, LEKIN ULARDAN IQTIBOS KELTIRMA):
1. Agar `yesterday`, `last_week`, yoki `last_month` qismlari `null` bo'lsa, o'zgarish yo'q dema. Shunchaki: "Bugun ma'lumotlaringiz birinchi marta bazaga ulandi. Hozircha bu faqat 'Start' (boshlang'ich) nuqta. Haqiqiy va aniq o'zgarishlarni ertadan boshlab taqqoslab beraman," deb yoz va gapni davom ettir. Menga berilgan qoidani matnga qoshib yozib yuborma!
2. Mijoz quruq raqamlarni o'zi ham ko'rib turibdi! Ularni shunchaki sanab berma. O'rniga, raqamlar orqasidagi YASHIRIN MA'NONI tahlil qil.
3. Oddiy va zerikarli maslahatlar berma. Buning o'rniga jahon darajasidagi eng kuchli blogerlar (MrBeast, Iman Gadzhi, Ali Abdaal) ishlatadigan bitta SIRLI SMM hiylasini o'rgat.
4. Mijoz bilan "Men sening shaxsiy prodyuseringman" degan ruhda, sovuqqon 'Sigma' uslubida (ortiqcha yalinmasdan, faktlar bilan) gaplash.
5. Qalin shrift qilish uchun ** ISHLATMA, uning o'rniga faqat HTML <b> va </b> taglaridan foydalan!
"""
    
    for _ in range(3):
        gemini_key = km.get_gemini_key()
        if not gemini_key: break
        try:
            import google.generativeai as genai
            if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
                del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-3.6-flash")
            response = model.generate_content(prompt)
            if response.text:
                import re
                return re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', response.text)
        except Exception as e:
            print(f"[AI Stats Error Gemini]: {e}")
            continue
            
    # Zaxira: Groq orqali
    for _ in range(3):
        groq_key = km.get_groq_key()
        if not groq_key: break
        try:
            import requests
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
            payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]}
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    import re
                    return re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', data["choices"][0]["message"]["content"].strip())
            else:
                print(f"[AI Stats Groq non-200]: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[AI Stats Error Groq]: {e}")
            continue
            
    # Zaxira 2: OpenRouter orqali
    for _ in range(3):
        or_key = km.get_openrouter_key()
        if not or_key: break
        try:
            import requests
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {or_key}", "Content-Type": "application/json"}
            payload = {"model": "google/gemini-2.0-flash-lite-preview-02-05:free", "messages": [{"role": "user", "content": prompt}]}
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    import re
                    return re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', data["choices"][0]["message"]["content"].strip())
            else:
                print(f"[AI Stats OR non-200]: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[AI Stats Error OR]: {e}")
            continue
            
    return "⚠️ AI tahlilini olishda xatolik yuz berdi. (Server band yoki limit tugagan)"

def append_viral_hashtags(caption):
    """
    AI o'zidan yomon/noto'g'ri hashteglar o'ylab topib videoni 'tashlab' yubormasligi uchun, 
    AI orqali hashteg yasash o'chirib qo'yildi. 
    Uning o'rniga foydalanuvchining 'Doimiy Hashteglar' funksiyasidan keladigan matn ishlatiladi.
    """
    clean_caption = "\n".join([line for line in caption.split("\n") if not line.strip().startswith("#")])
    return clean_caption.strip()

def generate_first_comment(caption):
    km = KeyManager()
    prompt = f"Sen kreativ SMM yozuvchisan. Quyidagi Reels/TikTok post matni (caption):\n\n{caption}\n\nVAZIFA: Odamlarni fikr bildirishga chorlaydigan 1 ta qisqacha 'Birinchi Komment' yoz (O'zbek tilida). Juda qisqa, qiziqarli yoki baxsli savol bo'lsin. Faqat komment matnini yoz, qo'shtirnoqlarsiz:"
    
    first_comment = ""
    for _ in range(3):
        gemini_key = km.get_gemini_key()
        if not gemini_key: break
        try:
            import google.generativeai as genai
            if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
                del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-3.6-flash")
            response = model.generate_content(prompt)
            if response.text:
                first_comment = response.text.strip().replace('"', '')
                break
        except Exception:
            pass
            
    if not first_comment:
        for _ in range(3):
            groq_key = km.get_groq_key()
            if not groq_key: break
            try:
                import requests
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
                payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]}
                response = requests.post(url, headers=headers, json=payload, timeout=10)
                if response.status_code == 200:
                    first_comment = response.json()["choices"][0]["message"]["content"].strip().replace('"', '')
                    break
            except Exception:
                pass
                
    if not first_comment:
        first_comment = "Videodagi holat kimga tanish? 😂 Fikringizni yozib qoldiring 👇"
        
    return first_comment

def generate_data_driven_strategy(profile_data, trend_data):
    import random
    import time
    km = KeyManager()
    prompt = f"""# SENING ROLING VA DARAJANG:
Sen oddiy AI emassan. Sen ijtimoiy tarmoqlar (Insta, TikTok, YouTube) algoritmalarini buzib tashlaydigan, millionlab prosmotrlar olib keladigan, inson psixologiyasini eng chuqur his qiladigan "Pro +++Max" darajadagi Viral Kontent Prodyuserisan! Sening vazifang menga 20 kunlik shunday kontent plan yozib berishki, uni o'qigan odamning miyasi portlab ketsin!

# INPUT (KIRITUVCHI MA'LUMOTLAR):
- Profil yo'nalishi (Mavzu): {profile_data}
- Hozirgi Trendlar: {trend_data}

(Tasodifiy kodi: {random.randint(1000,99999)})

# ⚠️ QAT'IY QOIDALAR (BUZISH TAQIQLANADI, "PRO +++MAX" REJIMI):
1. 20 KUN = 20 TA MUTLAQO HAR XIL OLAM! Hech qachon bir xil mavzuni, bir xil mantiqni yoki bir xil xulosani qaytara ko'rma! Siklga (loop) tushib qolish umuman mumkin emas. Har bir kun mutlaqo yangi bir fojia, komediya yoki psixologik fakt bo'lishi shart.
2. 100% HAYOTIY VA MANTIQIY (RELATABLE): Syujetlar osmondan olinmasin! Odamlar ko'rganda "Iye, bu aniq men-ku!" deb do'stlariga yuborishga majbur bo'lsin. Mavhum, ma'nosiz (masalan, qorong'i xonada yig'lash, mavhum falsafa) shablonlardan qat'iyan qoch! Har bir syujet real hayotdagi aniq bir muammo yoki kulguli mantiqqa (paradoksga) asoslanishi SHART.
3. BOMBA HOOK (1-SONIYA): Videoning birinchi soniyasidayoq tomoshabin miyasini chalg'itadigan vahimali, absurd yoki o'ta qiziqarli 1 ta qisqa jumla yoz! "Bilasizmi...", "Sizga bitta sir ochaman", "Muvaffaqiyat siri" degan zerikarli, musur so'zlarni UMUMAN ISHLATMA! 
4. VIZUAL SSENARIY (KINO DARAJASIDA): Menga "oldi-qochdi" gaplar yozma! Har bir kunning ssenariysini 2-3 ta gapda shunday tasvirlaki: Kamera qayerdan olyapti? Qahramon yuzida qanday emotsiya? Atrofda qanday harakat va orqa fonda qanday musiqa/ovoz bor? Barchasi aniq, jonli (ko'cha, oshxona, ofis, mashina ichi) bo'lsin.
5. KUCHLI XULOSA: Har bir videoning oxirida tomoshabinni o'ylantirib qo'yadigan yoki daxshatli mantiq orqali kulgidan yiqitadigan, psixologik xulosa bo'lishi shart.

# NATIJANI CHIQARISH FORMATI:
Har bir kun uchun AYNAN SHU STRUKTURA bo'yicha javob ber (Jadval qilib chizma, ro'yxat qilib yoz):

📅 [KUN]: [Videoning jozibali nomi] | Platforma: [Insta / YouTube Shorts / TikTok]
🪝 HOOK: [1-soniyadagi portlovchi jumla]
🎬 SSENARIY: [Kamera rakursi, aniq harakatlar, mimika va ovozlar - batafsil 3 ta gapda]
🧠 XULOSA/MANTIQ: [Tomoshabin oladigan aniq hissiyot yoki mantiqiy yechim]

🔥 Qani ketdik, o'zingdagi butun kreativni ishga sol va menga hech qanday "suvsiz", internetni portlatadigan 20 kunlik jadvalni yaratib ber!"""
    
    # 1. Gemini orqali urinish (agar ishlasa)
    for _ in range(2):
        gemini_key = km.get_gemini_key()
        if not gemini_key: break
        try:
            import google.generativeai as genai
            if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
                del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-3.6-flash")
            response = model.generate_content(prompt)
            if response.text:
                return response.text.strip()
        except Exception:
            continue
            
    # 2. Zaxira sifatida Groq
    for _ in range(3):
        groq_key = km.get_groq_key()
        if not groq_key: break
        try:
            import requests
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
            payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]}
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"].strip()
        except Exception:
            continue
            
    # 3. Zaxira sifatida OpenRouter
    for _ in range(3):
        or_key = km.get_openrouter_key()
        if not or_key: break
        try:
            import requests
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {or_key}", "Content-Type": "application/json"}
            payload = {"model": "google/gemini-2.0-flash-lite-preview-02-05:free", "messages": [{"role": "user", "content": prompt}]}
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"].strip()
        except Exception:
            continue
            
    return None



def get_standard_comment(caption):
    lower_text = str(caption).lower()
    if 'kino kodi' in lower_text or 'kod:' in lower_text or 'kodi:' in lower_text or 'kino:' in lower_text:
        return "🎬 Kino kodi orqali botdan kinoni ko'ring: @TemurbekDevbot"
    return "👇 Fikringizni izohlarda yozib qoldiring!"

def generate_pro_max_scenario(user_prompt):
    km = KeyManager()
    prompt = f"""# SENING ROLING:
Sen neyromarketing, inson psixologiyasi va ijtimoiy tarmoqlar (TikTok/Reels/Shorts) algoritmlari bo'yicha dunyodagi №1 Viral Ssenariynavissan. Sening yagona maqsading — tomoshabin miyasida dofamin ishlab chiqaruvchi, 200% Retention (ko'rilish davomiyligi) ga ega bo'lgan 30 soniyalik ssenariylar yaratish.
Mijoz senga mavzuni yuboradi: "{user_prompt}"

# 🧠 VIRAL PSIXOLOGIYA VA MEXANIKA (QAT'IY QOIDALAR):
1. NEGATIV YOKI ZIDDIYATLI HOOK (0-3 SONIYA): Miyani shokka tushirish uchun "Siz bilishingiz kerak bo'lgan..." degan musur so'zlarni unut! Hook har doim insoniyatning eng og'riqli nuqtasiga urishi, uning xatosini ko'rsatishi yoki qabul qilingan normalarni inkor etishi shart (Masalan: "Buni qilmang!", "Eng katta yolg'on...").
2. PATTERN INTERRUPT (MIYANI CHALG'ITISH): Tomoshabin zerikmasligi uchun kadrda har 3 soniyada vizual yoki audio o'zgarish bo'lishi shart. Ssenariyda buni yoz: (Masalan: Keskin Zoom-in, musiqa birdan to'xtashi, qahramonning jilmaygan yuzdan jiddiy yuzga o'tishi).
3. HARAKAT (ACTION > WORDS): Qahramon shunchaki o'tirib gapirmasin! Ssenariyda harakat yoz: nimadir yeyapti, stolni uryapti, nimanidir otib yuboryapti. Dinamika bo'lishi shart.
4. MANTIQIY PARADOKS (TWIST): Videoning oxirida odamlar kutgan xulosa emas, balki ularning miyasini ostin-ustun qiladigan, mantiqan 100% to'g'ri bo'lgan hayotiy haqiqat (Twist) ochilsin. Ular o'zini ko'rib kulishsin yoki yig'lashsin.
5. SOF O'ZBEK TILI (KIRILMAGAN TIL): Matn kitobiy bo'lmasin. 10 soniyada maksimal 20 ta so'z. Qisqa, keskin, ko'cha tiliga yaqin, tabiiy va zarbli dialoglar yozing. 

# 🎬 CHIQARISH FORMATI (SHU STRUKTURADAN CHIQMA):

[Mavzu]: [Ssenariy nomi] | Xronometraj: 30 soniya

🔥 1-QISM (0:00 - 0:10) - SHOK HOOK VA MUAMMO
👁 Kadr (Dinamika): [Kamera harakati, qahramonning jismoniy harakati, kutilmagan vizual]
🎵 Ovoz/Effekt: [Musiqa boshlanishi, urilish yoki qarsak ovozi]
🗣 Matn: "[15-20 so'z. Qat'iy, ziddiyatli yoki shokka tushiruvchi kirish]"
🤖 AI Video Prompt (Eng): [Runway/Sora uchun toza inglizcha prompt. "Uzbek character, speaking native language, realistic lip movement, cinematic 8k, dynamic movement" shart.]

🔥 2-QISM (0:10 - 0:20) - ZIDDIYAT VA BURILISH
👁 Kadr (Pattern Interrupt): [Kadr keskin o'zgarishi, emotsiya, yaqin rakurs (Zoom)]
🎵 Ovoz/Effekt: [Musiqaning o'zgarishi yoki kutilmagan sukunat (Awkward silence)]
🗣 Matn: "[Vaziyatni chigallashtiruvchi yoki mantiqni o'zgartiruvchi gap]"
🤖 AI Video Prompt (Eng): [Kadrni vizualizatsiya qilish uchun aniq inglizcha prompt]

🔥 3-QISM (0:20 - 0:30) - MANTIQIY NOKAUT (XULOSA)
👁 Kadr (Yechim): [Qahramonning harakati va tomoshabinga qarashi]
🎵 Ovoz/Effekt: [Punchline musiqasi, Bass drop]
🗣 Matn: "[Videoni qayta ko'rishga majbur qiluvchi, kuchli mantiqiy xulosa]"
🤖 AI Video Prompt (Eng): [Oxirgi emotsiyani ko'rsatuvchi inglizcha prompt]

Qoidalar aniq. Ortiqcha gaplarsiz, to'g'ridan-to'g'ri ssenariyni yozishni boshla."""

    # 1. Gemini orqali urinish
    for _ in range(2):
        gemini_key = km.get_gemini_key()
        if not gemini_key: break
        try:
            import google.generativeai as genai
            if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
                del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-3.6-flash") # Ssenariy uchun aqlliroq model kerak
            response = model.generate_content(prompt)
            if response.text:
                return response.text.strip()
        except Exception:
            pass

    # 2. Zaxira Groq
    for _ in range(3):
        groq_key = km.get_groq_key()
        if not groq_key: break
        try:
            import requests
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
            payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]}
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
        except Exception:
            pass

    return "⚠️ Ssenariy yaratishda xatolik yuz berdi. AI serverlari band bo'lishi mumkin."

def generate_comment_reply(comment_text, platform, username):
    km = KeyManager()
    prompt = f"""Sen samimiy, tajribali va do'stona Dasturchi (Temurbek) san. 
Sening {platform} sahifangdagi videoga quyidagi izoh (komment) yozildi.
Foydalanuvchi: {username}
Izoh: "{comment_text}"

QAT'IY QOIDALAR:
1. Izohga o'ta samimiy va xuddi odamdek javob ber. O'zbek tilida yoz.
2. Qisqa va lo'nda bo'lsin (1-2 ta gap).
3. Emojilardan me'yorida foydalan.
4. Hech qanday "Salom, men Temurbekman" deb o'zingni tanishtirma, shunchaki suhbatni davom ettir.
5. Faqat izohning o'zini qaytar, ortiqcha so'zlarsiz.
"""
    
    for _ in range(3):
        gemini_key = km.get_gemini_key()
        if not gemini_key: break
        try:
            import google.generativeai as genai
            if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
                del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-3.6-flash")
            response = model.generate_content(prompt)
            if response.text:
                return response.text.strip().replace('"', '')
        except Exception:
            pass
            
    return "Ajoyib fikr! Rahmat! 😊"
