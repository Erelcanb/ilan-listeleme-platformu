from fastapi import FastAPI
from app.infrastructure.database import engine, Base
from app.infrastructure.scraper import veri_cek_ve_parcala
from app.application.ai_service import ilan_metnini_analiz_et

# Veritabanı tablolarını oluştur (Eğer daha önce oluştuysa dokunmaz)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="İlan Analiz Platformu",
    description="AI Destekli Gayrimenkul ve Vasıta Analiz Sistemi",
    version="1.0.0"
)

@app.get("/")
def ana_sayfa():
    return {
        "durum": "Başarılı", 
        "mesaj": "API çalışıyor. /analiz-et/ ucunu kullanarak test yapabilirsiniz."
    }

@app.get("/analiz-et/")
def analiz_et(url: str):
    """
    1. Belirtilen URL'den ham metni çeker.
    2. Ham metni Gemini AI'ya gönderir.
    3. AI'dan gelen anlamlı veriyi (JSON) döner.
    """
    # 1. Adım: Web sitesine bağlan ve metni çek
    ham_veri = veri_cek_ve_parcala(url)
    
    if ham_veri["durum"] == "başarılı":
        # 2. Adım: Çekilen ham metni yapay zekaya gönder
        analiz_sonucu = ilan_metnini_analiz_et(ham_veri["ham_metin"])
        
        # Sonucu hem AI'dan gelen verilerle hem de orijinal URL ile birleştirip dönelim
        return {
            "islem_durumu": "Tamamlandı",
            "kaynak_url": url,
            "analiz": analiz_sonucu
        }
    
    # Eğer scraper hata alırsa hatayı kullanıcıya göster
    return ham_veri