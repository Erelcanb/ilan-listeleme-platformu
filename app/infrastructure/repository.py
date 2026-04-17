from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.infrastructure.orm_models import IlanORM
from app.domain.models import IlanTipi

def ilan_kaydet(db: Session, url: str, ai_verisi: dict, ham_metin: str = ""):
    """
    Yapay zekadan gelen analiz verilerini temizleyip veritabanına kaydeder.
    """
    guvenli_baslik = ai_verisi.get("baslik") or "Başlık Bulunamadı"
    
    # --- YENİ VERİ TEMİZLEME KATMANI ---
    # Gelen fiyatı (Örn: "1.180.000 TL" veya "150.000") saf sayıya çeviriyoruz
    ham_fiyat = str(ai_verisi.get("fiyat", "0"))
    # Önce "TL" yazılarını ve boşlukları at, sonra binlik ayırıcı noktaları sil
    temiz_fiyat = ham_fiyat.upper().replace("TL", "").replace(" ", "").replace(".", "")
    # Varsa kuruş virgülünü noktaya çevir (Python float formatı için)
    temiz_fiyat = temiz_fiyat.replace(",", ".")
    
    try:
        guvenli_fiyat = float(temiz_fiyat)
    except ValueError:
        guvenli_fiyat = 0.0  # Çevirme başarısız olursa çökmesini engelle
    # -----------------------------------

    yeni_ilan = IlanORM(
        baslik=guvenli_baslik,
        fiyat=guvenli_fiyat,
        link=url,
        ilan_tipi=ai_verisi.get("ilan_tipi", "Bilinmiyor"),
        orijinal_metin=ham_metin,
        detaylar=ai_verisi.get("detaylar", {})
    )
    
    try:
        db.add(yeni_ilan)
        db.commit()
        db.refresh(yeni_ilan)
        return yeni_ilan
    except Exception as e:
        db.rollback()
        print(f"Veritabanı Kayıt Hatası: {e}")
        return None
    

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

def ilan_sil(db: Session, ilan_id: int):
    """
    Verilen ID'ye sahip ilanı veritabanından siler.
    """
    # 1. Önce silinecek ilanı veritabanında bul
    silinecek_ilan = db.query(IlanORM).filter(IlanORM.id == ilan_id).first()
    
    # 2. Eğer böyle bir ilan yoksa False döndür
    if not silinecek_ilan:
        return False
        
    # 3. İlan bulunduysa sil ve işlemi onayla
    try:
        db.delete(silinecek_ilan)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False
    
def ilan_fiyat_guncelle(db: Session, ilan_id: int, yeni_fiyat: float):
    """
    Verilen ID'ye sahip ilanın fiyatını günceller.
    """
    # 1. Önce güncellenecek ilanı bul
    guncellenecek_ilan = db.query(IlanORM).filter(IlanORM.id == ilan_id).first()
    
    # 2. Eğer ilan yoksa None döndür
    if not guncellenecek_ilan:
        return None
        
    # 3. İlan bulunduysa fiyatını değiştir ve veritabanına kaydet
    try:
        guncellenecek_ilan.fiyat = yeni_fiyat
        db.commit()
        db.refresh(guncellenecek_ilan)
        return guncellenecek_ilan
    except Exception as e:
        db.rollback()
        return None