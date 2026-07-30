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
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.path.dirname(__file__), "service_account.json")
            genai.configure()
            model = genai.GenerativeModel("gemini-3.5-flash")
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
            model = genai.GenerativeModel("gemini-3.5-flash")
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
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.path.dirname(__file__), "service_account.json")
            genai.configure()
            model = genai.GenerativeModel("gemini-3.5-flash")
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

VAZIFA: Menga 30 KUNLIK SUPER-VIRAL, MIYANI PORTLATADIGAN video ssenariylar jadvalini yozib ber. 
Foydalanuvchi ma'lumotlari: {profile_data}
Trendlar: {trend_data}

🔥 QOIDALAR (BUZILMASIN!):
1. 30 KUN UCHUN 30 XIL MAVZU: Takrorlanish qat'iyan taqiqlanadi! Har bir kun uchun men bergan 30 xil yo'nalishdan foydalan!
2. BOMBA HOOK (1-soniya): Tomoshabinni 1-soniyada mixlab qo'yadigan vahimali/sirli 1 ta jumla. (Masalan: "Telefoningiz sizni pinhona eshitishini bilarmidingiz?").
3. 10s SSENARIY (JAMI 15 SO'Z): Faqat: [Harakat] + Ovoz. Qotib qolgan gaplar umuman yo'q! "Haqiqatni bilasizmi", "Qorong'i xona" kabi zerikarli gaplarni QAYTARMA!

Mavzular ro'yxati (Bularni ketma-ket jadvalga qo'y):
1. Supermarketlarning yashirin xiylalari
2. Tana tilidagi 1 soniyalik sir (Manipulyatsiya)
3. Smartfon kamerasining biz bilmagan xavfi
4. Parfyumeriya do'konlarining psixologik siri
5. Boylarning ertalabki maxfiy odati
6. Restoran menyularidagi "narx" qopqoni
7. Yolg'onchini 3 soniyada fosh qilish
8. Instagram algoritmining qora siri
9. O'ta arzon tovarlarning daxshatli siri
10. Samolyot bortkuzatuvchilarining yashirin ishoralari
11. Miyani tez uxlashga majburlash (Harbiy usul)
12. Kasinolarda nima uchun soat yo'q?
13. Wi-Fi orqali sizni qanday kuzatishadi?
14. Kiyim do'konlaridagi oynalarning siri
15. Mashhur brendlarning asl ma'nosi
16. Suyhbatdoshni o'ziga jalb qilishning dark siri
17. Nega hech qachon "Ha" deb javob bermaslik kerak?
18. Muzlatgichdagi mahsulotlarning yashirin muddati
19. Shifokorlar bizga aytmaydigan 1 ta fakt
20. Reklamalardagi muz kubiklarining siri
21. Sizni eshitib turadigan aqlli uylar
22. Zaryadnikni rosetkada qoldirish xavfi
23. Avtosalonlardagi yashirin psixologiya
24. Ish suhbatida HRni aldash usuli
25. 5 soniyada diqqatni jamlash siri
26. Kreditorlarning asosiy tuzog'i
27. Mehmonxonalardagi stakanlarning daxshatli siri
28. TikTok bizning miyamizni qanday o'zgartirdi?
29. Parollarni qanday qilib 1 soniyada buzishadi?
30. Qahva do'konlaridagi yozuvlarning ma'nosi

NAMUNA (Aynan shunday yoz):
| Hafta/Kun | Viral Video Mavzusi | Bomba Hook (1-soniya) | 10s Ssenariy (Harakat + Ovoz) | Format |
| --- | --- | --- | --- | --- |
| 1-kun | Supermarket xiylasi | "Supermarketlar bizni shunday tunaydi!" | [Kadrda: Aravacha g'ildiragi] Ovoz: G'ildirak atayin qiyshiq yasaladi, sekin yurishingiz uchun! | Reels/TikTok |
| 2-kun | Manipulyatsiya | "Odamni 3 soniyada o'qib oling!" | [Kadrda: Yuz ifodalari] Ovoz: Kimdir so'zlashayotganda chap ko'ziga qarang, u kalovlanib qoladi! | Reels/TikTok |

Faqat va faqat to'liq 30 kunlik jadvalni ber! Salomlashish, izoh yozma! Jadvalni NAMUNA kabi batafsil, takrorlamasdan, jozibador yoz!"""
    
    # 1. Gemini orqali urinish (agar ishlasa)
    for _ in range(2):
        gemini_key = km.get_gemini_key()
        if not gemini_key: break
        try:
            import google.generativeai as genai
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.path.dirname(__file__), "service_account.json")
            genai.configure()
            model = genai.GenerativeModel("gemini-1.5-flash")
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
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.path.dirname(__file__), "service_account.json")
            genai.configure()
            model = genai.GenerativeModel("gemini-1.5-pro") # Ssenariy uchun aqlliroq model kerak
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
