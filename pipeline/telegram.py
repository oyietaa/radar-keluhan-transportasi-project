import os
import requests

def kirim(teks):
    token = os.getenv("TELEGRAM_TOKEN")
    chat = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat:
        print("Telegram tidak dikonfigurasi. Pesan:", teks)
        return
    requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                  json={"chat_id": chat, "text": teks}, timeout=20)