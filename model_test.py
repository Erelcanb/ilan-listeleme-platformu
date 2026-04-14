import os
import google.generativeai as genai
from dotenv import load_dotenv

# .env dosyasındaki şifremizi yüklüyoruz
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("--- SENİN API ANAHTARINA TANIMLI GOOGLE MODELLERİ ---")
try:
    # Metin üretebilen tüm modelleri listele
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
    print("--------------------------------------------------")
except Exception as e:
    print(f"Modeller çekilirken hata oluştu: {e}")