import pandas as pd
import json
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from config import CLEAN_CSV
from config import MODEL_DIR

df = pd.read_csv(CLEAN_CSV)
df["jumlah_kata"] = df["teks_asli"].str.split().str.len()
Xa, Xb, ya, yb = train_test_split(
    df[["jumlah_kata", "score"]], df["thumbsUpCount"],
    test_size=0.2, random_state=42)
reg = LinearRegression().fit(Xa, ya)

print("MAE model                :", round(mean_absolute_error(yb, reg.predict(Xb)), 3))
print("MAE selalu tebak 0       :", round(mean_absolute_error(yb, [0] * len(yb)), 3))
print("MAE tebak rata-rata latih:", round(mean_absolute_error(yb, [ya.mean()] * len(yb)), 3))
print("Terbesar di data uji     :", yb.max(), "| rata-rata uji:", round(yb.mean(), 3))
print()
print(df["thumbsUpCount"].describe())
print(df["thumbsUpCount"].value_counts().head(6))

p = MODEL_DIR / "metrik.json"
m = json.loads(p.read_text(encoding="utf-8"))
m["mae_tebak_nol"] = round(mean_absolute_error(yb, [0] * len(yb)), 3)
m["mae_tebak_rata2"] = round(mean_absolute_error(yb, [ya.mean()] * len(yb)), 3)
m["persen_membantu_nol"] = round(float((df["thumbsUpCount"] == 0).mean() * 100), 1)
p.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
print("metrik.json diperbarui")