from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.infrastructure.database import engine, Base, SessionLocal
from app.infrastructure.scraper import veri_cek_ve_parcala
from app.application.ai_service import ilan_metnini_analiz_et
from app.infrastructure.repository import ilan_kaydet, ilanlari_getir

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="İlan Analiz Platformu",
    description="AI Destekli Gayrimenkul ve Vasıta Analiz Sistemi",
    version="1.0.0"
)

# Her bir istek geldiğinde veritabanı kapısını açıp, işlem bitince kapatan fonksiyon
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def ana_sayfa():
    return {"durum": "Başarılı", "mesaj": "API çalışıyor."}

# Depends(get_db) ile FastAPI'ye "Bana bir veritabanı oturumu ver" diyoruz
@app.get("/analiz-et/")
def analiz_et(url: str, db: Session = Depends(get_db)):
    """
    1. Metni çeker
    2. AI ile analiz eder
    3. Sonucu veritabanına kaydeder!
    """
    # 1. Adım: Veriyi çek
    ham_veri = veri_cek_ve_parcala(url)
    
    if ham_veri["durum"] == "başarılı":
        # 2. Adım: Yapay Zekaya Gönder
        analiz_sonucu = ilan_metnini_analiz_et(ham_veri["ham_metin"])
        
        # Eğer AI bir JSON (sözlük) döndürdüyse kayıt işlemine geç
        if isinstance(analiz_sonucu, dict) and "Hata" not in analiz_sonucu:
            
            # 3. Adım: Veritabanına Kaydet
            kayit_sonucu = ilan_kaydet(
                db=db,
                ai_verisi=analiz_sonucu,
                url=url,
                ham_metin=ham_veri["ham_metin"]
            )
            
            return {
                "islem_durumu": "Tamamlandı",
                "veritabani": kayit_sonucu,
                "analiz": analiz_sonucu
            }
        
        return {"islem_durumu": "AI Hatası", "detay": analiz_sonucu}
    
    return ham_veri

@app.get("/ilanlar/")
def ilanlari_listele(ilan_tipi: str = None, max_fiyat: float = None, db: Session = Depends(get_db)):
    """
    Veritabanına kaydedilmiş ilanları listeler.
    Filtreleme için 'ilan_tipi' (EMLAK/VASITA) ve 'max_fiyat' kullanılabilir.
    """
    ilanlar = ilanlari_getir(db, ilan_tipi=ilan_tipi, max_fiyat=max_fiyat)
    
    return {
        "islem_durumu": "Başarılı",
        "toplam_sonuc": len(ilanlar),
        "ilanlar": ilanlar
    }