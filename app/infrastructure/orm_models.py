from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.infrastructure.database import Base
from app.domain.models import IlanTipi

class IlanORM(Base):
    __tablename__ = "ilanlar"

    id = Column(Integer, primary_key=True, index=True)
    baslik = Column(String, nullable=False)
    fiyat = Column(Float, nullable=False)
    link = Column(String, nullable=False, unique=True) # Aynı ilanı iki kez çekmemek için unique=True
    ilan_tipi = Column(SQLEnum(IlanTipi), nullable=False)
    
    orijinal_metin = Column(String, nullable=False)
    ai_ozeti = Column(String, nullable=True)
    
    # İşte PostgreSQL'in gücü: JSONB! Emlak ve Vasıta detayları burada esnekçe tutulacak.
    detaylar = Column(JSONB, default=dict)
    
    olusturulma_tarihi = Column(DateTime(timezone=True), server_default=func.now())