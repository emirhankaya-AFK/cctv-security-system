import requests
import os

class TelegramNotifier:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.enabled = True
        
        # Check if placeholders are still present
        if not token or "YOUR_TELEGRAM" in token or not chat_id or "YOUR_TELEGRAM" in str(chat_id):
            print("[WARN] Telegram Bot Token veya Chat ID varsayılan değerlerde bırakılmış. Telegram bildirimleri devre dışı kalacak.")
            self.enabled = False

    def send_message(self, message):
        if not self.enabled:
            print(f"[LOCAL ALARM] {message}")
            return False
            
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                return True
            else:
                print(f"[ERROR] Telegram mesajı gönderilemedi. Hata Kodu: {response.status_code}, Yanıt: {response.text}")
                return False
        except Exception as e:
            print(f"[ERROR] Telegram bağlantı hatası: {e}")
            return False

    def send_photo(self, photo_path, caption=None):
        if not self.enabled:
            print(f"[LOCAL ALARM] Fotoğraf gönderilemedi (Telegram devre dışı): {photo_path} - Başlık: {caption}")
            return False
            
        if not os.path.exists(photo_path):
            print(f"[ERROR] Gönderilecek fotoğraf bulunamadı: {photo_path}")
            return False
            
        url = f"https://api.telegram.org/bot{self.token}/sendPhoto"
        try:
            with open(photo_path, 'rb') as photo:
                files = {'photo': photo}
                data = {'chat_id': self.chat_id}
                if caption:
                    data['caption'] = caption
                    
                response = requests.post(url, data=data, files=files, timeout=15)
                if response.status_code == 200:
                    return True
                else:
                    print(f"[ERROR] Telegram fotoğrafı gönderilemedi. Hata Kodu: {response.status_code}, Yanıt: {response.text}")
                    return False
        except Exception as e:
            print(f"[ERROR] Telegram fotoğraf gönderme hatası: {e}")
            return False
