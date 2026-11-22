import json
import joblib
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import classification_report, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from config import CLEAN_CSV, MODEL_DIR
import sys
if "--yakin" not in sys.argv:
    sys.exit("Menjalankan ulang akan mengganti model dan nomor cluster, sehingga "
             "models/tema.json harus dibuat ulang. Gunakan --yakin bila sengaja.")

def label(skor):
    return "negatif" if skor <= 2 else ("netral" if skor == 3 else "positif")

df = pd.read_csv("data/data_latih_awal.csv").dropna(subset=["teks_bersih"])
MODEL_DIR.mkdir(exist_ok=True)
metrik = {}

# 1. Sentimen (label dari rating)
df["sentimen"] = df["score"].map(label)
X_tr, X_te, y_tr, y_te = train_test_split(
    df["teks_bersih"], df["sentimen"], test_size=0.2,
    random_state=42, stratify=df["sentimen"])
sent = make_pipeline(
    TfidfVectorizer(max_features=5000, ngram_range=(1, 2)),
    LogisticRegression(max_iter=1000, class_weight="balanced"))
sent.fit(X_tr, y_tr)
print(classification_report(y_te, sent.predict(X_te)))
laporan = classification_report(y_te, sent.predict(X_te), output_dict=True)
metrik["sentimen_akurasi"] = round(laporan["accuracy"], 3)
joblib.dump(sent, MODEL_DIR / "sentimen.joblib")

# 2. Clustering (hanya ulasan >= 4 kata)
dk = df[df["teks_bersih"].str.split().str.len() >= 4].reset_index(drop=True)
K = 4
STOP_CLUSTER = ["kai", "kereta", "api", "aplikasi", "tiket", "nya", "saya",
                "mau", "sudah", "aja", "banget", "lagi", "sangat", "terus",
                "sering"]
vek = TfidfVectorizer(max_features=3000, stop_words=STOP_CLUSTER)
M = vek.fit_transform(dk["teks_bersih"])
km = KMeans(n_clusters=K, n_init=10, random_state=42).fit(M)
joblib.dump((vek, km), MODEL_DIR / "cluster.joblib")
istilah = vek.get_feature_names_out()
info = {}
for c in range(K):
    top = km.cluster_centers_[c].argsort()[::-1][:5]
    contoh = dk.loc[km.labels_ == c, "teks_asli"].head(3).tolist()
    info[str(c)] = {"kata": [str(istilah[i]) for i in top],
                    "jumlah": int((km.labels_ == c).sum()),
                    "contoh": contoh}
    print("\nCluster", c, "|", info[str(c)]["jumlah"], "ulasan")
    print("  kata dominan:", info[str(c)]["kata"])
    for k in contoh:
        print("  -", k[:120])
(MODEL_DIR / "cluster_info.json").write_text(
    json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")

# 3. Regresi: jumlah kata + rating -> jumlah "membantu"
df["jumlah_kata"] = df["teks_asli"].str.split().str.len()
Xa, Xb, ya, yb = train_test_split(
    df[["jumlah_kata", "score"]], df["thumbsUpCount"],
    test_size=0.2, random_state=42)
reg = LinearRegression().fit(Xa, ya)
pred = reg.predict(Xb)
metrik["regresi_mae"] = round(float(mean_absolute_error(yb, pred)), 3)
metrik["regresi_r2"] = round(float(r2_score(yb, pred)), 3)
print("\nMetrik:", metrik)
joblib.dump(reg, MODEL_DIR / "regresi.joblib")
(MODEL_DIR / "metrik.json").write_text(
    json.dumps(metrik, ensure_ascii=False, indent=2), encoding="utf-8")