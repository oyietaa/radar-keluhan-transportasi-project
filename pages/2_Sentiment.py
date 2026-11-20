import json
import pandas as pd
import streamlit as st
from config import MODEL_DIR
from muat import muat_data

st.title("Sentimen")
df = muat_data()
metrik = json.loads((MODEL_DIR / "metrik.json").read_text(encoding="utf-8"))

urutan = ["positif", "netral", "negatif"]
hitung = df["sentimen"].value_counts().reindex(urutan).fillna(0).astype(int)
persen = (hitung / hitung.sum() * 100).round(1)

st.subheader("Distribusi sentimen (prediksi model)")
c1, c2 = st.columns([1, 2])
c1.dataframe(pd.DataFrame({"jumlah": hitung, "persen (%)": persen}))
c2.bar_chart(hitung)

st.metric("Akurasi model pada data uji", f"{metrik['sentimen_akurasi'] * 100:.1f}%")
st.caption("Label dilatih dari rating bintang (1-2 negatif, 3 netral, 4-5 positif). "
           "Kelas netral paling lemah dikenali model karena jumlahnya sedikit.")

st.subheader("Perbandingan dengan label dari rating")
st.write("Baris = label dari rating, kolom = prediksi model")
st.dataframe(pd.crosstab(df["sentimen_rating"], df["sentimen"]))
sama = (df["sentimen_rating"] == df["sentimen"]).mean() * 100
st.caption(f"Kesesuaian: {sama:.1f}% (dihitung pada seluruh data, sebagian "
           "dipakai melatih, jadi tampak lebih baik daripada akurasi data uji).")

st.subheader("Tabel ulasan")
pilih = st.multiselect("Filter sentimen", urutan, default=["negatif"])
tampil = df[df["sentimen"].isin(pilih)]
st.dataframe(tampil[["at", "score", "sentimen", "teks_asli"]].head(200))