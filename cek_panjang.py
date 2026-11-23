import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from config import MODEL_DIR

def label(skor):
    return "negatif" if skor <= 2 else ("netral" if skor == 3 else "positif")

df = pd.read_csv("data/data_latih_awal.csv").dropna(subset=["teks_bersih"])
df["rating_label"] = df["score"].map(label)
_, uji = train_test_split(df, test_size=0.2, random_state=42,
                          stratify=df["rating_label"])
uji = uji.copy()
uji["prediksi"] = joblib.load(MODEL_DIR / "sentimen.joblib").predict(uji["teks_bersih"])
uji["kata"] = uji["teks_asli"].str.split().str.len()
uji["kelompok"] = pd.cut(uji["kata"], [0, 2, 5, 10, 1000],
                         labels=["1-2 kata", "3-5 kata", "6-10 kata", ">10 kata"])
uji["benar"] = uji["prediksi"] == uji["rating_label"]
hasil = uji.groupby("kelompok", observed=True).agg(
    jumlah=("benar", "size"),
    akurasi=("benar", "mean"),
    netral_prediksi=("prediksi", lambda s: (s == "netral").mean()),
    netral_rating=("rating_label", lambda s: (s == "netral").mean()))
print(hasil.round(3))