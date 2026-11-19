import json
import joblib
import pandas as pd
from config import CLEAN_CSV, MODEL_DIR

MIN_KATA_CLUSTER = 4

def label(skor):
    return "negatif" if skor <= 2 else ("netral" if skor == 3 else "positif")

def tambah_prediksi(df):
    sent = joblib.load(MODEL_DIR / "sentimen.joblib")
    vek, km = joblib.load(MODEL_DIR / "cluster.joblib")
    tema = json.loads((MODEL_DIR / "tema.json").read_text(encoding="utf-8"))
    df = df.copy()
    df["sentimen_rating"] = df["score"].map(label)
    df["sentimen"] = sent.predict(df["teks_bersih"])
    panjang = df["teks_bersih"].str.split().str.len()
    df["cluster"] = -1
    cukup = panjang >= MIN_KATA_CLUSTER
    if cukup.any():
        df.loc[cukup, "cluster"] = km.predict(
            vek.transform(df.loc[cukup, "teks_bersih"]))
    df["tema"] = df["cluster"].astype(str).map(tema)
    return df

if __name__ == "__main__":
    d = pd.read_csv(CLEAN_CSV, parse_dates=["at"])
    d = tambah_prediksi(d)
    d.to_csv(CLEAN_CSV, index=False)
    print(d["sentimen"].value_counts())
    print(d["tema"].value_counts())