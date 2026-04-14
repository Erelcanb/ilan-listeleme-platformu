import requests
from bs4 import BeautifulSoup
import urllib3

# SSL uyarılarını terminalde görmemek için kapatıyoruz
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def veri_cek_ve_parcala(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "tr-TR,tr;q=0.9",
        "Referer": "https://www.google.com/"
    }
    
    try:
        # SSL sertifika kontrolünü es geçiyoruz
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status() 
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Sayfadaki tüm metni (scripts ve style etiketleri hariç) temiz bir şekilde alıyoruz
        # Bu kısım Gemini'ye temiz veri gitmesi için çok önemli
        for script in soup(["script", "style"]):
            script.decompose()

        tum_metin = soup.get_text(separator=' ', strip=True)
        
        return {
            "durum": "başarılı", 
            "url": url,
            "ham_metin": tum_metin
        }
        
    except Exception as e:
        return {"durum": "hata", "mesaj": f"Veri çekilirken hata oluştu: {str(e)}"}