from datetime import datetime, timedelta
import pandas as pd
from config import RAW_DIR, RETENSI_BULAN, RETENSI_MAKS

ARSIP_TETAP = {"mentah_2026-11-19.csv"}  # pengambilan awal 3.000 ulasan, tidak ikut dihapus

def terapkan_retensi(df):
    batas = pd.Timestamp.now() - pd.DateOffset(months=RETENSI_BULAN)
    df = df[df["at"] >= batas]
    return df.sort_values("at", ascending=False).head(RETENSI_MAKS)

def bersihkan_raw(hari=60):
    batas = datetime.now() - timedelta(days=hari)
    for f in RAW_DIR.glob("mentah_*.csv"):
        if f.name in ARSIP_TETAP:
            continue
        tgl = datetime.strptime(f.stem.split("_")[1], "%Y-%m-%d")
        if tgl < batas:
            f.unlink()