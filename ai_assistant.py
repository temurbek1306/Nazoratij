import os
import json
import random
import requests

def _call_gemini(api_key, prompt, model_name="gemini-2.5-flash"):
    """
    Yangi google.genai SDK orqali Gemini API ga so'rov yuborish.
    Eski google.generativeai deprecated bo'lgani uchun, AQ. formatdagi
    yangi API kalitlarni qo'llab-quvvatlaydigan google.genai ishlatamiz.
    """
    try:
        from google import genai
        
        if api_key == "SERVICE_ACCOUNT_AUTH":
            # Service Account orqali Vertex AI backend
            sa_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "service_account.json")
            if os.path.exists(sa_file):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = sa_file
                # Service Account bilan project_id kerak
                with open(sa_file, "r") as f:
                    sa_data = json.load(f)
                project_id = sa_data.get("project_id", "")
                client = genai.Client(vertexai=True, project=project_id, location="us-central1")
            else:
                return None
        else:
            client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        if response and response.text:
            return response.text
    except Exception as e:
        print(f"[Gemini Error ({model_name})]: {e}")
    return None

def _call_openrouter(api_key, prompt, model_name="openrouter/free"):
    """
    OpenRouter API orqali so'rov yuborish.
    Asosiy prioritet qilib qo'yildi.
    """
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
        else:
            print(f"[OpenRouter Status Error]: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[OpenRouter Exception]: {e}")
    return None

def _call_groq(api_key, prompt, model_name="llama-3.3-70b-versatile"):
    """
    Groq API orqali so'rov yuborish.
    """
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
        else:
            print(f"[Groq Status Error]: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[Groq Exception]: {e}")
    return None

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
    
    # 1-Urinish: OpenRouter (Asosiy)
    for _ in range(3):
        or_key = km.get_openrouter_key()
        if not or_key: break
        result = _call_openrouter(or_key, full_prompt)
        if result:
            return "🌐 [OpenRouter AI]:\n\n" + result

    # 2-Urinish: Groq
    for _ in range(3):
        groq_key = km.get_groq_key()
        if not groq_key: break
        result = _call_groq(groq_key, full_prompt)
        if result:
            return "⚡️ [Groq AI]:\n\n" + result

    # 3-Urinish: Gemini
    for _ in range(3):
        gemini_key = km.get_gemini_key()
        if not gemini_key: break
        result = _call_gemini(gemini_key, full_prompt)
        if result:
            return "✨ [Gemini AI]:\n\n" + result
            
    return "⚠️ Kechirasiz, barcha AI serverlari (Groq, OpenRouter, Gemini) hozircha band yoki API limitga tushdi."

def generate_caption_groq(summary):
    km = KeyManager()
    prompt = f"Sen O'zbekistondagi kreativ SMM ekpertsan. Quyida videoning chuqur tahlili (summary) berilgan. Buni diqqat bilan o'qi: \n\n{summary}\n\nVAZIFA: Aynan shu voqea, harakat va yozuvlarga 100% mos keladigan, videodan uzilib qolmagan Instagram post matnini (caption) yoz! Umumiy, hamma videoga tushadigan shablon gaplarni YOZMA. Kulgili, kinoyali yoki kreativ yondashuv qil. Oxirida odamlarni fikr bildirishga, LIKE bosishga va profilingizga OBUNA BO'LISHGA undovchi kreativ chaqiriq (Call to Action) qo'sh. DIQQAT: Hech qanday HASHTAG (#) ishlatma! Faqat toza matn yoz."
    
    for _ in range(3):
        groq_key = km.get_groq_key()
        if not groq_key: break
        result = _call_groq(groq_key, prompt)
        if result:
            return result.strip()
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
            payload = {"model": "openrouter/free", "messages": [{"role": "user", "content": prompt}]}
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
    
    # 1-Urinish: OpenRouter
    for _ in range(3):
        or_key = km.get_openrouter_key()
        if not or_key: break
        result = _call_openrouter(or_key, prompt)
        if result:
            import re
            return re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', result.strip())

    # 2-Urinish: Groq
    for _ in range(3):
        groq_key = km.get_groq_key()
        if not groq_key: break
        result = _call_groq(groq_key, prompt)
        if result:
            import re
            return re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', result.strip())

    # 3-Urinish: Gemini
    for _ in range(3):
        gemini_key = km.get_gemini_key()
        if not gemini_key: break
        result = _call_gemini(gemini_key, prompt)
        if result:
            import re
            return re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', result)
            
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
    # 1. OpenRouter
    for _ in range(3):
        or_key = km.get_openrouter_key()
        if not or_key: break
        result = _call_openrouter(or_key, prompt)
        if result:
            first_comment = result.strip().replace('"', '')
            break

    if not first_comment:
        # 2. Groq
        for _ in range(3):
            groq_key = km.get_groq_key()
            if not groq_key: break
            result = _call_groq(groq_key, prompt)
            if result:
                first_comment = result.strip().replace('"', '')
                break
            
    if not first_comment:
        # 3. Gemini
        for _ in range(3):
            gemini_key = km.get_gemini_key()
            if not gemini_key: break
            result = _call_gemini(gemini_key, prompt)
            if result:
                first_comment = result.strip().replace('"', '')
                break
                
    if not first_comment:
        first_comment = "Videodagi holat kimga tanish? 😂 Fikringizni yozib qoldiring 👇"
        
    return first_comment

