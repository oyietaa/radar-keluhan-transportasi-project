import importlib.metadata as md
import json
from pathlib import Path

import joblib
import pandas as pd

from config import CLEAN_CSV, MODEL_DIR, RAW_DIR, RINGKASAN, LOG

def ok(b):
    return "OK   " if b else "CEK  "

df = pd.read_csv(CLEAN_CSV, parse_dates=["at"])
wajib = ["reviewId", "teks_asli", "teks_bersih", "score", "thumbsUpCount",
         "at", "sentimen_rating", "sentimen", "cluster", "tema"]
ada = [k for k in wajib if k in df.columns]

print("== STRUKTUR DATA ==")
print(ok(len(ada) == len(wajib)), "kolom wajib hilang:", [k for k in wajib if k not in ada] or "tidak ada")
print(ok(df["reviewId"].is_unique), "duplikat reviewId:", int(df["reviewId"].duplicated().sum()))
kosong = df[ada].isna().sum()
print(ok(kosong.sum() == 0), "sel kosong:", kosong[kosong > 0].to_dict() or 0)
print(ok(df["score"].between(1, 5).all()), "rating 1-5")
print(ok((df["thumbsUpCount"] >= 0).all()), "membantu tidak negatif")
print(ok((df["teks_bersih"].str.split().str.len() >= 1).all()), "tidak ada teks bersih kosong")
print("baris:", len(df), "| rentang:", df["at"].min(), "->", df["at"].max())
cek = df["score"].map(lambda s: "negatif" if s <= 2 else ("netral" if s == 3 else "positif"))
print(ok((cek == df["sentimen_rating"]).all()), "sentimen_rating sesuai rating")

print("\n== DATA PRIBADI DI TEKS ASLI (hanya jumlah, jangan salin isinya) ==")
pola = {"email": r"[\w\.-]+@[\w\.-]+\.\w+",
        "telepon": r"(?:\+62|62|0)8\d{8,11}",
        "angka 8+ digit": r"\d{8,}"}
for nama, p in pola.items():
    n = int(df["teks_asli"].str.contains(p, regex=True, na=False).sum())
    print(ok(n == 0), nama, ":", n, "ulasan")

print("\n== MODEL DAN TEMA ==")
for n in ["sentimen.joblib", "cluster.joblib", "regresi.joblib", "cluster_info.json",
          "metrik.json", "tema.json", "uji_regresi.csv"]:
    print(ok((MODEL_DIR / n).exists()), n)
tema = json.loads((MODEL_DIR / "tema.json").read_text(encoding="utf-8"))
print(ok(set(df["tema"].unique()) <= set(tema.values())), "semua tema terdaftar di tema.json")
print(df["tema"].value_counts().to_string())
print(df["sentimen"].value_counts().to_string())

sent = joblib.load(MODEL_DIR / "sentimen.joblib")
s = df.sample(200, random_state=0)
print(ok((sent.predict(s["teks_bersih"]) == s["sentimen"]).all()),
      "sentimen tersimpan = hasil model tersimpan")
vek, km = joblib.load(MODEL_DIR / "cluster.joblib")
c = df[df["cluster"] >= 0].sample(200, random_state=0)
print(ok((km.predict(vek.transform(c["teks_bersih"])) == c["cluster"]).all()),
      "cluster tersimpan = hasil model tersimpan")
X = vek.transform(df.loc[df["cluster"] >= 0, "teks_bersih"])
print("ulasan >=4 kata bervektor nol:", int((X.getnnz(axis=1) == 0).sum()))

print("\n== RINGKASAN, LOG, BERKAS ==")
r = json.loads(RINGKASAN.read_text(encoding="utf-8"))
print(ok(r["total_ulasan"] == len(df)), "ringkasan:", r["total_ulasan"], "| data:", len(df))
log = json.loads(LOG.read_text(encoding="utf-8"))
print(len(log), "entri log; terakhir:", log[-1]["status"], log[-1]["waktu"])
print("berkas mentah:", len(list(RAW_DIR.glob("mentah_*.csv"))),
      "| ukuran CSV bersih (KB):", round(CLEAN_CSV.stat().st_size / 1024))

print("\n== VERSI PUSTAKA VS requirements-pipeline.txt ==")
for baris in Path("requirements-pipeline.txt").read_text().split():
    nama, _, ver = baris.partition("==")
    try:
        terpasang = md.version(nama)
    except md.PackageNotFoundError:
        terpasang = "TIDAK TERPASANG"
    print(ok(terpasang == ver), nama, ver, "| terpasang:", terpasang)