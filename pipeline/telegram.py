import os
import re
import requests

def kirim(teks, pakai_html=False):
    token = os.getenv("TELEGRAM_TOKEN")
    chat = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat:
        print("Telegram tidak dikonfigurasi. Pesan:", teks)
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat, "text": teks, "disable_web_page_preview": True}
    if pakai_html:
        data["parse_mode"] = "HTML"
    res = requests.post(url, json=data, timeout=20)
    if not res.ok and pakai_html:
        polos = re.sub(r"<[^>]+>", "", teks)
        polos = polos.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
        res = requests.post(url, json={"chat_id": chat, "text": polos,
                                       "disable_web_page_preview": True}, timeout=20)
    if not res.ok:
        print("Telegram menolak pesan:", res.status_code)