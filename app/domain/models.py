from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum
from datetime import datetime

# İlan tiplerini kısıtlamak ve standartlaştırmak için Enum kullanıyoruz
class IlanTipi(str, Enum):
    EMLAK = "emlak"
    VASITA = "vasita"

# Temel İlan Sınıfımız (Entity)
class Ilan(BaseModel):
    id: Optional[int] = None  # Veritabanına kaydedilince otomatik dolacak
    baslik: str = Field(..., description="İlanın başlığı")
    fiyat: float = Field(..., description="İlanın fiyatı")
    link: str = Field(..., description="İlanın çekildiği orijinal URL")
    ilan_tipi: IlanTipi
    
    # AI entegrasyonu için alanlar
    orijinal_metin: str = Field(..., description="Web sitesinden çekilen ham ilan açıklaması")
    ai_ozeti: Optional[str] = None  # Gemini çalıştıktan sonra burası dolacak
    
    # PostgreSQL JSONB esnekliği için detaylar sözlüğü
    detaylar: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Emlak için oda sayısı, vasıta için kilometre gibi değişken veriler"
    )
    
    olusturulma_tarihi: datetime = Field(default_factory=datetime.now)