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
    prompt = f"""Sen O'zbekistondagi eng qimmat va kuchli "Dark SMM" va Viral-Video prodyusersan. 

(Tasodifiy generatsiya kodi: {random.randint(1000,99999)} / Vaqt: {time.time()})

VAZIFA: Menga 20 KUNLIK SUPER-VIRAL, MIYANI PORTLATADIGAN batafsil video ssenariylar jadvalini yozib ber. 
Foydalanuvchi ma'lumotlari (profil yo'nalishi): {profile_data}
Hozirgi Trendlar (Insta, YouTube, FB): {trend_data}

🔥 QOIDALAR (PRO +++MAX QOIDASI):
1. 20 KUN UCHUN 20 TA MUTLAQO HAR XIL MAVZU: Hech qachon bir xil mavzuni qayta-qayta yozib, siklga tushib qolma! 20 kunning har biri bir-biridan 100% mutlaqo farq qiladigan g'oyalar bo'lishi SHART! 
2. ERKAKLAR PSIXOLOGIYASI VA ABSURD: Ssenariylarga dark psixologiya, pul ishlash sirlari, xavfli manipulyatsiyalar, do'stlik (bro-culture) va epik kutilmagan vaziyatlarni (plot twist) qo'sh!
3. BOMBA HOOK (1-soniya): Tomoshabinning miyasini chalg'itadigan vahimali yoki jozibali 1 ta qisqa jumla. Oddiy gaplashish bo'lmasin!
4. BATAFSIL SSENARIY VA MATN XILMAXILLIGI: Har bir kunning ssenariysini juda batafsil qilib 2-3 ta gapda yozib ber (kamera qayerdan keladi, odam qanday harakat qiladi, qanday ovoz eshitiladi). Hech qachon "X haqiqati" kabi axmoqona shablonlarni umuman ishlatma! Qandaydir mavhum "ramzlar" emas, balki jonli, real harakatlar (ko'cha, ofis, mashina, janjal) tasvirlansin.
5. XULOSA/MA'NO: Har bir video tomoshabinga qanday yashirin ma'no yoki hissiyot berishi kerakligini qisqacha qo'sh.
6. PLATFORMALAR: Instagram, YouTube, Facebook uchun eng mos formatlarni aralashtirib yoz.

NAMUNA (Aynan shu jadval formatida yoz):
| Hafta/Kun | Viral Video Mavzusi | Bomba Hook (1-soniya) | Batafsil Ssenariy (Kadrlar + Ovoz) | Xulosa/Ma'no | Format |
| --- | --- | --- | --- | --- | --- |
| 1-kun | Do'stlik siri (Bro-Code) | "Haqiqiy do'st senga yordam bermaydi..." | [Kadr: Qorong'i sportzal. Yigit katta og'irlik ko'tarolmay qiynalyapti. Sherigi yordam berish o'rniga uning qulog'iga nimadir pichirlaydi. Yigitning ko'zlari kattalashib, shtangani osmonga otib yuboradi!] Ovoz: Sekin boshlanib, portlovchi Phonk musiqasi. | Tomoshabinda g'azab aralash ulkan motivatsiya uyg'onadi. | Instagram Reels |
| 2-kun | Ko'rinmas qopqon (Xavf)| "Biz komfort zonaga keldik. Endi orqaga qaytamiz!" | [Kadr: Yomg'irli tungi trassa. Mashina katta tezlikda ketyapti. Birdan haydovchi keskin tormoz beradi va rulni qayirib, mashinani orqaga uchiradi.] Ovoz: Shinalar chirillashi, kuchli yurak urishi. | Komfort zonaning aslida qanchalik xavfli ekanligini anglash. | YouTube Shorts |

DIQQAT ENGIN ENG MUHIM QOIDA: Namunadagi "Do'stlik siri" va "Ko'rinmas qopqon" mavzularini UMMUMAN jadvalga qo'shma!!! Ular faqat men senga tushuntirishim uchun yozilgan misol! Sen 1-kundan boshlab o'zingning 20 ta mutlaqo yangi, takrorlanmas ssenariylaringni yozasan! Hech qanday shablonlarsiz! Faqat jadvalni qaytar!"""
    
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
    prompt = f"""Sen jahon darajasidagi, gollivud uslubida fikrlaydigan "Pro+++ Max Viral Max" video ssenaristisan.
Mijoz senga mavzu va qismlar sonini yubordi: "{user_prompt}"

QAT'IY QOIDALAR (BUZILISHI MUMKIN EMAS):
1. ZERIKARLI BO'LMASIN: Hech qachon oddiy, zerikarli yoki standart internet ssenariylarini berma. Ssenariylar odamning miyasini chalg'itadigan, 200% retention (kutish) beradigan darajada "Pro +++Max" bo'lishi shart!
2. BRO-CULTURE & PSIXOLOGIYA: Ssenariylarga erkaklar psixologiyasi, do'stlik (bro-culture), motivatsiya va epik absurd vaziyatlarni (masalan: 2-3 kishi ishtirokidagi syujetli burilishlar, kutilmagan dark psixologiya fokuslari) qo'sh! (Masalan: Boy ko'ringanlar aslida kambag'al chiqishi yoki ziddiyatli holat).
3. 10 SONIYA QOIDASI: Har bir qism ROPPA-ROSA 10 soniyalik bo'lishi shart. Agar mijoz "3 qism" degan bo'lsa, umumiy video 30 soniya bo'ladi.
4. MATN HAJMI: 10 soniya ichiga ko'pi bilan 20-25 ta so'z sig'adi. "Diktor/Matn" qismi QAT'IYAN 25 ta so'zdan oshmasligi kerak! 
5. KADRLAR ALMASHUVI VA OVOZ: Ovoz effektlariga (Phonk musiqa, Bass drop, yurak urishi, sukunat) va kadrlar tili (Whip pan, slow-mo, 0.5x burchak) ga alohida urg'u ber. Har bir kadr o'quvchini shok holatga tushirishi kerak.

FORMAT (Shu formatdan mutlaqo chetga chiqma):
🎬 UMUMIY MA'LUMOT
Mavzu: [Mavzu]
Umumiy vaqt: [Masalan, 30 soniya]

--- QISMLAR ---

🔥 1-QISM (0:00 - 0:10) - HOOK
👁 Kadr (Vizual): [Absurd vaziyat, kutilmagan holat, kamera harakatlari]
🎵 Ovoz: [Musiqa, Bass drop yoki ovoz effektlari]
🗣 Yozuv/Diktor (Max 25 so'z): "[Diqqatni tortuvchi so'zlar]"

🔥 2-QISM (0:10 - 0:20) - BURILISH (TWIST)
👁 Kadr (Vizual): [Shok qiluvchi burilish, syujetning kutilmagan tomonga ketishi]
🎵 Ovoz: [Musiqa effekti o'zgarishi]
🗣 Yozuv/Diktor: "[Matn]"

(va hokazo, so'ralgan qismlar soniga qarab davom eting).

Javobing to'g'ridan-to'g'ri ssenariy bilan boshlanishi kerak, ortiqcha gaplarsiz!"""

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