def generate_data_driven_strategy(profile_data, trend_data):
    """
    Kontent reja generatori (Static-First + AI-Fallback arxitekturasi).
    
    MANTIQ:
    1. AVVAL: Loyihadagi tayyor 20 kunlik ssenariylar faylidan random 5 tasini oladi.
       (Bu ssenariylar qo'lda yozilgan, 100% sifatli va o'zbek mentalitetiga mos)
    2. FAQAT FAYL TOPILMASA: AI modeliga murojaat qiladi (hardened prompt bilan).
    """
    import random
    import time
    import re
    
    # ===== 1-BOSQICH: STATIK MA'LUMOTLAR BAZASIDAN OLISH (ASOSIY MANBA) =====
    try:
        scenarios_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "20_kunlik_viral_ssenariylar.md")
        if os.path.exists(scenarios_file):
            with open(scenarios_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Faylni "### 📅 KUN" bloklari bo'yicha bo'laklarga ajratish
            blocks = re.split(r'(?=### 📅 KUN \d+)', content)
            scenario_blocks = [b.strip() for b in blocks if b.strip().startswith("### 📅 KUN")]
            
            if len(scenario_blocks) >= 5:
                # 20 ta ichidan random 5 tasini tanlash
                selected = random.sample(scenario_blocks, min(5, len(scenario_blocks)))
                
                # Yangi kun raqamlarini berish (1-5)
                result_lines = []
                result_lines.append("# 🔥 5 KUNLIK VIRAL KONTENT REJANGIZ")
                result_lines.append(f"*(Profil: {profile_data} | Trend: {trend_data})*\n")
                result_lines.append("---\n")
                
                for i, block in enumerate(selected, 1):
                    # Eski kun raqamini yangisiga almashtirish
                    reformatted = re.sub(
                        r'### 📅 KUN \d+:',
                        f'### 📅 KUN {i}:',
                        block,
                        count=1
                    )
                    result_lines.append(reformatted)
                    result_lines.append("")  # Bo'sh qator
                
                result_lines.append("---")
                result_lines.append("*Har bir ssenariy real hayotdagi mantiqiy paradokslar ustiga qurilgan.*")
                
                return "\n".join(result_lines)
    except Exception:
        pass  # Fayl bilan muammo bo'lsa, AI ga o'tamiz
    
    # ===== 2-BOSQICH: AI FALLBACK (faqat fayl topilmaganda) =====
    km = KeyManager()
    prompt = f"""# VAZIFA VA ROLING:
Sen axloq darsi o'tadigan o'qituvchi emassan! Sen asabiy, reallikni boricha (achchiq va kulguli qilib) ko'rsatadigan "Stand-up" komiki va Gollivud darajasidagi ssenaristsan. Sening vazifang 5 kunlik HAYOTIY, MANTIQIY va mutlaqo TAKRORLANMAS kontent reja yozish.

# INPUT:
- Profil yo'nalishi: {profile_data}
- Hozirgi Trendlar: {trend_data}
(Tasodifiy kodi: {random.randint(1000,99999)})

# 🚫 TAQIQLANGAN SO'ZLAR (BAN LIST — BIRONTASINI HAM ISHLATSANG, VAZIFA BARBOD):
- "Hayotning ma'nosi", "Qaror qabul qilish", "Pulni boshqarish", "Sevgi bu..."
- "Ular buni anglab yetishadi", "Muhim rol o'ynaydi", "Tushunish kerak"
- "Lekin ba'zilar tushunmaydi", "Eng yaxshi usuli", "Eshitingiz bor bormi"
- "Absurdiy qarorlar", "Asabiyati keskin kesiladi" — bu robot tarjimalar!
INSHO YOZISHNI EMAS, HAYOTIY KOMEDIYA/FOJIA YOZISHNI BUYURYAPMAN!

# 🚫 TIL QOIDALARI:
1. SOF O'ZBEK TILI: 100% toza, grammatik xatosiz o'zbek tilida yoz. Google Translate tarjimalari TAQIQLANADI!
2. ABSURD MANTIQSIZLIK TAQIQLANADI: Osmondan olingan jinniliklarni yozma! Faqat real hayotdagi oddiy muammolar (taksi kutish, qarz, telefon qaramlik).
3. KINOYA = PICHING/IRONIYA/SARKAZM, KINOYA ≠ KINOTEATR!!! Buni chalkashtirsang, vazifani barbod qilasan.

# 🔥 SSENARIY QOIDALARI:
1. Hooklar: 1-kun "Qo'rqinchli", 2-kun "Kulguli", 3-kun "Fakt", 4-kun "Kinoya (piching)", 5-kun "Absurd savol".
2. Xulosa hech qachon axloq darsi bo'lmasin — faqat qora yumor yoki kinoya (piching)!
3. HARAKAT: Qahramonlar jismoniy harakat qilsin (telefonga asabiy qarash, kofe to'kish, mashina eshigini urish).

# 💎 NAMUNALAR (AYNAN SHU DARAJADA, SHU TILDA YOZASAN):

📅 KUN 1: "Budilnik Illyuziyasi" | Platforma: Reels
🪝 HOOK: "Nega biz o'zimizga-o'zimiz ataylab yolg'on gapirishni yaxshi ko'ramiz?"
🎬 SSENARIY: Yotoqxona. Yigit uxlashdan oldin telefonida budilniklarni sozlayapti: 06:00, 06:05, 06:10. Yuzida "ertaga tog'larni talqon qilaman" degan jiddiy ishonch. Kadr keskin o'zgaradi: Tonggi soat 07:45. Yigit ko'zini ochib soatga qaraydi va panikada bitta paypog'ini topolmay, xona bo'ylab sakrab yugurishni boshlaydi.
🧠 XULOSA/MANTIQ: Biz 10 ta budilnikni barvaqt uyg'onish uchun emas, vijdonimizni tinchlantirib xotirjam uxlash uchun qo'yamiz.

📅 KUN 2: "Mashina va G'urur (GPS)" | Platforma: YouTube Shorts
🪝 HOOK: "Erkak kishining g'ururi qachon o'zining eng yuqori cho'qqisiga chiqadi?"
🎬 SSENARIY: Mashina ichida. GPS navigator robot ovozida: "O'ngga buriling, manzilga 5 daqiqa qoldi" deydi. Yigit jiddiy qiyofada navigatorga qarab: "Sen nimaniyam bilarding" deydi-da, rulni keskin chapga buradi. Kadr o'zgaradi: Mashina qorong'i, yopiq tupikka tiqilib qolgan. Yigit rulni urib, "Shu internet umuman yaxshi ishlamayapti-da o'zi!" deb nosozlikni ayblaydi.
🧠 XULOSA/MANTIQ: Erkak kishi o'z xatosini tan olgandan ko'ra, butun koinot va zamonaviy texnologiyalarni ayblashni afzal ko'radi.

📅 KUN 3: "Xolodilnik Fojiasi" | Platforma: Shorts
🪝 HOOK: "Miyamizdagi mo'jizaga bo'lgan yashirin ishonchni qayerda ko'rish mumkin?"
🎬 SSENARIY: Kechqurun. Yigit qornini ushlab xolodilnikni ochadi: Ichida yarimta qatiq va piyoz bor xolos. Xafsalasiz yopadi. 5 daqiqadan so'ng u qaytib kelib xolodilnikni yana ochadi (xuddi ichida o'z-o'zidan qovurilgan go'sht paydo bo'lib qoladigandek). U bu ishni yana 3 marta takrorlaydi, umidvor nigoh bilan.
🧠 XULOSA/MANTIQ: Umid so'nggi bo'lib o'ladi... Ayniqsa gap qorin ochligi va xolodilnik haqida ketganda.

# ENDI SENING NAVBATING:
Yuqoridagi 3 ta NAMUNANI diqqat bilan o'rgandingmi? AYNAN shu stilda, shu sifatda va shu toza tilda 5 KUNLIK mutlaqo har xil ssenariylar yoz! Agar yana "asabiyati kesildi" yoki "kinoga borganlar" degan ahmoqlik yozsang — nol baho olasan!"""
    
    # 2a. OpenRouter orqali
    for _ in range(3):
        or_key = km.get_openrouter_key()
        if not or_key: break
        result = _call_openrouter(or_key, prompt)
        if result:
            return result.strip()
            
    # 2b. Groq orqali
    for _ in range(3):
        groq_key = km.get_groq_key()
        if not groq_key: break
        result = _call_groq(groq_key, prompt)
        if result:
            return result.strip()
            
    # 2c. Zaxira sifatida Gemini
    for _ in range(2):
        gemini_key = km.get_gemini_key()
        if not gemini_key: break
        result = _call_gemini(gemini_key, prompt, model_name="gemini-2.5-flash")
        if result:
            return result.strip()
            
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

    # 1. OpenRouter
    for _ in range(3):
        or_key = km.get_openrouter_key()
        if not or_key: break
        result = _call_openrouter(or_key, prompt)
        if result:
            return result.strip()

    # 2. Groq
    for _ in range(3):
        groq_key = km.get_groq_key()
        if not groq_key: break
        result = _call_groq(groq_key, prompt)
        if result:
            return result.strip()

    # 3. Zaxira Gemini
    for _ in range(2):
        gemini_key = km.get_gemini_key()
        if not gemini_key: break
        result = _call_gemini(gemini_key, prompt, model_name="gemini-2.5-flash")
        if result:
            return result.strip()

    return "⚠️ Ssenariy yaratishda xatolik yuz berdi. AI serverlari band bo'lishi mumkin."

def generate_comment_reply(comment_text, platform, username):
    return "Ajoyib fikr, bizga obuna bo'ling!"
