from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.infrastructure.orm_models import IlanORM
from app.domain.models import IlanTipi

def ilan_kaydet(db: Session, ai_verisi: dict, url: str, ham_metin: str):
    """
    Yapay zekadan gelen temizlenmiş veriyi veritabanına kaydeder.
    """
    try:
        # 1. Aynı link daha önce kaydedilmiş mi kontrol et (unique=True kuralı için)
        mevcut_ilan = db.query(IlanORM).filter(IlanORM.link == url).first()
        if mevcut_ilan:
            return {"kayit_durumu": "Atlandı", "mesaj": "Bu ilan zaten veritabanında mevcut."}

        # 2. Fiyatı güvenli bir şekilde ondalıklı sayıya (Float) çevir
        fiyat_str = ai_verisi.get("fiyat")
        fiyat_float = 0.0
        if fiyat_str:
            try:
                # Bazen fiyat "1375000" bazen de null gelebilir
                fiyat_float = float(fiyat_str)
            except ValueError:
                pass

        # 3. İlan Tipini Enum formatına çevir
        tip_str = str(ai_verisi.get("ilan_tipi")).upper()
        secilen_tip = IlanTipi.VASITA if tip_str == "VASITA" else IlanTipi.EMLAK

        # 4. Veritabanı objesini oluştur
        yeni_ilan = IlanORM(
            baslik=ai_verisi.get("baslik", "Başlık Bulunamadı"),
            fiyat=fiyat_float,
            link=url,
            ilan_tipi=secilen_tip,
            orijinal_metin=ham_metin,  # Belki ileride AI'ı tekrar eğitmek için saklıyoruz
            detaylar=ai_verisi.get("detaylar", {})
        )

        # 5. Veritabanına yaz ve onayla
        db.add(yeni_ilan)
        db.commit()
        db.refresh(yeni_ilan) # Oluşan ID'yi geri almak için sayfayı yeniliyoruz
        
        return {"kayit_durumu": "Başarılı", "ilan_id": yeni_ilan.id}

    except Exception as e:
        db.rollback() # Bir hata olursa yarım kalan işlemi iptal et (Geri al)
        return {"kayit_durumu": "Hata", "mesaj": str(e)}
    

def ilanlari_getir(db: Session, ilan_tipi: str = None, max_fiyat: float = None, limit: int = 50):
    """
    Veritabanındaki ilanları filtreleyerek getirir.
    """
    # Önce tüm ilanları getirecek temel sorguyu hazırlıyoruz
    sorgu = db.query(IlanORM)
    
    # Eğer kullanıcı sadece "VASITA" veya "EMLAK" istediyse filtrele
    if ilan_tipi:
        secilen_tip = IlanTipi.VASITA if ilan_tipi.upper() == "VASITA" else IlanTipi.EMLAK
        sorgu = sorgu.filter(IlanORM.ilan_tipi == secilen_tip)
        
    # Eğer kullanıcı bir maksimum fiyat belirttiyse filtrele
    if max_fiyat:
        sorgu = sorgu.filter(IlanORM.fiyat <= max_fiyat)
        
    # Sonuçları en yeniler en üstte olacak şekilde getir (id'ye göre tersten sırala)
    return sorgu.order_by(IlanORM.id.desc()).limit(limit).all()