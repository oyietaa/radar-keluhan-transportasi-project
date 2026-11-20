import pandas as pd
from google_play_scraper import reviews, Sort
from config import APP_ID, LANG, COUNTRY

KOLOM = ["reviewId", "content", "score", "thumbsUpCount", "at", "appVersion"]

def ambil(jumlah):
    hasil, _ = reviews(APP_ID, lang=LANG, country=COUNTRY,
                       sort=Sort.NEWEST, count=jumlah)
    if not hasil:
        raise RuntimeError("Tidak ada ulasan yang terambil. Cek koneksi atau scraper.")
    df = pd.DataFrame(hasil)
    for k in KOLOM:
        if k not in df.columns:
            df[k] = None
    return df[KOLOM]