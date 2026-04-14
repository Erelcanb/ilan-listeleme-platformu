import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# .env dosyasındaki gizli değişkenleri yüklüyoruz
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy Motorunu (Engine) oluşturuyoruz
engine = create_engine(DATABASE_URL)

# Veritabanı ile konuşmamızı sağlayacak oturum (Session) sınıfı
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tablo sınıflarımızın miras alacağı temel sınıf
Base = declarative_base()

# Veritabanı bağlantısı almak için kullanacağımız bağımlılık (Dependency) fonksiyonu
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()