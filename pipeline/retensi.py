from datetime import datetime, timedelta
import pandas as pd
from config import RAW_DIR, RETENSI_BULAN, RETENSI_MAKS

def terapkan_retensi(df):
    batas = pd.Timestamp.now() - pd.DateOffset(months=RETENSI_BULAN)
    df = df[df["at"] >= batas]
    return df.sort_values("at", ascending=False).head(RETENSI_MAKS)

def bersihkan_raw(hari=60):
    batas = datetime.now() - timedelta(days=hari)
    for f in RAW_DIR.glob("mentah_*.csv"):
        tgl = datetime.strptime(f.stem.split("_")[1], "%Y-%m-%d")
        if tgl < batas:
            f.unlink()