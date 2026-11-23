import json
import pandas as pd
import streamlit as st
from config import BASE, MODEL_DIR
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

st.subheader("Kinerja model per kelas (data uji 598 ulasan)")
st.dataframe(pd.DataFrame(
    {"precision": [0.76, 0.14, 0.95], "recall": [0.83, 0.17, 0.88],
     "f1": [0.79, 0.15, 0.91], "jumlah uji": [225, 36, 337]},
    index=["negatif", "netral", "positif"]))
st.caption("Hasil pelatihan awal. Kelas netral jauh lebih lemah karena jumlahnya "
           "sedikit dan rating 3 sering berisi campuran pujian dan keluhan, "
           "sehingga akurasi keseluruhan tidak menggambarkan kelas ini.")

st.subheader("Akurasi menurut panjang ulasan (data uji)")
try:
    pjg = pd.read_csv(MODEL_DIR / "evaluasi_panjang.csv", index_col=0)
    st.dataframe(pjg)
    grafik = pjg["akurasi"].copy()
    grafik.index = [f"{i}. {n}" for i, n in enumerate(grafik.index, 1)]
    st.bar_chart(grafik)
    st.caption("Ulasan 1-2 kata paling mudah ditebak (kata penilaiannya jelas). "
               "Akurasi keseluruhan sebagian ditopang kelompok ini.")
except FileNotFoundError:
    st.info("Berkas evaluasi_panjang.csv belum ada. Jalankan cek_panjang.py.")

st.subheader("Evaluasi terbatas: 20 ulasan dinilai manual")
try:
    ev = pd.read_csv(BASE / "evaluasi_sentimen.csv")
except FileNotFoundError:
    st.info("Berkas evaluasi_sentimen.csv belum ada.")
else:
    n = len(ev)
    a, b, c = st.columns(3)
    a.metric("Manual vs rating", f"{(ev.label_manual == ev.sentimen_rating).sum()}/{n}")
    b.metric("Manual vs model", f"{(ev.label_manual == ev.prediksi).sum()}/{n}")
    c.metric("Rating vs model", f"{(ev.sentimen_rating == ev.prediksi).sum()}/{n}")
    st.caption("Label diberikan sebelum melihat rating dan prediksi; penilai memilih "
               "netral bila ragu. Sampel kecil, sehingga tidak menggambarkan seluruh data.")
    beda = ev[ev.label_manual != ev.prediksi]
    st.write("Ketidaksesuaian antara label manual dan prediksi model:")
    st.dataframe(beda[["teks_asli", "label_manual", "sentimen_rating", "prediksi"]],
                 hide_index=True)