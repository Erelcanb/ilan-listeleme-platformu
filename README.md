# 🚀 AI Destekli Otonom İlan Analiz Platformu

Bu proje; çeşitli gayrimenkul ve vasıta ilan platformlarındaki (Örn: Sahibinden, Arabam.com vb.) karmaşık ilan verilerini otonom olarak çeken, güvenlik duvarlarını aşan ve Google Gemini Yapay Zeka modeli ile analiz ederek yapılandırılmış veri halinde PostgreSQL veritabanına kaydeden Full-Stack bir web mimarisidir.

## 🌟 Öne Çıkan Özellikler

- **Gelişmiş Web Scraper (Anti-Bot Bypass):** Playwright altyapısı sayesinde Cloudflare gibi güvenlik duvarlarına takılmadan, gerçek tarayıcı simülasyonu ile veri çekimi.
- **Yapay Zeka Entegrasyonu:** Çekilen karmaşık (unstructured) HTML/Metin verilerinin Google Gemini API kullanılarak anlamlı JSON verilerine (Başlık, Fiyat, İlan Tipi vb.) dönüştürülmesi.
- **Otonom Kuyruk Yönetimi (Queue System):** FastAPI `BackgroundTasks` kullanılarak, sisteme verilen toplu ilan linklerinin API hız limitlerine (Rate Limit) takılmadan arka planda sırayla ve otonom işlenmesi.
- **Tam Teşekküllü CRUD API:** İlan oluşturma, listeleme, silme ve fiyat güncelleme (PATCH) yetenekleri.
- **Antivirüs & OS Uyumlu Veritabanı:** psycopg2'nin DLL engellerini aşmak için %100 Python tabanlı `pg8000` sürücüsü ve Windows `asyncio` event loop çakışmalarını önleyen özel mimari.
- **Dinamik Görsel Arayüz (Frontend):** Bootstrap tabanlı, API ile asenkron (CORS destekli) konuşan şık web arayüzü.

## 🛠️ Kullanılan Teknolojiler

- **Backend:** Python, FastAPI, Pydantic
- **Veritabanı & ORM:** PostgreSQL, SQLAlchemy, pg8000
- **Veri Çekme (Scraping):** Playwright (Chromium Headless/Headed)
- **Yapay Zeka:** Google Generative AI (Gemini 2.5 Flash)
- **Frontend:** HTML5, JavaScript (Fetch API), Bootstrap 5

## ⚙️ Kurulum ve Çalıştırma

### 1. Gereksinimleri Yükleyin
Projeyi klonladıktan sonra sanal ortamınızı (venv) oluşturun ve gerekli kütüphaneleri indirin:
```bash
pip install fastapi uvicorn sqlalchemy pg8000 pydantic python-dotenv google-generativeai playwright
```
### 2. Tarayıcı Motorunu Kurun
Playwright'ın arka planda otonom çalışabilmesi için gerekli tarayıcıyı indirin:
```bash
playwright install chromium
```
### 3. Çevresel Değişkenleri (.env) Ayarlayın
Proje ana dizininde bir .env dosyası oluşturun ve bilgilerinizi girin:
```Kod snippet'i
DATABASE_URL=postgresql+pg8000://kullanici_adi:sifre@localhost:5432/veritabani_adi
GEMINI_API_KEY=sizin_google_gemini_api_anahtariniz
```
### 4. Sunucuyu Başlatın
Motoru ateşlemek için aşağıdaki komutu çalıştırın:
```bash
python -m uvicorn app.main:app --reload
```
### 5. Arayüzü Görüntüleyin
Sunucu çalıştıktan sonra frontend/index.html dosyasını herhangi bir tarayıcıda açarak ilanlarınızı görselleştirebilir veya http://localhost:8000/docs adresinden Swagger API arayüzüne ulaşabilirsiniz.

---

## 📅 Geliştirme Günlüğü (Changelog)

### [17.04.2026]
- **Fix (Veritabanı):** Yapay zekadan gelen metin tabanlı fiyatları (örn: "1.180.000 TL") veritabanına kaydederken yaşanan tip uyuşmazlığını (Type Error) çözmek için `repository.py` içerisine "Veri Temizleme (Sanitization)" filtresi eklendi.
- **Feat (Scraper):** Gelişmiş bot korumalarını (Cloudflare vb.) kalıcı olarak aşmak için Playwright modülü "Persistent Context" (Hafızalı Tarayıcı) mimarisine geçirildi.

### [16.04.2026]
- **Feat (Kuyruk):** FastAPI BackgroundTasks ile API limitlerine takılmayan otonom kuyruk (queue) mimarisi kuruldu.
- **UI (Arayüz):** Bootstrap tabanlı görsel arayüz (frontend) asenkron çalışacak ve CORS destekleyecek şekilde sisteme entegre edildi.