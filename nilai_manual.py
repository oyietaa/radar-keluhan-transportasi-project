import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from config import MODEL_DIR

NAMA = {"1": "positif", "2": "netral", "3": "negatif"}

def label(skor):
    return "negatif" if skor <= 2 else ("netral" if skor == 3 else "positif")

df = pd.read_csv("data/data_latih_awal.csv").dropna(subset=["teks_bersih"])
df["sentimen_rating"] = df["score"].map(label)
_, uji = train_test_split(df, test_size=0.2, random_state=42,
                          stratify=df["sentimen_rating"])
s = uji.sample(20, random_state=7).reset_index(drop=True)

print("Nilai sentimen tiap ulasan: 1 = positif, 2 = netral, 3 = negatif")
print("Nilai dengan pembacaanmu sendiri. Rating dan prediksi sengaja disembunyikan.\n")
manual = []
for i, teks in enumerate(s["teks_asli"], 1):
    print(f"[{i}/20] {teks}\n")
    while True:
        j = input("Sentimen (1/2/3): ").strip()
        if j in NAMA:
            manual.append(NAMA[j])
            break
        print("Ketik 1, 2, atau 3.")
    print("-" * 60)

s["label_manual"] = manual
s["prediksi"] = joblib.load(MODEL_DIR / "sentimen.joblib").predict(s["teks_bersih"])
s[["reviewId", "teks_asli", "label_manual", "sentimen_rating", "prediksi"]].to_csv(
    "evaluasi_sentimen.csv", index=False)

def cocok(a, b):
    n = int((s[a] == s[b]).sum())
    return f"{n}/20 = {n / 20:.0%}"

print("\nHASIL")
print("Manual vs rating :", cocok("label_manual", "sentimen_rating"))
print("Manual vs model  :", cocok("label_manual", "prediksi"))
print("Rating vs model  :", cocok("sentimen_rating", "prediksi"))
print("\nKetidaksesuaian manual vs model:")
for _, r in s[s["label_manual"] != s["prediksi"]].iterrows():
    print(f'- manual={r["label_manual"]}, rating={r["sentimen_rating"]}, '
          f'model={r["prediksi"]} | {r["teks_asli"][:120]}')