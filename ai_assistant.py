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
        
        self.current_groq_index = 0
        self.current_gemini_index = 0
        self.current_or_index = 0
        
    def get_gemini_key(self):
        if self.keys.get("gemini") and len(self.keys["gemini"]) > 0:
            key = self.keys["gemini"][self.current_gemini_index]
            self.current_gemini_index = (self.current_gemini_index + 1) % len(self.keys["gemini"])
            return key
        return os.getenv("GEMINI_API_KEY")

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
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
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
    
    prompt = f"""Sen O'zbekistondagi eng zo'r SMM va YouTube mutaxassisisan.
Mijozingning YouTube va Instagram kanallari bo'yicha quyidagi statistika keldi:
{json.dumps(stats_data, indent=2)}

Vazifang:
1. Kechagi kunga, o'tgan haftaga va o'tgan oyga (mavjud ma'lumotlarga qarab) nisbatan qanchalik o'sish (yoki tushish) bo'lganini hisoblab, chiroyli qilib tushuntir.
2. Ikkala tarmoqni (YouTube va Instagram) alohida tahlil qil. Quruq raqamlar emas, inson o'qiydigan chiroyli tilda yoz.
3. Mijozga motivatsiya ber va kelajak uchun bitta foydali, kreativ SMM maslahat qoldir.
4. Javobingni chiroyli emojilar bilan, sof O'zbek tilida (kirill yozuvidan qochib, lotinda) yoz.
5. Juda uzun emas, o'qishga qulay qilib yoz. Qalin shrift (bold) qilish uchun ** (yulduzcha) ISHLATMA, uning o'rniga HTML <b> va </b> taglaridan foydalan!
"""
    
    for _ in range(3):
        gemini_key = km.get_gemini_key()
        if not gemini_key: break
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
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
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
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
    km = KeyManager()
    prompt = f"""Sen O'zbekistondagi eng mashhur va kreativ SMM prodyusersan (TikTok/Reels bo'yicha millionlik ekspert).

Quyida ma'lumotlar:
1. FOYDALANUVCHI FAKTLARI:
{profile_data}

2. GLOBAL TRENDLAR:
{trend_data}

VAZIFA:
Shunga asoslanib kelgusi 30 kun uchun 💥 VIRAL VIDEO G'OYALARI jadvalini tuz.

DIQQAT - ENG MUHIM QOIDALAR:
1. Bu videolar rostdan ham 10 SONIYALIK bo'lishi shart. Ssenariy JAMI 20 TA SO'ZDAN oshmasligi qat'iyan talab qilinadi!
2. FAKAT TEXNOLOGIYA EMAS! Mavzular butunlay OMMABOP, KULGILI, PSIXOLOGIK yoki hayotiy trendlar bo'lsin. Masalan: "Yolg'onchini ko'zidan bilib olish", "Odamni tez uxlab qolish siri", "Erkaklar va Ayollar o'rtasidagi kulgili farq", "Hech qachon qilinmasligi kerak bo'lgan 3 ta ish". Dasturlashni umuman aralashtirma!
3. HOOK: 1-soniyada uradigan, qisqa va vahimali bo'lsin. (Masalan: "Zaryadingiz tez tugayaptimi?!", "Bu saytni hech kim bilmaydi!").
4. [10 Soniyalik Ssenariy] qismi: Faqat 2 ta qadamdan iborat bo'lsin. 1. Muallif bitta jumla gapiradi. 2. Ekranda harakat ko'rsatiladi. Hammasi jami 15-20 so'zdan iborat bo'lsin.
5. Hech qanday inglizcha qotib qolgan tarjimalar yoki uzun salomlashishlar kerak emas. "Salom do'stlar" degan gapni UCHIRIB TASHLA.

Jadval ustunlari: [Hafta/Kun] | [Viral Video Mavzusi] | [Bomba Hook (1-soniya)] | [10s Ssenariy (Max 20 so'z)] | [Format]

Javobing to'g'ridan-to'g'ri jadval bilan boshlansin, keraksiz kirish so'zlari yozma."""
    
    # 1. Gemini orqali urinish (Foydalanuvchi talabi)
    for _ in range(3):
        gemini_key = km.get_gemini_key()
        if not gemini_key: break
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
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
                return response.json()["choices"][0]["message"]["content"].strip()
        except Exception:
            continue
    return None



def get_standard_comment(caption):
    lower_text = str(caption).lower()
    if 'kino kodi' in lower_text or 'kod:' in lower_text or 'kodi:' in lower_text or 'kino:' in lower_text:
        return "🎬 Kino kodi orqali botdan kinoni ko'ring: @TemurbekDevbot"
    return "👇 Fikringizni izohlarda yozib qoldiring!"
