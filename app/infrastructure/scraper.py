import sys
import asyncio
from playwright.sync_api import sync_playwright
import time

# Windows üzerinde FastAPI ve Playwright'ın alt işlem (subprocess) açarken 
# çakışmasını (NotImplementedError) önleyen kritik uyumluluk ayarı:
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

def veri_cek_ve_parcala(url: str):
    """
    Gelişmiş Scraper Sistemi (Playwright tabanlı).
    Gerçek bir tarayıcı simülasyonu ile siteye girer, bot korumalarını aşar 
    ve sayfadaki temiz metni (HTML olmadan) çeker.
    """
    with sync_playwright() as p:
        # headless=False yaparak gerçek bir Chrome penceresi açıyoruz
        browser = p.chromium.launch(headless=False)
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        
        try:
            # İlan linkine git ve sayfanın iskeleti yüklenene kadar bekle
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
            
            # Sahibinden gibi sitelerde JavaScript'in verileri tam ekrana basması için 3 saniye bekle
            time.sleep(3) 
            
            # Tüm sayfadaki okunan temiz metni al
            ham_metin = page.inner_text("body")
            
            browser.close()
            return {"durum": "başarılı", "ham_metin": ham_metin}
            
        except Exception as e:
            browser.close()
            print(f"Scraper Hatası ({url}): {e}")
            return {"durum": "hata", "ham_metin": ""}