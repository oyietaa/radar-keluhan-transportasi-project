import re
import pandas as pd

NORMALISASI = {
    "gak": "tidak", "ga": "tidak", "nggak": "tidak", "enggak": "tidak",
    "tdk": "tidak", "gk": "tidak", "bgt": "banget", "udh": "sudah",
    "udah": "sudah", "sdh": "sudah", "blm": "belum", "yg": "yang",
    "dgn": "dengan", "utk": "untuk", "krn": "karena", "tp": "tapi",
    "jg": "juga", "gmn": "bagaimana", "gimana": "bagaimana",
    "g": "tidak", "lg": "lagi", "dg": "dengan", "ttp": "tetap",
    "sampe": "sampai", "tpi": "tapi", "pake": "pakai", "emg": "memang",
    "bs": "bisa", "sy": "saya",
}
STOPWORDS = {"yang", "di", "ke", "dari", "dan", "atau", "itu", "ini",
             "untuk", "dengan", "adalah", "pada", "juga", "ada"}

def bersihkan_teks(teks):
    teks = str(teks).lower()
    teks = re.sub(r"http\S+|www\.\S+", " ", teks)
    teks = re.sub(r"[^a-z\s]", " ", teks)
    teks = re.sub(r"(.)\1{2,}", r"\1", teks)
    hasil = []
    for kata in teks.split():
        kata = NORMALISASI.get(kata, kata)
        if kata not in STOPWORDS:
            hasil.append(kata)
    return " ".join(hasil)

def bersihkan_df(df):
    df = df.dropna(subset=["content"]).copy()
    df["teks_asli"] = df["content"].astype(str)
    df["teks_bersih"] = df["teks_asli"].map(bersihkan_teks)
    df = df[df["teks_bersih"].str.split().str.len() >= 2]
    df = df.drop_duplicates(subset="reviewId")
    df = df.drop_duplicates(subset="teks_bersih")
    df["at"] = pd.to_datetime(df["at"])
    df["thumbsUpCount"] = pd.to_numeric(df["thumbsUpCount"], errors="coerce")
    df = df.dropna(subset=["thumbsUpCount", "score"])
    return df.drop(columns=["content"]).reset_index(drop=True)