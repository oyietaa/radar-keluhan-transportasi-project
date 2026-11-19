import argparse
import datetime
from config import RAW_DIR, CLEAN_CSV
from pipeline.ambil import ambil
from pipeline.bersihkan import bersihkan_df

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--jumlah", type=int, default=3000)
    a = p.parse_args()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    CLEAN_CSV.parent.mkdir(parents=True, exist_ok=True)
    mentah = ambil(a.jumlah)
    mentah.to_csv(RAW_DIR / f"mentah_{datetime.date.today()}.csv", index=False)
    bersih = bersihkan_df(mentah)
    bersih.to_csv(CLEAN_CSV, index=False)
    print(len(mentah), "mentah ->", len(bersih), "bersih")

if __name__ == "__main__":
    main()