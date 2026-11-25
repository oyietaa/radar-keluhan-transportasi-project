import json
from datetime import datetime, timedelta, timezone
import pandas as pd
from config import CLEAN_CSV, RINGKASAN

SINGKAT = "Ulasan singkat"

def buat_ringkasan(df, jumlah_baru=0):
    pct = (df["sentimen"].value_counts(normalize=True) * 100).round(1).to_dict()
    tema = df.loc[df["tema"] != SINGKAT, "tema"].value_counts()
    return {
        "diperbarui": datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None).isoformat(timespec="minutes"),
        "total_ulasan": int(len(df)),
        "ulasan_baru": int(jumlah_baru),
        "persen_sentimen": {k: pct.get(k, 0.0)
                            for k in ("positif", "netral", "negatif")},
        "rata_rata_rating": round(float(df["score"].mean()), 2),
        "tema_terbanyak": str(tema.index[0]) if len(tema) else "-",
        "jumlah_per_tema": {str(k): int(v) for k, v in tema.items()},
        "ulasan_singkat": int((df["tema"] == SINGKAT).sum()),
    }

def pesan_ringkas(r):
    return (f"Access by KAI: {r['ulasan_baru']} ulasan baru. "
            f"Negatif {r['persen_sentimen']['negatif']}%. "
            f"Tema terbanyak: {r['tema_terbanyak']}.")

if __name__ == "__main__":
    d = pd.read_csv(CLEAN_CSV, parse_dates=["at"])
    r = buat_ringkasan(d)
    RINGKASAN.write_text(json.dumps(r, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    print(json.dumps(r, ensure_ascii=False, indent=2))