import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Gemini Ayarları
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# En sağlam model ismi budur, sürüm numarası eklemeden deneyelim
model = genai.GenerativeModel('gemini-2.5-flash') 

def ilan_metnini_analiz_et(ham_metin: str):
    # Promptu biraz daha sadeleştirelim
    prompt = f"""
    Aşağıdaki metinden şu bilgileri çıkar ve sadece JSON olarak döndür:
    - baslik
    - fiyat
    - ilan_tipi (EMLAK veya VASITA)
    - detaylar (sözlük formatında)

    Metin:
    {ham_metin[:2000]}
    """
    
    try:
        # stream=False ekleyerek yanıtın tek seferde ve tam gelmesini garanti ediyoruz
        response = model.generate_content(prompt)
        
        if not response.text:
            return {"Hata": "AI boş yanıt döndürdü."}
            
        text = response.text
        
        # JSON bloğunu cımbızla çekme işlemi
        if "{" in text:
            start = text.find("{")
            end = text.rfind("}") + 1
            json_text = text[start:end]
            return json.loads(json_text)
        
        return {"Hata": "JSON formatı bulunamadı", "AI_Response": text}
        
    except Exception as e:
        return {"Hata": f"Analiz sırasında bir sorun oluştu: {str(e)}"}