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
    prompt = f"Sen O'zbekistondagi eng mashhur SMM kopiraytersan. Senga bitta video haqida ma'lumot (video summary) beraman. Shundan kelib chiqib Instagram va YouTube Shorts uchun odamlarni o'ziga tortadigan, e'tiborni ushlab qoladigan va oxirida savol bilan tugaydigan zo'r o'zbekcha ssenariy/caption yozib ber. DIQQAT: Hech qanday HASHTAG (#) ishlatma! Buni tizim o'zi qoshadi. Faqat toza matn yoz.\n\nVideo ma'lumoti:\n{summary}"
    
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
    prompt = f"Sen O'zbekistondagi juda kreativ SMM ekpertsan. Senga bitta video haqida ma'lumot (video summary) beraman. Qisqa, odamni o'ylantiradigan, falsafiy yoki qiziqarli yondashuv bilan caption yozib ber. DIQQAT: Hech qanday HASHTAG (#) ishlatma! Tizim o'zi qo'shadi. Faqat toza matn yoz.\n\nVideo ma'lumoti:\n{summary}"
    
    for _ in range(3):
        or_key = km.get_openrouter_key()
        if not or_key: break
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {or_key}", "Content-Type": "application/json"}
            payload = {"model": "google/gemma-4-31b-it:free", "messages": [{"role": "user", "content": prompt}]}
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
        except Exception:
            continue
    return None

import random

def append_viral_hashtags(caption):
    # O'zbekistondagi eng kuchli blogerlar va IT sohasidagilar ishlatadigan viral hashteglar
    general_viral = ["#rek", "#rekka", "#uzbekistan", "#toshkent", "#trend", "#qiziqarli", "#uzbek", "#foydali"]
    niche_tech = ["#dasturlash", "#dasturchi", "#ituz", "#biznes", "#rivojlanish", "#motivatsiya", "#smm"]
    ai_tags = ["#sunniyintellekt", "#aiuz", "#ai"]
    
    # Aralashtirib tanlab olish: 3 ta umumiy, 2 ta tech, 1 ta AI
    selected_tags = random.sample(general_viral, 3) + random.sample(niche_tech, 2) + random.sample(ai_tags, 1)
    
    # Har doim mualliflik hashtegi
    selected_tags.append("#temurbekdev")
    
    # Matn ichida agar hashtaglar qolib ketgan bo'lsa (AI baribir yozib qo'ygan bo'lsa) tozalaymiz
    clean_caption = "\n".join([line for line in caption.split("\n") if not line.strip().startswith("#")])
    
    return clean_caption.strip() + "\n\n" + " ".join(selected_tags)

def generate_data_driven_strategy(profile_data, trend_data):
    km = KeyManager()
    prompt = f"""Sen O'zbekistondagi eng mashhur va kreativ SMM prodyusersan (TikTok va Reels bo'yicha ekspert). Foydalanuvchining kanali IT, Dasturlash, Sun'iy Intellekt va Texnologiyalarga bag'ishlangan (#temurbekdev).

Quyida ikkita ma'lumot beriladi:
1. FOYDALANUVCHINING O'Z PROFILI FAKTLARI:
{profile_data}

2. GLOBAL INSTAGRAM TRENDLARI:
{trend_data}

VAZIFA:
Shu ma'lumotlarga asoslanib kelgusi 30 kun uchun (jami 12-15 ta) 💥 VIRAL VIDEO G'OYALARI jadvalini tuz.

DIQQAT - ENG MUHIM QOIDALAR:
1. Bu videolar rostdan ham 10 SONIYALIK TikTok/Reels bo'lishi shart. Ssenariydagi hamma gaplar qo'shilib JAMI 20 TA SO'ZDAN oshmasligi qat'iyan talab qilinadi! (Odamlar tez skroll qiladi).
2. Mavzular dasturchilar uchun emas, 100% ODDIY ODAMLAR uchun (ommabop) bo'lsin: "Zaryadni 2 kunga yetkazish", "Internetni tezlashtirish", "Birovni telefonini tekshirish siri", "Yashirin AI saytlar". Falsafa va dasturlash haqida umuman yozma.
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

