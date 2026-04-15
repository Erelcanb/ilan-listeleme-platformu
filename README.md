# 🚀 AI Destekli İlan Analiz ve Listeleme Platformu

Bu proje, emlak ve vasıta ilan platformlarındaki (Örn: Sahibinden, Arabam.com vb.) karmaşık ilan metinlerini web scraping yöntemiyle çeken, Google Gemini Yapay Zeka modeli ile anlamlı verilere dönüştüren ve veritabanında listeleyen modern bir backend sistemidir.

## 🏗 Mimari Yaklaşım

Proje, yazılım mühendisliği standartlarına uygun olarak **Clean Architecture (Temiz Mimari)** prensipleriyle geliştirilmiştir. Kod tabanı üç ana katmana ayrılmıştır:
* **Domain:** Temel iş kuralları ve veri tipleri (Enum vb.)
* **Application:** Yapay zeka entegrasyonu ve iş mantığı
* **Infrastructure:** Veritabanı bağlantıları (ORM), Dış servisler (Scraper) ve Repolar

## 🛠 Kullanılan Teknolojiler

* **Web Çerçevesi:** FastAPI (Asenkron ve yüksek performanslı)
* **Yapay Zeka:** Google Gemini 2.5 Flash
* **Veritabanı:** PostgreSQL & SQLAlchemy (JSONB desteği ile esnek veri tutma)
* **Web Scraping:** BeautifulSoup4 & Requests
* **Sunucu:** Uvicorn

## ⚙️ Kurulum ve Çalıştırma

Projenin yerel bilgisayarınızda çalışabilmesi için aşağıdaki adımları izleyin:

**1. Repoyu Klonlayın**
```bash
git clone <sizin-repo-linkiniz>
cd ilan-listeleme-platformu
```

**2. Sanal Ortam Oluşturun ve Aktif Edin**
```bash
python -m venv venv
# Windows için:
.\venv\Scripts\activate
# MacOS/Linux için:
source venv/bin/activate
```
**3. Gerekli Kütüphaneleri Yükleyin**
```bash
pip install -r requirements.txt
```
**4. Çevresel Değişkenleri Ayarlayın (.env)**
Projenin ana dizininde bir .env dosyası oluşturun ve yapay zeka API anahtarınızı ekleyin (Bu dosya .gitignore içinde olmalıdır):
```Kod snippet'i
GEMINI_API_KEY=sizin_google_gemini_api_anahtariniz
```

**5. Sunucuyu Başlatın**
```bash
python -m uvicorn app.main:app --reload
```

# 🌐 API Uç Noktaları (Endpoints)
Uygulama ayağa kalktığında http://localhost:8000/docs adresinden Swagger UI paneline erişebilir ve aşağıdaki işlemleri test edebilirsiniz:

* *GET / :* Sistem sağlık kontrolü.
* *GET /analiz-et/?url={ilan_linki} :* Verilen linkteki ilanı çeker, Gemini AI ile analiz eder (Fiyat, Başlık, Detaylar) ve PostgreSQL veritabanına kaydeder.
* *GET /ilanlar/ :* Veritabanına kaydedilmiş ilanları listeler. ilan_tipi (EMLAK/VASITA) ve max_fiyat parametreleriyle gelişmiş filtreleme yapılabilir.

# 🎯 Gelecek Hedefleri
* [ ] Frontend (Arayüz) entegrasyonunun yapılması.
* [ ] Düzenli aralıklarla belirli linkleri kontrol eden Celery/Redis tabanlı arka plan görevleri (Background tasks).
* [ ] AI modelinin çıkarım yeteneğini artırmak için "Oda Sayısı", "Kilometre" gibi detayların spesifik kolonlara ayrılması.