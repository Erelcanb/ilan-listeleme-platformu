from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.infrastructure.database import engine, Base, SessionLocal
from app.infrastructure.scraper import veri_cek_ve_parcala
from app.application.ai_service import ilan_metnini_analiz_et
from app.infrastructure.repository import ilan_kaydet, ilanlari_getir, ilan_sil, ilan_fiyat_guncelle
import time
from typing import List
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="İlan Analiz Platformu",
    description="AI Destekli Gayrimenkul ve Vasıta Analiz Sistemi",
    version="1.0.0"
)

# Tarayıcıların API'mizle konuşabilmesi için CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Geliştirme aşamasında olduğumuz için herkese izin veriyoruz
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

# Kullanıcının göndereceği toplu link listesinin şeması
class TopluLink(BaseModel):
    urls: List[str]

# Otonom olarak arka planda çalışacak işçi fonksiyonumuz
def arka_plan_isleyicisi(urls: List[str]):
    # Kendi bağımsız veritabanı oturumumuzu açıyoruz
    db = SessionLocal()
    try:
        for url in urls:
            print(f"🔄 İşleniyor: {url}")
            try:
                # 1. Scraper ile veriyi çek (Fonksiyon ismini kendi koduna göre teyit et)
                ham_veri = veri_cek_ve_parcala(url) 
                
                # 2. Gemini AI'a gönder ve analiz et
                analiz_sonucu = ilan_metnini_analiz_et(ham_veri["ham_metin"])
                
                # 3. Veritabanına kaydet
                ilan_kaydet(
                db=db,
                ai_verisi=analiz_sonucu,
                url=url,
                ham_metin=ham_veri["ham_metin"]
            )
                
                print(f"✅ Başarılı, veritabanına kaydedildi: {url}")
            except Exception as e:
                print(f"❌ Hata ({url}): {e}")
            
            # Google API'nin "Dakikada 5 istek" sınırına çarpmamak için sistemi 15 saniye uyutuyoruz
            print("⏳ API sınırı için 15 saniye bekleniyor...\n")
            time.sleep(15)
    finally:
        db.close() # İşlem bitince bağlantıyı güvenle kapat

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

@app.delete("/ilanlar/{ilan_id}")
def ilani_sil(ilan_id: int, db: Session = Depends(get_db)):
    """
    ID'si verilen ilanı veritabanından kalıcı olarak siler.
    """
    basarili_mi = ilan_sil(db=db, ilan_id=ilan_id)
    
    if basarili_mi:
        return {"islem_durumu": "Başarılı", "mesaj": f"ID {ilan_id} numaralı ilan silindi."}
    
    # Eğer ilan bulunamazsa veya silinemezse 404 (Bulunamadı) hatası döndür
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail=f"ID {ilan_id} numaralı ilan bulunamadı.")

@app.patch("/ilanlar/{ilan_id}/fiyat")
def ilanin_fiyatini_guncelle(ilan_id: int, yeni_fiyat: float, db: Session = Depends(get_db)):
    """
    ID'si verilen ilanın fiyatını günceller.
    """
    guncellenen_ilan = ilan_fiyat_guncelle(db=db, ilan_id=ilan_id, yeni_fiyat=yeni_fiyat)
    
    if guncellenen_ilan:
        return {
            "islem_durumu": "Başarılı", 
            "mesaj": f"ID {ilan_id} numaralı ilanın fiyatı {yeni_fiyat} olarak güncellendi."
        }
    
    raise HTTPException(status_code=404, detail=f"ID {ilan_id} numaralı ilan bulunamadı veya güncellenemedi.")

@app.post("/toplu-analiz/")
def toplu_analiz_baslat(veriler: TopluLink, arka_plan: BackgroundTasks):
    """
    Birden fazla ilan linkini alır ve arka planda sırayla işlemek üzere kuyruğa ekler.
    """
    # Görevi arka plana devret
    arka_plan.add_task(arka_plan_isleyicisi, veriler.urls)
    
    # Kullanıcıyı bekletmeden hemen cevap dön
    return {
        "islem_durumu": "Otonom Sistem Devrede", 
        "mesaj": f"{len(veriler.urls)} adet link kuyruğa eklendi. Sistem bunları arka planda 15'er saniye aralıklarla analiz edip kaydedecek."
    }