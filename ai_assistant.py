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
    prompt = f"""# VAZIFA VA ROLING:
Sen 2026-yilning eng kuchli, kreativ Ssenariynavisisan. Sening vazifang 20 kunlik HAYOTIY, MANTIQIY va mutlaqo TAKRORLANMAS kontent reja yozish. 

# INPUT (KIRITUVCHI MA'LUMOTLAR):
- Profil yo'nalishi (Mavzu): {profile_data}
- Hozirgi Trendlar: {trend_data}
(Tasodifiy kodi: {random.randint(1000,99999)})

# 🚫 ANTI-LOOP QOIDASI (ENG MUHIM QOIDA):
Men sening eng katta zaifligingni bilaman! Sen bitta shablon tuzib olib, (Masalan: "X ning usuli nima? X ning usuli - X-dir, lekin ba'zilar tushunmaydi") 20 marta faqat so'zlarni o'zgartirib nusxalaysan! 
QAT'IY TAQIQLANADI: 
1. Ikkita kunning ssenariysi yoki gapi bir-biriga 1% ham o'xshamasligi shart!
2. Har bir videoning Hook (ilgak) qismi turli xil hissiyotda boshlansin: 1-kun "Qo'rqinchli", 2-kun "Kulguli savol", 3-kun "Fakt", 4-kun "Kinoya".
3. "Lekin ba'zilar tushunmaydi", "Eng yaxshi usuli" degan shablon so'zlarni UMUMAN ISHLATMA! 

# 🔥 QAT'IY QOIDALAR (BUZILMASIN):
1. FANTASTIKA VA ABSTRAKT YUKLAMALAR TAQIQLANADI. "Hayot bu - yorug'lik", "Sevgi bu - do'stlik" kabi arzon va ma'nosiz falsafani yozma! Ssenariy faqat real voqea (pul yo'qotish, asabiylashish, qimmat narsa sotib olish, do'stni aldash) asosida bo'lsin.
2. HARAKAT KO'RSAT: "Do'sti bilan suhbatlashib..." degan yagona harakatni yig'ishtir! Qahramonlar mashina haydasin, ovqat yoqib yuborsin, telefonda urishsin, kiyim yirtsin. Dinamika ber!

# 💎 MANA SENGA NAMUNA (SHU DARAJADA KREATIV YOZASAN):

[NAMUNA 1 - Iqtisodiy komediya]
📅 KUN 1: "Zal mantiqi" | Platforma: Reels
🪝 HOOK: "O'zbek yigitlarining eng katta yolg'oni qaysi bilasizmi? Dushanbadan yugurish!"
🎬 SSENARIY: Qahvaxona. Yigit maqtanib 3 millionlik VIP sport zal kartasini ko'rsatyapti. Kadr o'zgaradi: 6 oydan keyin o'sha yigit divanda qorni chiqib, chips yeb yotibdi. Do'sti: "6 oyda 2 marta borgansan. Bitta trenirovkang 1.5 millionga tushibdi-da?"
🧠 XULOSA/MANTIQ: Moliyaviy savodxonlik - bu abonoment olib, o'zini sportchidek his qilish emas.

[NAMUNA 2 - Kundalik psixologiya]
📅 KUN 2: "Youtube ustalari" | Platforma: TikTok
🪝 HOOK: "Uydagi oddiy rozetka qanday qilib 2 millionlik xarajatga aylanadi?"
🎬 SSENARIY: Yigit og'zida fonarik tishlab, Youtubedan hindcha videodars orqali tok ulashga urinyapti. Birdan qisqa tutashuv (portlash). Kadr yorishganda yigitning yuzi tutundan qoraygan, sochlari tikka bo'lib qolgan. U erigan simni ko'rsatib: "Asosiysi, usta pulini tejadik!" deydi.
🧠 XULOSA/MANTIQ: O'zbekona g'urur ba'zan cho'ntakka eng katta zarba beradi.

# ENDI SENING NAVBATING:
Yozgan har bir kuningni tekshiraman! Agar yana "Shablon" ishlatsang yoki falsafa sotsang, nol baho olasan. Yuqoridagi 2 ta namuna kabi HAYOTIY, mantiqan kuchli, mutlaqo turli xil harakatlar va ziddiyatlarga boy 20 KUNLIK JADVAL tuz!"""
    
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
    prompt = f"""# VAZIFA VA ROLING (2026-YIL STANDARTI):
Sen 2026-yilgi ijtimoiy tarmoqlar algoritmalarini boshqaruvchi №1 Viral Ssenariynavissan. Maqsading — 200%+ Retention beruvchi, vizual jihatdan 100% REAL VA HAYOTIY bo'lgan viral ssenariylar yaratish.

Mijoz senga mavzu va qismlar sonini yuboradi: "{user_prompt}" (Agar mijoz qismlar sonini yozgan bo'lsa, o'shancha qism yarat. Har bir qism qat'iy 10 soniyadan bo'ladi.)

# 🔥 QAT'IY QOIDALAR (BUZISH UMUMAN TAQIQLANADI):
1. FANTASTIKA VA METAFORAGA O'LIM: "Odamning boshi ochilishi", "Ichki dunyosining ko'rinishi", "Miyadagi yorug'lik", "Qorong'i xona", "gologramma" kabi osmondan olingan, g'alati va fantastik tasvirlarni UMUMAN ISHLATMA! Odamlar ucha olmaydi, boshlar ochilmaydi. Hamma narsa 100% REAL HAYOTDA bo'lishi shart!
2. REAL LOKATSIYA VA OBYEKTLAR: Voqealar faqat oddiy, insoniy joylarda (qahvaxona, ofis, mashina ichi, yotoqxona, ko'cha) bo'lib o'tsin. Qahramonlar faqat real harakatlar qilsin: kofe ho'plash, telefonga asabiy tikilish, rulni urish, kiyim almashtirish, birov bilan yozishish. 
3. PSIXOLOGIYA - BU HARAKAT: Psixologiyani fantastik elementlar bilan emas, insonning harakati va mantiqiy paradoksi bilan ko'rsat! (Masalan: Psixologiya boshning ochilishi emas — psixologiya bu odamning qimmat zalga obuna bo'lib, divanda chips yeb yotishi!). 
4. SOF O'ZBEK TILI (KO'CHA STILI): "Mening ichki dunyom", "Men tushunmadim" kabi robot va Google Translate gaplarini unut! "Brat, miyam qotib qoldi", "Bo'ldi, tamom bo'ldim" kabi tirik insonlar (ko'cha yigitlari) ishlatadigan zarbli, tabiiy gaplarni yoz!
5. 10 SONIYA VA KADR: Har bir qism qat'iy 10 soniya. Kadrlar vizual (kamera yaqinlashishi, odamning reaksiyasi) va ovoz (Musiqa, Bass drop) orqali o'zgaradi.
6. SYUJET YAKKALIGI (CONTINUITY): Barcha qismlar bitta yagona voqeaning davomi bo'lishi shart! 1-qismdagi muammo 2-qismda rivojlanib, oxirgi qismda mantiqiy yechimga kelishi kerak. Qismlar bir-biridan umuman uzilib qolmasin, ular bitta butun kinoning uzviy parchalari kabi bir-biriga 100% mantiqan bog'liq bo'lishi shart!

# 🎬 CHIQARISH FORMATI (SHU STRUKTURADAN CHIQMA):
Mijoz necha qism so'ragan bo'lsa, AYNAN shuncha qism yoz. Har bir qism roppa-rosa 10 soniya!
DIQQAT (AI VIDEO PROMPT QOIDASI): Qahramon yuzi va kiyimi barcha qismlarda 100% bir xil bo'lishi shart! Buning uchun 1-qismda qahramonning tashqi ko'rinishini aniq tasvirlang (masalan: "25-year-old Uzbek man, short dark hair, wearing a black hoodie"). Keyin, xuddi shu tasvirni 2, 3 va qolgan barcha qismlardagi promptlarga xat-buxatisiz ko'chirib o'tkazing! Har bir prompt to'liq mustaqil vizualizatsiya bo'lishi kerak.

🎬 UMUMIY MA'LUMOT
Mavzu: [Ssenariy nomi]
Xronometraj: [Umumiy vaqt]
Qismlar soni: [Masalan, 4 ta]

--- SSENARIY ---

🔥 1-QISM (0:00 - 0:10) - SHOK HOOK
👁 Kadr (Real Life Dynamics): [Aniq, real hayotiy harakat (mashinada, stulda, telefonda) va kamera rakursi]
🎵 Ovoz/Effekt: [Spatial 3D audio, Bass drop, asabiy yurak urishi]
🗣 Matn: "[Maksimal 20-25 so'z. Qat'iy, ziddiyatli kirish]"
🤖 AI Video Prompt (Eng): "[Qahramonning aniq tashqi ko'rinishi: yoshi, jinsi, millati, kiyimi], everyday real life setting, direct audio-driven neural lip-sync, speaking in Uzbek, 16k resolution, perfect temporal consistency. [Bu yerga qolgan REAL kadr harakatini batafsil yozing. No sci-fi]"

🔥 2-QISM (0:10 - 0:20) - RIVOJLANISH / ZIDDIYAT
👁 Kadr (Neural Interrupt): [Kadrning kutilmagan joyga ko'chishi, emotsiya, tezkor Zoom]
🎵 Ovoz/Effekt: [Vakuum sukunati yoki kutilmagan kuchli ovoz]
🗣 Matn: "[Vaziyatni chigallashtiruvchi jumlalar]"
🤖 AI Video Prompt (Eng): "[1-qismdagi qahramonning tashqi ko'rinishini aynan nusxalang], speaking in Uzbek, 16k resolution. [2-qismdagi real vizual va harakatni batafsil yozing. No sci-fi]"

[Mijoz so'rovi bo'yicha oraliq qismlarni har 10 soniya vaqti bilan qo'shib bor. Masalan: 3-QISM (0:20 - 0:30) va hokazo... Har bir qismda AI Video Promptiga 1-qismdagi qahramon ko'rinishini nusxala!]

🔥 OXIRGI QISM - MANTIQIY NOKAUT (XULOSA)
👁 Kadr (Twist yechimi): [Qahramonning harakati va tomoshabinga qarashi, mantiqiy burilish]
🎵 Ovoz/Effekt: [Punchline musiqasi, Phonk yoki to'liq jimjitlik]
🗣 Matn: "[Videoni qayta ko'rishga va do'stga yuborishga majbur qiluvchi, kuchli mantiqiy xulosa]"
🤖 AI Video Prompt (Eng): "[1-qismdagi qahramonning tashqi ko'rinishini aynan nusxalang], speaking in Uzbek, 16k resolution. [Oxirgi shok emotsiyani ko'rsatuvchi real vizual harakat. No sci-fi]"

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
