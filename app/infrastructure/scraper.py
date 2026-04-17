import sys
import asyncio
from playwright.sync_api import sync_playwright
import time
import os

# Windows uyumluluk yaması
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

def veri_cek_ve_parcala(url: str):
    with sync_playwright() as p:
        # Botun hafızasını (çerezlerini) kaydedeceği bir klasör yolu belirliyoruz
        hafiza_klasoru = os.path.join(os.getcwd(), "tarayici_hafizasi")
        
        # Tarayıcıyı tam hayalet (stealth) modda başlatıyoruz
        context = p.chromium.launch_persistent_context(
            user_data_dir=hafiza_klasoru,
            headless=False,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],  # KRİTİK YAMA: Playwright'ın varsayılan bot sinyalini susturur
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        
        page = context.pages[0]
        
        # Ekstra Güvenlik Katmanı: JavaScript ile sisteme "Ben bot değilim" diyoruz
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Hafızalı mod kendi sayfasını otomatik açar, o yüzden ilk sekmeyi alıyoruz
        page = context.pages[0]
        
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
            
            # Güvenlik duvarını geçip asıl ilanın yüklenmesi için süreyi uzattık
            print("⏳ Cloudflare engellerini aşman için 30 saniye bekleniyor...")
            time.sleep(30)
            
            ham_metin = page.inner_text("body")
            
            context.close()
            return {"durum": "başarılı", "ham_metin": ham_metin}
            
        except Exception as e:
            context.close()
            print(f"Scraper Hatası ({url}): {e}")
            return {"durum": "hata", "ham_metin": ""}